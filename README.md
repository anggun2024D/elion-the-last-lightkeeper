# 🎮 Elion – The Last Lightkeeper

Elion – The Last Lightkeeper adalah game petualangan 2D berbasis **Python** dan **Pygame**
yang dikembangkan sebagai **Proyek Ujian Akhir Semester (UAS)**  
mata kuliah **Pemrograman Berorientasi Objek (PBO)**.

Game ini dirancang untuk menunjukkan penerapan konsep **Object-Oriented Programming (OOP)**
secara nyata melalui sistem karakter, musuh, item, dan manajemen state permainan.

---

## 📌 Latar Belakang
Pemrograman Berorientasi Objek (OOP) merupakan paradigma penting dalam pengembangan
perangkat lunak modern karena memungkinkan kode yang lebih terstruktur, mudah
dikembangkan, dan mudah dipelihara.

Melalui proyek ini, konsep OOP tidak hanya dipelajari secara teoritis,
tetapi juga diterapkan langsung dalam bentuk **game 2D interaktif** menggunakan Pygame,
sehingga meningkatkan pemahaman mahasiswa terhadap implementasi nyata OOP.

---

## 🎯 Tujuan Pengembangan
Tujuan dari pembuatan game ini adalah:
- Menerapkan konsep **Encapsulation, Inheritance, dan Polymorphism**
- Membuat aplikasi game 2D berbasis OOP dengan struktur kode yang rapi
- Mengimplementasikan interaksi pemain, musuh, dan item secara objektif
- Mengembangkan game dengan alur gameplay yang jelas dan menarik
- Menyediakan dokumentasi dan laporan akademik yang lengkap

---

## 🧙 Deskripsi Game
Pemain berperan sebagai **Elion**, seorang Lightkeeper terakhir yang harus
mengembalikan cahaya dunia dengan mengumpulkan **Spirit Gems** dan membuka **Portal Cahaya**.

Dalam perjalanannya, Elion ditemani oleh **Companion Spirit** yang memberikan petunjuk,
sementara berbagai musuh berusaha menghalangi perjalanan menuju kemenangan.

**Detail Game:**
- Genre: 2D Top-Down Adventure
- Tema: Fantasy & Spiritual Journey
- Engine: Python + Pygame
- Platform: Desktop (Windows/Linux)

---

## 🕹️ Fitur Utama
- Sistem karakter Player dan Companion berbasis OOP
- Musuh dengan perilaku berbeda (Patrol & Chase)
- Penerapan **Inheritance & Polymorphism** pada sistem musuh
- Sistem item (Spirit Gems) dan inventori
- Portal sebagai objektif kemenangan
- Particle system dan efek visual
- Camera follow dan screen shake
- HUD (Lives, Score, Gems, Timer)
- Win State & Menu System

---

## 🧩 Konsep OOP yang Diterapkan
### 1️⃣ Encapsulation
- Atribut penting seperti posisi, nyawa, dan inventori disembunyikan
- Akses data melalui method getter dan behavior internal class

### 2️⃣ Inheritance
- Kelas `Enemy` sebagai parent class
- `GlimpEnemy` dan `UmbraEnemy` sebagai child class

### 3️⃣ Polymorphism
- Method `take_action()` dioverride untuk perilaku musuh yang berbeda
- Pemanggilan method dilakukan secara uniform melalui objek parent

---

## 🗺️ Alur Gameplay Singkat
1. Pemain memulai game dari menu utama
2. Menjelajahi map dan mengumpulkan 3 Spirit Gems
3. Menghindari dan bertahan dari musuh
4. Portal akan aktif setelah semua gem terkumpul
5. Masuk portal untuk memicu **Win State**

---

## ⌨️ Kontrol
| Tombol | Fungsi |
|------|-------|
| W / A / S / D | Bergerak |
| Arrow Keys | Bergerak |
| ENTER | Mulai game / konfirmasi |
| ESC | Keluar dari game |

---

## ▶️ Cara Menjalankan Game
1. Pastikan Python 3 sudah terinstal
2. Install Pygame:
```
pip install pygame
```
Jalankan game:
```
python elion_pygame.py
```
---

👤 Pengembang

Nama: Anggun Amaylia Abdillah |
Mata Kuliah: Pemrograman Berorientasi Objek |
Proyek: UAS PBO

---
