# **Google AI Pro Student Verification Tool**

## 🎯 **Deskripsi**

**Google AI Pro Student Verifier** adalah alat otomatis yang membantu mahasiswa untuk memverifikasi status akademik mereka guna mendapatkan akses **Google AI Pro (Gemini Advanced)** secara gratis melalui program diskon mahasiswa SheerID. 

Tool ini mengotomatisasi proses verifikasi dengan:
- Membuat dokumen akademik palsu yang realistis
- Mengisi formulir verifikasi otomatis
- Mengunggah dokumen ke server SheerID
- Menggunakan algoritma pemilihan universitas berbobot

> **Catatan Penting:** Per Januari 2026, pendaftaran baru hanya tersedia untuk mahasiswa di **Amerika Serikat**. Mahasiswa dari negara lain mungkin masih bisa mengakses untuk pengguna yang sudah terdaftar.

## ✨ **Fitur Utama**

### ✅ **Keunggulan Tool**
1. **100% Otomatis** - Tidak perlu input manual berulang
2. **Multi-Platform** - Windows (32-bit & 64-bit), Linux, Android Termux
3. **Database Universitas Lengkap** - 50+ universitas dengan bobot keberhasilan
4. **Smart Selection** - Pemilihan universitas berbobot statistik
5. **Dokumen Realistis** - Generate transkrip & ID mahasiswa berkualitas
6. **Proxy Support** - Dukungan proxy dengan/s tanpa autentikasi
7. **Statistik Tracking** - Pelacakan tingkat keberhasilan per universitas

### 📊 **Statistik Keberhasilan**
- **Universitas AS**: 85-95% keberhasilan
- **Community Colleges**: 80-85% keberhasilan  
- **Negara Lain**: 15-40% keberhasilan (terbatas)

## 💻 **Persyaratan Sistem**

### **Windows**
- Windows 7/8/10/11 (32-bit atau 64-bit)
- Minimum 2GB RAM
- 100MB ruang disk tersedia

### **Linux/Termux**
- Python 3.8+
- pip package manager
- 1GB RAM

## 📥 **Instalasi**

### **Untuk Pengguna Windows**
1. Download folder sesuai arsitektur sistem Anda:
   - **Windows 64-bit**: `PyRuntime_64/`
   - **Windows 32-bit**: `PyRuntime_32/`

2. Ekstrak folder ke lokasi yang diinginkan
3. Jalankan `run_cmd.bat` (untuk Windows)
4. **Tidak perlu install Python atau modul tambahan!**

### **Untuk Linux/Android Termux**
```bash
# Clone repository
git clone https://github.com/MichaelJorky/Google-AI-Pro-Student-Verification-Tool.git google-ai-verifier
cd google-ai-verifier

# Install dependencies
pip install httpx cloudscraper pillow

# Jalankan script
python script.py
```

## 🚀 **Penggunaan**

### **Windows (GUI Batch)**
1. Buka folder `PyRuntime_64` atau `PyRuntime_32`
2. Klik ganda `run_cmd.bat`
3. Pilih mode operasi:

```
==========================================
      PILIH MODE MENJALANKAN SCRIPT
==========================================
1. Mode Interaktif
2. Dengan URL Langsung  
3. Dengan Proxy (Host:Port)
4. Dengan Proxy Auth (User:Pass@Host:Port)
5. Keluar
==========================================
Masukkan pilihan (1-5): 
```

### **Command Line (Semua Platform)**
```bash
# Mode interaktif
python script.py

# Dengan URL langsung
python script.py "https://services.sheerid.com/verify/67c8c14f5f17a83b745e3f82/..."

# Dengan proxy
python script.py --proxy "127.0.0.1:8080" "URL_VERIFIKASI"

# Dengan proxy autentikasi
python script.py --proxy "user:pass@host:port" "URL_VERIFIKASI"
```

### **Android Termux**
```bash
pkg update && pkg upgrade
pkg install python git
pip install httpx cloudscraper pillow
python script.py
```

## 📄 **Contoh Output**

### **Contoh 1: Verifikasi Berhasil**
```
============================================================
         Alat Verifikasi Google One (Gemini AI Pro)
                  Diskon Mahasiswa SheerID
============================================================

   Masukkan URL verifikasi: https://services.sheerid.com/verify/67c8c14f5f17a83b745e3f82/?verificationId=abc123...

   Memproses...

   Mahasiswa: Michael Johnson
   Email: mjohnson456@ucla.edu
   Sekolah: University of California, Los Angeles
   Tanggal Lahir: 2003-05-15
   ID: abc123def456ghi789jkl...
   Memulai langkah: collectStudentPersonalInfo

   Langkah 1/3: Membuat transkrip akademik...
     Ukuran: 45.2 KB

   Langkah 2/3: Mengirimkan informasi mahasiswa...
     Langkah saat ini: docUpload

   Langkah 3/4: Melewati SSO...

   Langkah 4/5: Mengunggah dokumen...
     Dokumen berhasil diunggah!

   Langkah 5/5: Menyelesaikan unggah...
     Unggah selesai: pending

----------------------------------------------------------
   BERHASIL!
   Mahasiswa: Michael Johnson
   Email: mjohnson456@ucla.edu
   Sekolah: University of California, Los Angeles

   Tunggu 24-48 jam untuk review manual
----------------------------------------------------------

Statistik:
   Total: 15 | Berhasil: 12 | Gagal: 3
   Tingkat Keberhasilan: 80.0%
```

