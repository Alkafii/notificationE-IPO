# Monitor IPO Baru di e-ipo.co.id

Script ini mengecek halaman https://e-ipo.co.id/id/home secara berkala, dan
mengirim email jika ada card IPO baru yang muncul.

## Cara Kerja
- `monitor.py` mengambil HTML halaman, lalu mengekstrak setiap card IPO
  berdasarkan ID unik di link "Info lebih lanjut" (`/id/ipo/{id}/{slug}`).
- ID yang sudah pernah terlihat disimpan di `seen_ipos.json`.
- Kalau ada ID baru yang belum pernah tercatat -> email dikirim ke alamat tujuan.

## Opsi 1: Jalankan Otomatis via GitHub Actions (disarankan, gratis, tanpa server)

1. Buat repository baru di GitHub, lalu upload semua file di folder ini
   (termasuk folder `.github/workflows/`).
2. Buat App Password email (kalau pakai Gmail):
   - Aktifkan 2-Step Verification di akun Google.
   - Buka https://myaccount.google.com/apppasswords, buat App Password baru.
3. Di repo GitHub, buka **Settings > Secrets and variables > Actions**,
   tambahkan secrets berikut:
   - `SMTP_HOST` = `smtp.gmail.com`
   - `SMTP_PORT` = `587`
   - `SMTP_USER` = alamat email pengirim (misal `akunanda@gmail.com`)
   - `SMTP_PASS` = App Password yang dibuat di langkah 2
   - `EMAIL_TO`  = alamat email tujuan notifikasi
4. Selesai. Workflow akan otomatis jalan tiap 30 menit (bisa diubah di
   `.github/workflows/monitor.yml` bagian `cron`). Bisa juga dites manual
   lewat tab **Actions > Monitor e-IPO > Run workflow**.

   Catatan jadwal cron GitHub Actions: waktunya dalam UTC, dan pada jam sibuk
   bisa terlambat beberapa menit dari jadwal — ini normal & di luar kendali kita.

## Opsi 2: Jalankan Sendiri di Komputer/Server (cron biasa)

1. Install dependency:
   ```
   pip install -r requirements.txt
   ```
2. Set environment variables (bisa taruh di file `.env` lalu `source .env`,
   atau langsung export):
   ```
   export SMTP_HOST=smtp.gmail.com
   export SMTP_PORT=587
   export SMTP_USER=akunanda@gmail.com
   export SMTP_PASS=app_password_anda
   export EMAIL_TO=tujuan@email.com
   ```
3. Jalankan sekali untuk tes:
   ```
   python monitor.py
   ```
4. Tambahkan ke crontab supaya jalan otomatis tiap 30 menit:
   ```
   */30 * * * * cd /path/ke/eipo-monitor && /usr/bin/python3 monitor.py >> log.txt 2>&1
   ```

## Catatan Penting
- Struktur HTML web bisa berubah sewaktu-waktu. Kalau suatu saat script
  gagal mendeteksi card sama sekali (muncul pesan
  "Tidak ada card IPO yang berhasil di-parse"), berarti struktur HTML-nya
  berubah dan bagian `parse_ipos()` di `monitor.py` perlu disesuaikan lagi.
- Jalankan pertama kali dulu untuk membuat `seen_ipos.json` awal (baseline),
  supaya IPO yang SUDAH ada saat ini tidak dianggap "baru" dan memicu email
  massal di percobaan pertama.
- Kalau pakai provider email selain Gmail (mis. Outlook/Zoho), sesuaikan
  `SMTP_HOST` dan `SMTP_PORT` sesuai dokumentasi provider tsb.
