# PC Player

**PC Player** adalah pemutar media desktop Windows berbasis Python dan PyQt6 yang dirancang khusus dengan mengutamakan kecepatan, antarmuka minimalis, kontrol keyboard penuh (*keyboard-centric*), dan aksesibilitas ramah pembaca layar (screen reader friendly).

---

## Fitur Utama

- **Keyboard-Centric & Aksesibel:** Seluruh fungsi kendali (putar, jeda, volume, loop, playlist) dapat dioperasikan penuh melalui tombol keyboard dengan notifikasi ramah NVDA/JAWS.
- **Dukungan Audio & Video Lengkap:** Memutar seluruh format audio (`.mp3`, `.wav`, `.flac`, `.opus`, dll.) serta video (`.mp4`, `.webm`) dengan pemutar layar terpisah yang otomatis muncul.
- **Streaming & Pencarian Daring:** Putar langsung audio dari tautan internet (`Ctrl + L`) atau cari musik di internet (`Ctrl + F`).
- **Download Instan:** Simpan audio yang sedang di-streaming langsung ke komputer Anda (`Ctrl + D`).
- **A-B Loop:** Pengulangan bagian tertentu lagu secara presisi untuk latihan instrumen atau transkripsi audio.
- **Playlist Manager:** Buat, simpan (`Ctrl + S`), dan muat (`Ctrl + O`) daftar putar dalam format `.m3u`.

---

## Pintasan Keyboard (Shortcut)

### Pemutaran & Navigasi:
- **`Spasi`**: Putar (*Play*) / Jeda (*Pause*).
- **`Panah Kiri / Kanan`**: Mundur / Maju 5 detik.
- **`Panah Atas / Bawah`**: Naikkan / Turunkan volume.
- **`S / D / F`**: Kecepatan putar (Lambat / Normal / Cepat).

### Daftar Putar:
- **`Delete`**: Hapus lagu yang disorot dari daftar putar.
- **`Ctrl + Delete`**: Bersihkan seluruh isi daftar putar.
- **`Ctrl + S` / `Ctrl + O`**: Simpan / Buka berkas playlist `.m3u`.

### Fitur Lanjutan:
- **`I`**: Bacakan informasi audio (Codec, Bitrate, Judul, Artis).
- **`R`**: Nyalakan / Matikan mode Putar Ulang (*Repeat*).
- **`C`**: Nyalakan / Matikan mode Putar Acak (*Shuffle*).
- **`Ctrl + L`**: Buka tautan streaming internet.
- **`Ctrl + F`**: Cari lagu secara daring.
- **`Ctrl + D`**: Unduh musik streaming yang sedang diputar.
- **`[` / `]` / `\`**: Set Titik A Loop / Set Titik B Loop / Batalkan Loop.

---

## Unduhan & Pemasangan

Unduh berkas portabel **`PC_Player.exe`** dari menu [Releases](https://github.com/Mahfud-PG/pc-player/releases) dan jalankan langsung tanpa perlu instalasi.

---

## Pengembang

- **Mahfud Pg** & Tim Studio Hermes
- Lisensi: Terbuka untuk umum.