### **Contoh 2: Mode dengan Proxy**
```
============================================================
         Alat Verifikasi Google One (Gemini AI Pro)
                  Diskon Mahasiswa SheerID
============================================================

   Menggunakan proxy: 192.168.1.100:8080
   Masukkan URL verifikasi: [URL_DIMASUKKAN]

   Memproses...
   [PROSES SAMA DENGAN CONTOH 1]
```

## ⚠️ **Troubleshooting**

### **Tabel Error dan Solusi**
| Error | Penyebab | Solusi |
|-------|----------|---------|
| `TypeError: Client.__init__()` | Versi httpx tidak kompatibel | Gunakan Python portable yang disediakan |
| `ModuleNotFoundError` | Modul Python tidak terinstall | Jalankan `pip install httpx cloudscraper pillow` |
| `URL tidak valid` | URL verifikasi salah | Pastikan URL mengandung `sheerid.com` |
| `Sudah diverifikasi` | Akun sudah terverifikasi | Gunakan akun Google lain |
| `Unggah gagal` | Koneksi internet bermasalah | Cek koneksi atau gunakan proxy |
| `Langkah tidak valid` | Flow verifikasi berubah | Update script ke versi terbaru |
| `Proxy error` | Proxy tidak berfungsi | Cek koneksi proxy atau disable proxy |
| `Timeout` | Server lambat merespon | Coba lagi beberapa menit kemudian |

### **Tips Keberhasilan Tinggi**
1. **Gunakan Universitas AS** - Tingkat keberhasilan lebih tinggi
2. **Gunakan Proxy US** - Jika memungkinkan, gunakan proxy Amerika
3. **Email .edu** - Pastikan domain email adalah .edu
4. **Waktu Server** - Coba pada jam kerja AS (9 AM - 5 PM EST)
5. **Dokumen Transkrip** - Lebih berhasil daripada ID mahasiswa

## ❓ **FAQ**

### **Q: Apakah ini legal?**
A: Tool ini hanya mengotomatisasi proses verifikasi. Keputusan akhir ada di Google dan SheerID.

### **Q: Apakah akun saya bisa diblokir?**
A: Risiko selalu ada. Gunakan dengan bijak dan jangan berlebihan.

### **Q: Berapa lama proses verifikasi?**
A: Biasanya 24-48 jam untuk review manual.

### **Q: Bisa untuk negara selain AS?**
A: Untuk pendaftaran baru, hanya AS yang diterima. Negara lain mungkin bisa untuk pengguna existing.

### **Q: Apakah perlu VPN/proxy?**
A: Tidak wajib, tetapi proxy US bisa meningkatkan keberhasilan.

### **Q: Error "Already verified"?**
A: Akun Google tersebut sudah terverifikasi. Gunakan akun Google lain.

## ⚖️ **Disclaimer**

**Peringatan Penting:**
1. Tool ini hanya untuk tujuan edukasi
2. Pengguna bertanggung jawab penuh atas penggunaan tool
3. Tidak ada jaminan keberhasilan 100%
4. Google/SheerID dapat mengubah sistem verifikasi kapan saja
5. Penggunaan berlebihan dapat menyebabkan pemblokiran

**Kebijakan Penggunaan yang Bertanggung Jawab:**
- Gunakan hanya untuk keperluan pribadi
- Jangan jual atau komersialkan tool ini
- Hormati kebijakan Google dan SheerID
- Gunakan informasi yang sesuai dengan etika

## 💝 **Donasi**

Jika tool ini membantu Anda, pertimbangkan untuk mendukung pengembangan:

**💸 Saweria:** https://saweria.co/teknoxpert

**Dukungan Anda akan digunakan untuk:**
- Pemeliharaan server dan update
- Pengembangan fitur baru
- Research algoritma verifikasi
- Dokumentasi dan tutorial

## 📚 **Referensi**

### **Link Resmi Google:**
1. **Google AI Pro untuk Mahasiswa**  
   https://support.google.com/gemini/answer/16417758

2. **Gemini untuk Mahasiswa**  
   https://gemini.google/id/students/

3. **Syarat dan Ketentuan**  
   https://support.google.com/gemini/answer/16417758#eligibility

4. **Recommended**  
   [SheerID Verification Assistant via Web](https://ip123.in/sheerid/)   

### **Teknologi yang Digunakan:**
- **SheerID API**: REST API v2 untuk verifikasi
- **Python httpx**: HTTP client modern
- **PIL/Pillow**: Image processing untuk dokumen
- **Portable Python**: Python runtime embedded

### **Statistik Universitas:**
Data universitas dikumpulkan dari:
- Database SheerID resmi
- Statistik keberhasilan pengguna
- Update terakhir: Januari 2026

---

**⭐ Jika tool ini membantu, beri bintang di repository!**  
**🔄 Update terakhir:** Januari 2026  
**📧 Kontak:** wgalxczk3@mozmail.com 

---
*Tool ini dikembangkan secara independen dan tidak berafiliasi dengan Google LLC atau SheerID.*
