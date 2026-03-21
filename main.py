import asyncio
import os
import requests
import smtplib
import whois
import time
from email.message import EmailMessage
from googlesearch import search
from playwright.async_api import async_playwright
from dotenv import load_dotenv

# ============================================================
# LOAD KONFIGURASI DARI FILE .env
# ============================================================
load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
EMAIL_SENDER = os.getenv('EMAIL_SENDER')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')

# Ambang batas skor untuk menentukan itu situs judi (0-100)
THRESHOLD_SCORE = 15

# Kata kunci dan bobot poin (Bisa ditambah sesuai tren)
KEYWORDS = {
    "slot gacor": 20, 
    "maxwin": 20, 
    "zeus slot": 15, 
    "deposit pulsa": 10, 
    "togel online": 20, 
    "jp paus": 15,
    "situs judi": 20, 
    "link alternatif": 10, 
    "bet murah": 10,
    "scatter hitam": 15
}

# Target tetap yang ingin dipantau terus (opsional)
MANUAL_TARGETS = []

# ============================================================
# FUNGSI HELPER
# ============================================================

def send_telegram(message, photo_path=None):
    """Mengirim pesan dan foto bukti ke Bot Telegram"""
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("[-] Skip Telegram: Token/Chat ID tidak diatur.")
        return

    url_msg = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    url_photo = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
    
    try:
        if photo_path and os.path.exists(photo_path):
            with open(photo_path, 'rb') as photo:
                requests.post(url_photo, data={'chat_id': CHAT_ID, 'caption': message, 'parse_mode': 'Markdown'}, files={'photo': photo})
        else:
            requests.post(url_msg, data={'chat_id': CHAT_ID, 'text': message, 'parse_mode': 'Markdown'})
    except Exception as e:
        print(f"[-] Gagal kirim Telegram: {e}")

def get_abuse_email(domain):
    """Mencari email penyalahgunaan (abuse) melalui WHOIS"""
    try:
        w = whois.whois(domain)
        emails = w.emails
        if isinstance(emails, list): 
            return emails[0]
        return emails if emails else "abuse@kominfo.go.id"
    except:
        return "abuse@kominfo.go.id"

def send_auto_report(domain, abuse_email, screenshot_path):
    """Mengirim email pengaduan otomatis ke Provider Hosting/ISP"""
    if not EMAIL_SENDER or not EMAIL_PASSWORD:
        print("[-] Skip Email: Kredensial email tidak diatur di .env")
        return False

    msg = EmailMessage()
    msg['Subject'] = f"URGENT: Laporan Konten Perjudian Online - {domain}"
    msg['From'] = EMAIL_SENDER
    msg['To'] = abuse_email
    
    body = f"""
Yth. Tim Abuse / Compliance,

Sistem monitoring keamanan siber kami mendeteksi adanya aktivitas perjudian online (Judi Online) pada infrastruktur/domain berikut yang berada dalam layanan Anda:

Domain: {domain}
Waktu Deteksi: {time.ctime()}

Konten ini melanggar regulasi konten ilegal (Perjudian) sesuai UU ITE di Indonesia. Kami mohon bantuan Anda untuk melakukan peninjauan dan tindakan pemblokiran (take down) segera. 

Terlampir adalah bukti screenshot halaman tersebut sebagai referensi. Terima kasih atas kerja samanya dalam menjaga ruang digital tetap aman.

Hormat kami,
Anti-Judol Automated System
    """
    msg.set_content(body)

    try:
        with open(screenshot_path, 'rb') as f:
            msg.add_attachment(f.read(), maintype='image', subtype='png', filename=f"evidence_{domain}.png")
        
        # Menggunakan SMTP Gmail (Port 465 untuk SSL)
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
            smtp.send_message(msg)
        return True
    except Exception as e:
        print(f"[-] Gagal kirim Email Report ke {abuse_email}: {e}")
        return False

