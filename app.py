from flask import Flask, request, render_template, jsonify, send_from_directory
from Crypto.Cipher import AES, DES, Blowfish
from Crypto.Util.Padding import pad, unpad
import numpy as np
import cv2
import os
import struct

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALGO_MAP = {"AES": b'\x01', "DES": b'\x02', "Blowfish": b'\x03'}
ALGO_REVERSE = {1: "AES", 2: "DES", 3: "Blowfish"}

def get_cipher(algorithm, key):
    key_bytes = key.encode('utf-8')

    if algorithm == 'AES':
        if len(key_bytes) != 16:
            raise ValueError("AES için anahtar uzunluğu 16 byte olmalıdır.")
        return AES.new(key_bytes, AES.MODE_ECB), 16

    elif algorithm == 'DES':
        if len(key_bytes) != 8:
            raise ValueError("DES için anahtar uzunluğu 8 byte olmalıdır.")
        return DES.new(key_bytes, DES.MODE_ECB), 8

    elif algorithm == 'Blowfish':
        if not 4 <= len(key_bytes) <= 56:
            raise ValueError("Blowfish anahtarı 4 ile 56 byte arasında olmalıdır.")
        return Blowfish.new(key_bytes, Blowfish.MODE_ECB), 8

    else:
        raise ValueError("Geçersiz algoritma seçildi.")

def embed_data_in_image(image, data):
    flat = image.flatten()
    binary_data = ''.join(f'{byte:08b}' for byte in data)
    if len(binary_data) > len(flat):
        raise ValueError("Veri çok büyük.")
    for i in range(len(binary_data)):
        flat[i] = (flat[i] & ~1) | int(binary_data[i])
    return flat.reshape(image.shape)

def extract_data_from_image(image, length):
    flat = image.flatten()
    total_bits = length * 8
    if total_bits > len(flat):
        raise ValueError("Çıkarılmak istenen veri, resmin kapasitesini aşıyor.")
    bits = [str(flat[i] & 1) for i in range(total_bits)]
    bytes_out = [int(''.join(bits[i:i+8]), 2) for i in range(0, len(bits), 8)]
    return bytes(bytes_out)

def auto_resize(secret_img, main_shape, block_size):
    max_capacity = main_shape[0] * main_shape[1] * main_shape[2] // 8 - 9
    h, w = secret_img.shape[:2]
    while True:
        resized = cv2.resize(secret_img, (w, h))
        raw = resized.tobytes()
        padded = pad(raw, block_size)
        if len(padded) <= max_capacity:
            return resized
        h = int(h * 0.9)
        w = int(w * 0.9)
        if h < 10 or w < 10:
            raise ValueError("Gizli resim çok küçük hale geldi, sığdırılamıyor.")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/extract')
def extract_page():
    return render_template('extract.html')

@app.route('/upload', methods=['POST'])
def upload():
    try:
        main_file = request.files['main_image']
        secret_file = request.files['secret_image']
        algorithm = request.form['algorithm']
        key = request.form['user_key']

        main_path = os.path.join(UPLOAD_FOLDER, 'main.png')
        secret_path = os.path.join(UPLOAD_FOLDER, 'secret.png')
        main_file.save(main_path)
        secret_file.save(secret_path)

        main = cv2.imread(main_path)
        secret = cv2.imread(secret_path)

        cipher, block_size = get_cipher(algorithm, key)
        secret = auto_resize(secret, main.shape, block_size)

        h, w = secret.shape[:2]
        secret_bytes = secret.tobytes()
        encrypted = cipher.encrypt(pad(secret_bytes, block_size))

        algo_byte = ALGO_MAP[algorithm]
        data_length = struct.pack('>I', len(encrypted))
        size_bytes = struct.pack('>HH', h, w)

        final_data = algo_byte + data_length + size_bytes + encrypted

        # Önizleme oluştur (ana resmin üzerine saydam gizli resim efekti)
        preview_image = main.copy()
        secret_resized = cv2.resize(secret, (main.shape[1], main.shape[0]))
        blended = cv2.addWeighted(preview_image, 1.0, secret_resized, 0.3, 0)

        preview_name = f'hidden_image2_{algorithm}.png'
        cv2.imwrite(os.path.join(UPLOAD_FOLDER, preview_name), blended)

        encoded = embed_data_in_image(main, final_data)
        file_name = f'hidden_image_{algorithm}.png'
        cv2.imwrite(os.path.join(UPLOAD_FOLDER, file_name), encoded)

        return jsonify({"success": True, "algorithm": algorithm})

    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@app.route('/extract', methods=['POST'])
def extract():
    try:
        file = request.files['image']
        key = request.form['password']
        filename = os.path.join(UPLOAD_FOLDER, 'extract_target.png')
        file.save(filename)

        image = cv2.imread(filename)
        header = extract_data_from_image(image, 9)
        algo_id = header[0]
        encrypted_length = struct.unpack('>I', header[1:5])[0]
        height, width = struct.unpack('>HH', header[5:9])

        full_data = extract_data_from_image(image, 9 + encrypted_length)
        encrypted_data = full_data[9:]

        if algo_id not in ALGO_REVERSE:
            return jsonify({"error": "Geçersiz algoritma kodu!"}), 400

        algorithm = ALGO_REVERSE[algo_id]
        cipher, block_size = get_cipher(algorithm, key)

        decrypted = unpad(cipher.decrypt(encrypted_data), block_size)
        secret = np.frombuffer(decrypted, dtype=np.uint8).reshape((height, width, 3))

        out_path = os.path.join(UPLOAD_FOLDER, 'extracted_image.png')
        cv2.imwrite(out_path, secret)
        return send_from_directory(UPLOAD_FOLDER, 'extracted_image.png', as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
