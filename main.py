import asyncio
import os
import requests
import smtplib
import whois
import time
from email.message import EmailMessage
from googlesearch import search
from playwright.async_api import async_playwright

# ============================================================
# KONFIGURASI (WAJIB DIISI)
# ============================================================
TELEGRAM_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'
CHAT_ID = 'YOUR_TELEGRAM_CHAT_ID'

# Konfigurasi Email Pelaporan (Gunakan App Password jika Gmail)
EMAIL_SENDER = "email_kamu@gmail.com"
EMAIL_PASSWORD = "app_password_kamu" 

# Ambang batas skor untuk menentukan itu situs judi (0-100)
THRESHOLD_SCORE = 15

# Kata kunci dan bobot poin
KEYWORDS = {
    "slot gacor": 20, "maxwin": 20, "zeus slot": 15, 
    "deposit pulsa": 10, "togel online": 20, "jp paus": 15,
    "situs judi": 20, "link alternatif": 10, "bet murah": 10
}

# Target tetap (opsional, bisa dikosongkan jika ingin auto-search saja)
MANUAL_TARGETS = ["contoh-web-sekolah.sch.id"]
# ============================================================

def send_telegram(message, photo_path=None):
    """Mengirim pesan dan foto bukti ke Bot Telegram"""
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
        if isinstance(emails, list): return emails[0]
        return emails if emails else "abuse@kominfo.go.id"
    except:
        return "abuse@kominfo.go.id"

def send_auto_report(domain, abuse_email, screenshot_path):
    """Mengirim email pengaduan otomatis ke Provider Hosting/ISP"""
    msg = EmailMessage()
    msg['Subject'] = f"URGENT: Laporan Konten Perjudian Online - {domain}"
    msg['From'] = EMAIL_SENDER
    msg['To'] = abuse_email
    
    body = f"""
Kepada Tim Abuse / Compliance,

Sistem monitoring kami mendeteksi adanya aktivitas perjudian online (Judi Online) pada infrastruktur/domain berikut yang berada dalam layanan Anda:

Domain: {domain}
Waktu Deteksi: {time.ctime()}

Konten ini melanggar Undang-Undang ITE di Indonesia terkait penyebaran konten perjudian. Kami mohon bantuan Anda untuk melakukan peninjauan dan pemblokiran (take down) segera. Terlampir adalah bukti screenshot halaman tersebut.

Terima kasih atas kerja samanya dalam menjaga internet tetap aman.
    """
    msg.set_content(body)

    try:
        with open(screenshot_path, 'rb') as f:
            msg.add_attachment(f.read(), maintype='image', subtype='png', filename=f"evidence_{domain}.png")
        
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
            smtp.send_message(msg)
        return True
    except Exception as e:
        print(f"[-] Gagal kirim Email Report: {e}")
        return False

def hunt_targets():
    """Mencari domain yang terinjeksi judi menggunakan Google Dorking"""
    print("[*] Mencari target baru di Google (Dorking)...")
    queries = [
        'site:go.id "slot gacor"',
        'site:ac.id "maxwin"',
        'site:sch.id "togel"',
        'intitle:"daftar situs judi online"'
    ]
    
    found_domains = []
    for q in queries:
        try:
            for url in search(q, num_results=5):
                domain = url.split("//")[-1].split("/")[0]
                if domain not in found_domains:
                    found_domains.append(domain)
        except:
            continue
    return found_domains

async def process_domain(browser, domain):
    """Melakukan scanning, screenshot, dan reporting per domain"""
    page = await browser.new_page()
    url = f"http://{domain}"
    print(f"[*] Memeriksa: {domain}")
    
    try:
        await page.goto(url, timeout=60000, wait_until="networkidle")
        content = (await page.content()).lower()
        
        # Hitung Skor
        score = 0
        detected_keywords = []
        for word, weight in KEYWORDS.items():
            if word in content:
                score += weight
                detected_keywords.append(word)
        
        if score >= THRESHOLD_SCORE:
            ss_path = f"ss_{domain.replace('.', '_')}.png"
            await page.screenshot(path=ss_path)
            
            abuse_target = get_abuse_email(domain)
            report_ok = send_auto_report(domain, abuse_target, ss_path)
            
            status_report = "✅ Terkirim" if report_ok else "❌ Gagal"
            
            alert_msg = (f"🚨 *JUDI ONLINE TERDETEKSI!*\n\n"
                         f"🌐 *Domain:* `{domain}`\n"
                         f"📊 *Skor:* `{score}`\n"
                         f"🔍 *Keywords:* {', '.join(detected_keywords)}\n"
                         f"📧 *Report ISP:* `{abuse_target}` ({status_report})")
            
            send_telegram(alert_msg, ss_path)
            print(f"[!] POSITIF: {domain} dilaporkan.")
            
            if os.path.exists(ss_path): os.remove(ss_path)
        else:
            print(f"[+] {domain} Bersih.")
            
    except Exception as e:
        print(f"[-] Gagal akses {domain}: {e}")
    finally:
        await page.close()

async def main():
    print("=== STARTING ANTI-JUDOL AUTO SYSTEM ===")
    
    # Gabungkan target manual dan hasil hunting
    dynamic_targets = hunt_targets()
    all_targets = list(set(MANUAL_TARGETS + dynamic_targets))
    
    print(f"[*] Total {len(all_targets)} domain dalam antrean.")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Menjalankan scanning secara paralel
        tasks = [process_domain(browser, d) for d in all_targets]
        await asyncio.gather(*tasks)
        await browser.close()
    
    print("=== PEMERIKSAAN SELESAI ===")

if __name__ == "__main__":
    asyncio.run(main())