def hunt_targets():
    """Mencari domain yang terinjeksi judi menggunakan Google Dorking"""
    print("[*] Mencari target baru di Google (Dorking Mode)...")
    queries = [
        'site:go.id "slot gacor"',
        'site:ac.id "maxwin"',
        'site:sch.id "togel"',
        'intitle:"daftar situs judi online" -facebook -instagram'
    ]
    
    found_domains = []
    for q in queries:
        try:
            # Mengambil 5-10 hasil teratas untuk setiap query
            for url in search(q, num_results=5):
                # Ekstrak domain saja dari URL
                domain = url.split("//")[-1].split("/")[0]
                if domain not in found_domains:
                    found_domains.append(domain)
        except Exception as e:
            print(f"[-] Google Search Error: {e}")
            continue
    return found_domains

async def process_domain(browser, domain):
    """Proses utama: Scan, Analisis, Screenshot, dan Report"""
    page = await browser.new_page()
    # Atur User-Agent agar tidak terdeteksi sebagai bot sederhana
    await page.set_extra_http_headers({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"})
    
    url = f"http://{domain}"
    print(f"[*] Memeriksa: {domain}")
    
    try:
        # Timeout 40 detik, tunggu sampai jaringan stabil
        await page.goto(url, timeout=40000, wait_until="networkidle")
        content = (await page.content()).lower()
        
        # Hitung Skor Berdasarkan Keyword
        score = 0
        detected_keywords = []
        for word, weight in KEYWORDS.items():
            if word in content:
                score += weight
                detected_keywords.append(word)
        
        # Jika skor melewati ambang batas, eksekusi tindakan
        if score >= THRESHOLD_SCORE:
            # 1. Ambil Bukti Screenshot
            ss_path = f"evidence_{domain.replace('.', '_')}.png"
            await page.screenshot(path=ss_path, full_page=False)
            
            # 2. Cari Kontak Abuse
            abuse_target = get_abuse_email(domain)
            
            # 3. Kirim Auto-Report via Email
            report_ok = send_auto_report(domain, abuse_target, ss_path)
            status_report = "✅ Terkirim" if report_ok else "❌ Gagal"
            
            # 4. Notifikasi ke Telegram
            alert_msg = (f"🚨 *JUDI ONLINE TERDETEKSI!*\n\n"
                         f"🌐 *Domain:* `{domain}`\n"
                         f"📊 *Skor Indikasi:* `{score}`\n"
                         f"🔍 *Keywords:* {', '.join(detected_keywords)}\n"
                         f"📧 *Report ke ISP:* `{abuse_target}`\n"
                         f"📩 *Status Email:* {status_report}\n"
                         f"⏰ *Waktu:* {time.ctime()}")
            
            send_telegram(alert_msg, ss_path)
            print(f"[!] POSITIF: {domain} terdeteksi judi dan telah dilaporkan.")
            
            # Hapus file screenshot lokal setelah dikirim untuk menghemat penyimpanan
            if os.path.exists(ss_path):
                os.remove(ss_path)
        else:
            print(f"[+] {domain} dinyatakan Aman (Skor: {score}).")
            
    except Exception as e:
        print(f"[-] Gagal mengakses {domain}: {e}")
    finally:
        await page.close()

async def main():
    print("\n" + "="*50)
    print("      ANTI-JUDOL ULTIMATE AUTO-SYSTEM V4.1      ")
    print("="*50 + "\n")
    
    # Cari target secara dinamis + gabungkan dengan manual
    dynamic_targets = hunt_targets()
    all_targets = list(set(MANUAL_TARGETS + dynamic_targets))
    
    if not all_targets:
        print("[!] Tidak ada target untuk diperiksa. Coba cek koneksi internet.")
        return

    print(f"[*] Menyiapkan pemindaian untuk {len(all_targets)} domain...\n")
    
    async with async_playwright() as p:
        # Jalankan browser dalam mode headless (tanpa jendela)
        browser = await p.chromium.launch(headless=True)
        
        # Menjalankan pemindaian secara paralel (asynchronous)
        tasks = [process_domain(browser, d) for d in all_targets]
        await asyncio.gather(*tasks)
        
        await browser.close()
    
    print("\n" + "="*50)
    print("            PROSES SELESAI / FINISHED           ")
    print("="*50 + "\n")

if __name__ == "__main__":
    # Pastikan library sudah terinstall sebelum running
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[!] Program dihentikan oleh pengguna.")
