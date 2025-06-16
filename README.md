# 🔐 Görüntü Şifreleme ile Gizli Resim Gömme (Steganografi Projesi)

Bu proje, bir resmin içine başka bir resmi **şifreli** olarak gizleyen ve sadece doğru şifreyle çıkarılabilen bir sistem sunar. Görüntü işleme ve kriptografi tekniklerinin birleştirildiği bu uygulama, temel steganografi prensiplerini modern şifreleme algoritmalarıyla birleştirir.

---

## 🎯 Projenin Amacı

- Kullanıcının seçtiği bir **gizli resmi**, bir **ana resmin** içerisine gömmek
- Gizli resmi **AES**, **DES**, veya **Blowfish** algoritmalarından biriyle şifrelemek
- Sadece doğru şifreyle ve doğru algoritmayla gizli resmi yeniden ortaya çıkarmak

---

## 🧪 Kullanılan Teknolojiler

- **Python 3**
- **Flask** (Backend Web Framework)
- **OpenCV** (Görüntü işleme)
- **PyCryptodome** (AES, DES, Blowfish şifreleme)
- **HTML + Bootstrap** (Frontend arayüz)
- **LSB (Least Significant Bit)** steganografi yöntemi
- **PNG formatı** ile kayıpsız veri gömme

---

## 📦 Özellikler

- [x] Şifreli veri gömme (AES, DES, Blowfish)
- [x] PNG formatında kayıpsız veri saklama
- [x] Anahtar uzunluklarına göre şifre doğrulama
- [x] Gizli resim boyutunu otomatik küçültme
- [x] Gömme sırasında algoritma ve boyut bilgilerini veriye ekleme
- [x] Doğru şifreyle başarılı çıkarım
- [x] Yanlış şifreye karşı koruma
- [x] Kolay kullanılabilir web arayüzü

---

## 🚀 Kurulum

```bash
git clone https://github.com/ethemagcaa/FinalProjectsteganografi
cd gizli-resim-gomme

# Ortamı kur
pip install -r requirements.txt

# Uygulamayı başlat
python app.py
