# Final Project - Pemrograman Jaringan - D


## Anggota Kelompok - 7

| No. | Nama                              | NRP        |
|-----|-----------------------------------|------------|
| 1   | Haliza Nur Kamila Apalwan        | 5025231038 |
| 2   | Dea Kristin Ginting               | 5025231040 |
| 3   | Alma Khusnia                      | 5025231063 |
| 4   | Nadine Angela Joelita Irawan     | 5025231287 |
| 5   | Muhammad Aditya Handrian         | 5025231292 |

# Cara Menjalankan Game

Berikut adalah langkah-langkah untuk menjalankn game Tic Tac Toe
## Langkah-langkah
### 1. Dapatkan Alamat IP Server
- Buka Command Prompt (Windows) atau Terminal (macOS/Linux) pada device yang akan dijadikan server
- Ketik perintah berikut untuk mengetahui IP address lokal:
  - Windows: ipconfig (alamat IPv4)
  - macOS/Linux: ifconfig atau ip a (inet
- Catat IP address
### 2. Dapatkan Alamat IP Load Balancer
- Buka Command Prompt (Windows) atau Terminal (macOS/Linux) pada device yang akan dijadikan server
- Ketik perintah berikut untuk mengetahui IP address lokal:
  - Windows: ipconfig (alamat IPv4)
  - macOS/Linux: ifconfig atau ip a (inet
- Catat IP address
### 3. Ubah IP dan port pada Client
- Buka client.py
- Ubah IP address di baris berikut dengan IP address dan port load balancer
  ```
  BASE_URL = "http://10.8.195.69:8881"
  ```
### 4. Ubah IP dan port pada Load Balancer
- Buka load_balancer.py
- Ubah IP address di baris berikut dengan IP address dan port server
  ```
  backends = [
    'http://10.8.195.237:8889',
    'http://10.8.195.237:8890',
    'http://10.8.195.237:8891'
  ]
  ```
### 5. Jalankan Server
Gunakan command `python server_thread_http.py`
### 6. Jalankan healthy_check
Gunakan command `python healthy_check.py` untuk memonitor kinerja server
### 7. Jalankan Load Balancer
Gunakan command `load_balancer.py`
### 8. Jalankan Client
Gunakan command `python client.py`
### 9. Mulai Bermain
