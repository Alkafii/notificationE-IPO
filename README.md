# Monitor IPO Baru di e-ipo.co.id

Script ini mengecek halaman https://e-ipo.co.id/id/home secara berkala, dan
mengirim email HANYA jika ada card IPO baru yang muncul (bukan tiap kali cek).

## Isi Folder Ini
```
monitor.py                     -> script utama (scrape + kirim email)
requirements.txt                -> daftar library Python yang dibutuhkan
seen_ipos.json                  -> daftar IPO yang sudah pernah tercatat (baseline,
                                    sudah diisi IPO yang ada saat ini per Juli 2026,
                                    supaya upload ini TIDAK memicu email massal)
.github/workflows/monitor.yml   -> jadwal otomatis (tiap 30 menit) via GitHub Actions
```

## Cara Setup dari Nol

### 1. Hapus isi repo lama
Di repo GitHub kamu, hapus semua file lama (monitor.py, requirements.txt,
README.md, dan folder .github) supaya tidak bentrok dengan yang baru.

### 2. Upload semua file di folder ini
- Klik **Add file > Upload files**
- Upload `monitor.py`, `requirements.txt`, `seen_ipos.json`, `README.md`
  sekaligus (drag semua ke situ), klik **Commit changes**
- Untuk `.github/workflows/monitor.yml`: klik **Add file > Create new file**,
  di kotak nama file ketik `.github/workflows/monitor.yml`, lalu copy-paste
  isi file itu ke editor, klik **Commit changes**

### 3. Set Secrets (kalau belum ada dari sebelumnya, cek dulu di Settings > Secrets and variables > Actions)
| Secret | Isi |
|---|---|
| `SMTP_HOST` | `smtp.gmail.com` |
| `SMTP_PORT` | `587` |
| `SMTP_USER` | email pengirim (Gmail) |
| `SMTP_PASS` | App Password 16 karakter dari akun Gmail tsb |
| `EMAIL_TO` | email tujuan notifikasi |

Kalau secrets ini sudah pernah kamu isi sebelumnya dan tidak berubah, tidak
perlu diisi ulang — cukup pastikan nilainya masih benar.

### 4. Jalankan Manual Sekali untuk Tes
1. Tab **Actions** → **Monitor e-IPO** (menu kiri)
2. Klik **Run workflow** → klik tombol hijau **Run workflow**
3. Tunggu ~20 detik, refresh, pastikan hasilnya ✅ **Success** (bukan ❌)
4. Karena `seen_ipos.json` sudah berisi baseline IPO yang ada sekarang,
   run ini SEHARUSNYA menampilkan log "Tidak ada IPO baru." — artinya
   TIDAK ada email terkirim di percobaan ini. Itu tandanya sistem bekerja
   dengan benar.

### 5. Selesai
Setelah run pertama sukses, sistem otomatis cek tiap 30 menit. Email hanya
akan masuk saat benar-benar ada IPO baru yang belum pernah tercatat.

## Kalau Gagal (Status Failure ❌)
Klik run yang gagal → klik step yang ada tanda ❌ merah → baca pesan error,
lalu cocokkan dengan daftar ini:

- **Error terkait SMTP/email** (`SMTPAuthenticationError`, dll) →
  `SMTP_USER`/`SMTP_PASS` salah. Pastikan `SMTP_PASS` adalah App Password
  16 karakter, BUKAN password login Gmail biasa.
- **Error "failed to push some refs" / "rejected"** →
  Ada run lain yang sedang jalan bersamaan. Tunggu semua run selesai dulu
  (cek tidak ada status kuning "in progress"/"queued" di tab Actions),
  baru jalankan ulang manual.
- **"Tidak ada card IPO yang berhasil di-parse"** →
  Struktur halaman e-ipo.co.id berubah, `parse_ipos()` di `monitor.py`
  perlu disesuaikan ulang.

## Catatan
- Jadwal cron di `monitor.yml` (`*/30 * * * *`) memakai waktu UTC, dan bisa
  molor beberapa menit saat jam sibuk GitHub — ini normal.
- File `seen_ipos.json` dikelola otomatis oleh workflow (di-update tiap
  kali ada IPO baru terdeteksi). Tidak perlu diedit manual setelah setup awal.
