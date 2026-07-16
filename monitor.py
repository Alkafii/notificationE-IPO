"""
Monitor e-ipo.co.id — kirim email jika ada IPO (card) baru di halaman utama.

Cara kerja:
1. Ambil HTML dari https://e-ipo.co.id/id/home
2. Parse setiap card IPO (ambil ID unik dari link "Info lebih lanjut", nama, status, sektor, dll)
3. Bandingkan dengan data tersimpan sebelumnya (seen_ipos.json)
4. Jika ada ID yang belum pernah tercatat -> kirim email notifikasi
5. Simpan ulang daftar ID yang sudah dilihat

Menjalankan file ini butuh environment variables (lihat README.md):
  SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, EMAIL_TO
"""

import json
import os
import re
import smtplib
import sys
from email.mime.text import MIMEText
from pathlib import Path

import requests
from bs4 import BeautifulSoup

URL = "https://e-ipo.co.id/id/home"
STATE_FILE = Path(__file__).parent / "seen_ipos.json"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
}


def fetch_html() -> str:
    resp = requests.get(URL, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    return resp.text


def parse_ipos(html: str) -> dict:
    """Kembalikan dict {ipo_id: info_dict} dari semua card di halaman."""
    soup = BeautifulSoup(html, "html.parser")
    ipos = {}

    for link in soup.select('a[href*="/id/ipo/"]'):
        href = link.get("href", "")
        match = re.search(r"/id/ipo/(\d+)/([^/\"?#]+)", href)
        if not match:
            continue
        ipo_id, slug = match.group(1), match.group(2)

        card = link.find_parent(["div", "article", "li"])
        name = None
        status = None
        if card:
            title_tag = card.find(["h4", "h5", "h3"])
            if title_tag:
                name = title_tag.get_text(strip=True)
            status_tag = card.find(string=re.compile(r"(Closed|Offering|Upcoming)", re.I))
            if status_tag:
                status = status_tag.strip()

        ipos[ipo_id] = {
            "id": ipo_id,
            "slug": slug,
            "name": name or slug,
            "status": status or "-",
            "url": f"https://e-ipo.co.id/id/ipo/{ipo_id}/{slug}",
        }

    return ipos


def load_seen() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {}


def save_seen(data: dict) -> None:
    STATE_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2))


def send_email(new_ipos: list) -> None:
    smtp_host = os.environ["SMTP_HOST"]
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_user = os.environ["SMTP_USER"]
    smtp_pass = os.environ["SMTP_PASS"]
    email_to = os.environ["EMAIL_TO"]

    lines = ["IPO baru terdeteksi di e-ipo.co.id:\n"]
    for ipo in new_ipos:
        lines.append(f"- {ipo['name']} ({ipo['status']})")
        lines.append(f"  {ipo['url']}\n")

    body = "\n".join(lines)
    msg = MIMEText(body, _charset="utf-8")
    msg["Subject"] = f"[e-IPO] {len(new_ipos)} IPO baru terdeteksi"
    msg["From"] = smtp_user
    msg["To"] = email_to

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.sendmail(smtp_user, [email_to], msg.as_string())


def main() -> int:
    html = fetch_html()
    current = parse_ipos(html)
    if not current:
        print("Tidak ada card IPO yang berhasil di-parse. Cek struktur HTML mungkin berubah.")
        return 1

    seen = load_seen()
    new_ids = [i for i in current if i not in seen]

    if new_ids:
        new_ipos = [current[i] for i in new_ids]
        print(f"Ditemukan {len(new_ipos)} IPO baru:")
        for ipo in new_ipos:
            print(f"  - {ipo['name']} ({ipo['url']})")
        send_email(new_ipos)
    else:
        print("Tidak ada IPO baru.")

    save_seen(current)
    return 0


if __name__ == "__main__":
    sys.exit(main())
