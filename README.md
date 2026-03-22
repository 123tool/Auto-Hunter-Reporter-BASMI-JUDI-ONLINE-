# 🛡️ Basmi Judi Online (Auto Hunter & Reporter)

Script otomatis berbasis Python untuk mendeteksi konten perjudian online pada domain tertentu (terutama yang menginjeksi situs pemerintah/pendidikan), mengambil bukti screenshot, dan mengirimkan laporan penyalahgunaan (abuse report) secara otomatis ke ISP/Hosting terkait serta notifikasi ke Telegram.

## ✨ Fitur Utama
- **Auto Hunter**: Mencari situs yang terinjeksi judi menggunakan Google Dorking secara otomatis.
- **Smart Detection**: Sistem scoring berdasarkan bobot kata kunci (mencegah false positive).
- **Evidence Collector**: Mengambil screenshot otomatis sebagai bukti visual.
- **Auto Report**: Mencari email abuse pengelola server melalui WHOIS dan mengirimkan email pengaduan otomatis.
- **Telegram Notify**: Laporan instan langsung ke smartphone Anda.
- **Asynchronous**: Proses scanning super cepat (paralel).

## 🛠️ Syarat
- Python 3.9 atau lebih tinggi.
- Akun Gmail (untuk mengirim laporan email).
- Bot Telegram (via @BotFather).

## 📥 Cara Instalasi

1. **Clone Repository ini:**
   ```bash
   git clone [https://github.com/123tool/Auto-Hunter-Reporter-BASMI-JUDI-ONLINE-.git]
   cd Auto-Hunter-Reporter-BASMI-JUDI-ONLINE
2. **Instal Library yang dibutuhkan:**
   ```bash
   pip install requests playwright python-whois googlesearch-python
3. **Instal Browser Engine (Playwright):**
   ```bash
   playwright install chromium
4. **Konfigurasi Script:**
   Buka file main.py dan isi bagian:
   ```bash
   ​TELEGRAM_TOKEN & CHAT_ID
   ​EMAIL_SENDER & EMAIL_PASSWORD (Gunakan App
   Password Gmail).
5. **🚀 Cara Menjalankan
   ​Jalankan script secara manual atau pasang
   di Crontab (VPS) untuk berjalan otomatis
   setiap 6 jam:**
   ```bash
   python main.py
6. **Atau Buka terminal :**
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Anti-Judol
   Ultimate System"
   git remote add origin
   https://github.com/123tool/Auto-Hunter-Reporter-BASMI-JUDI-ONLINE-.git push -u origin
   main

 ## 💡 Hal Penting Sebelum Run:
 
**1. App Password : Jangan pakai password Gmail
 utama. Masuk ke Google Account Security,
 aktifkan 2-Step Verification, lalu buat App
 Password.**
 
**2. Library: Jalankan pip install python-dotenv requests playwright python-whois googlesearch-python lalu playwright install chromium.**

 ## ⚠️ Disclaimer
 
   ​**Script ini dibuat untuk tujuan keamanan
   siber dan membantu memberantas konten
   ilegal di Indonesia. Penggunaan di luar
   tanggung jawab pengembang. Pastikan Anda
   memiliki izin atau menggunakan data laporan
   dengan bijak. ​Mari jaga internet Indonesia
   tetap bersih! 🇮🇩**
