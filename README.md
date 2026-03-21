# 🛡️ Basmi Judi Online (Auto Hunter & Reporter)

Script otomatis berbasis Python untuk mendeteksi konten perjudian online pada domain tertentu (terutama yang menginjeksi situs pemerintah/pendidikan), mengambil bukti screenshot, dan mengirimkan laporan penyalahgunaan (abuse report) secara otomatis ke ISP/Hosting terkait serta notifikasi ke Telegram.

## ✨ Fitur Utama
- **Auto Hunter**: Mencari situs yang terinjeksi judi menggunakan Google Dorking secara otomatis.
- **Smart Detection**: Sistem scoring berdasarkan bobot kata kunci (mencegah false positive).
- **Evidence Collector**: Mengambil screenshot otomatis sebagai bukti visual.
- **Auto Report**: Mencari email abuse pengelola server melalui WHOIS dan mengirimkan email pengaduan otomatis.
- **Telegram Notify**: Laporan instan langsung ke smartphone Anda.
- **Asynchronous**: Proses scanning super cepat (paralel).

## 🛠️ Prasyarat
- Python 3.9 atau lebih tinggi.
- Akun Gmail (untuk mengirim laporan email).
- Bot Telegram (via @BotFather).

## 📥 Cara Instalasi

1. **Clone Repository ini:**
   ```bash
   git clone [https://github.com/username/basmi-judi-online.git](https://github.com/username/basmi-judi-online.git)
   cd basmi-judi-online
