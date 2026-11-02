# Log Pantau Alert Saham

Halaman log untuk alert saham gorengan (aplikasi web).

## Fitur
- Waktu scan terakhir dan 20 ticker yang dicek
- Trigger hari itu, atau keterangan eksplisit bila tidak ada trigger
- Linimasa 25 slot 09.00–15.00 WIB, slot yang hilang ditandai sebagai celah
- Riwayat per hari bursa

## Aturan
- Pemindaian terjadwal tiap 15 menit, Senin–Jumat 09.00–15.00 WIB
- Aturan trigger sama dengan alert WhatsApp yang sudah berjalan (VWAP, AKUM + SCALPING, ARA HUNTER, SCALPING AWAL)
- Dedup: maksimal sekali per ticker per jenis alert per hari
- Universe: 20 saham gorengan (ASLI, FUTR, PTRO, VKTR, PGAS, GOTO, TPIA, CUAN, BRPT, DSSA, BUMI, AADI, ENRG, INDY, MYOH, KINO, LINK, PTIS, SULI, NASI)
- Data dari Yahoo Finance IDX publik, bukan feed langsung BEI dan bukan real-time per tick

## Catatan
Halaman ini hanya log pantauan, tidak mengubah aturan atau daftar ticker alert. Hasil screening bukan rekomendasi pasti.

## Versi terminal (bisa dijalankan sendiri)
```bash
python3 log_pantau.py            # satu kali scan
python3 log_pantau.py --loop     # scan tiap 15 menit jam bursa
```
