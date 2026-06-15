import os
import sys
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import pytz
from streamlit_javascript import st_javascript
import time
import shutil

# Konfigurasi Halaman - Wajib di baris pertama setelah import
st.set_page_config(page_title="Sistem Dokumentasi Privat v16", layout="wide")

# Set zona waktu resmi ke WIB
WIB = pytz.timezone('Asia/Jakarta')

# --- PERUBAHAN NAMA DATABASE & FORMAT PENYIMPANAN BARU (v6) ---
DATABASE_FILE = "data_kegiatan_v6.csv"
USER_FILE = "data_users_v6.csv"
THEME_FILE = "data_themes_v6.csv"
STATUS_THEME_FILE = "status_theme_v6.txt" 
LOG_FILE = "data_aktivitas_log_v6.csv"
FOLDER_UTAMA_MEDIA = "media_simpanan_baru"  # Folder baru untuk foto & video

PATH_FOTO = os.path.join(FOLDER_UTAMA_MEDIA, "Foto")
PATH_VIDEO = os.path.join(FOLDER_UTAMA_MEDIA, "Video")

# Memastikan folder media baru tetap ada
for path in [PATH_FOTO, PATH_VIDEO]:
    if not os.path.exists(path): os.makedirs(path)
    if not os.path.exists(os.path.join(path, "Umum")): os.makedirs(os.path.join(path, "Umum"))

# --- SISTEM PENGAMANAN DATABASE MUTLAK ---
try:
    df_cek_kegiatan = pd.read_csv(DATABASE_FILE)
except Exception:
    df = pd.DataFrame(columns=["ID", "Tanggal", "Nama Kegiatan", "Kategori", "Folder", "Detail", "File Dokumentasi", "Waktu_Upload", "Masa_Berlaku_Menit", "Oleh_Admin"])
    df.to_csv(DATABASE_FILE, index=False)

try:
    df_cek_user = pd.read_csv(USER_FILE)
except Exception:
    df_user = pd.DataFrame([{"username": "admin", "email": "admin@email.com", "password": "adminsaja", "role": "Admin"}])
    df_user.to_csv(USER_FILE, index=False)

try:
    df_cek_tema = pd.read_csv(THEME_FILE)
except Exception:
    tema_awal = [
        {"Nama_Tema": "Dark Cyberpunk 🤖", "Bg_Color": "#0e1117", "Sidebar_Color": "#1f2937", "Text_Color": "#00ffcc", "Button_Color": "#ff007f", "Card_Bg": "#111827"},
        {"Nama_Tema": "Light Clean ☀️", "Bg_Color": "#f3f4f6", "Sidebar_Color": "#ffffff", "Text_Color": "#111827", "Button_Color": "#2563eb", "Card_Bg": "#ffffff"},
        {"Nama_Tema": "Midnight Blue 🌌", "Bg_Color": "#0b132b", "Sidebar_Color": "#1c2541", "Text_Color": "#ffffff", "Button_Color": "#48cae4", "Card_Bg": "#1c2541"},
        {"Nama_Tema": "Emerald Nature 🌿", "Bg_Color": "#132a13", "Sidebar_Color": "#31572c", "Text_Color": "#ecf39e", "Button_Color": "#90a955", "Card_Bg": "#31572c"}
    ]
    pd.DataFrame(tema_awal).to_csv(THEME_FILE, index=False)

if not os.path.exists(STATUS_THEME_FILE):
    with open(STATUS_THEME_FILE, "w", encoding="utf-8") as f:
        f.write("Dark Cyberpunk 🤖")

try:
    df_cek_log = pd.read_csv(LOG_FILE)
except Exception:
    df_log_init = pd.DataFrame(columns=["Waktu Kejadian (WIB)", "Username", "Aktivitas", "Detail Informasi"])
    df_log_init.to_csv(LOG_FILE, index=False)

# --- FUNGSI OPERASIONAL DATABASE ---
def baca_users(): return pd.read_csv(USER_FILE)
def simpan_users(df): df.to_csv(USER_FILE, index=False)
def baca_kegiatan(): return pd.read_csv(DATABASE_FILE)
def simpan_kegiatan(df): df.to_csv(DATABASE_FILE, index=False)
def baca_tema(): return pd.read_csv(THEME_FILE)
def simpan_tema(df): df.to_csv(THEME_FILE, index=False)
def baca_log(): return pd.read_csv(LOG_FILE)

def catat_log(username, aktivitas, detail):
    try:
        df_log_sekarang = pd.read_csv(LOG_FILE)
    except Exception:
        df_log_sekarang = pd.DataFrame(columns=["Waktu Kejadian (WIB)", "Username", "Aktivitas", "Detail Informasi"])
    waktu_sekarang_str = datetime.now(WIB).strftime("%Y-%m-%d %H:%M:%S")
    data_baru = [{"Waktu Kejadian (WIB)": waktu_sekarang_str, "Username": username, "Aktivitas": aktivitas, "Detail Informasi": detail}]
    df_log_sekarang = pd.concat([df_log_sekarang, pd.DataFrame(data_baru)], ignore_index=True)
    df_log_sekarang.to_csv(LOG_FILE, index=False)

def ambil_daftar_folder(kategori):
    path_base = PATH_FOTO if kategori in ["Foto", "Photos", "照片", "Fotos"] else PATH_VIDEO
    if not os.path.exists(path_base): return ["Umum"]
    return [f for f in os.listdir(path_base) if os.path.isdir(os.path.join(path_base, f))]

def ambil_tema_aktif_sistem():
    with open(STATUS_THEME_FILE, "r", encoding="utf-8") as f:
        return f.read().strip()

def set_tema_aktif_sistem(nama_tema):
    with open(STATUS_THEME_FILE, "w", encoding="utf-8") as f:
        f.write(nama_tema)

# --- KAMUS MULTI-BAHASA LENGKAP (10 BAHASA UTUH) ---
KAMUS = {
    "Indonesia": {
        "navigasi": "🧭 Navigasi", "belum_login": "Status: Belum Login", "logout": "Keluar (Log Out)",
        "menu_akses": "🔐 Akses Masuk Sistem", "pilih_menu": "Pilih Menu Akses:", "tab_masuk": "Masuk (Log In)",
        "tab_daftar": "Daftar Akun Baru", "tab_lupa": "🔑 Lupa Akun / Password", "username": "Username:",
        "password": "Password:", "btn_masuk": "Log In", "err_login": "Username atau Password salah!",
        "form_daftar": "Form Pendaftaran Akun", "buat_user": "Buat Username (Tanpa Spasi):", "masukan_email": "Masukkan Gmail Anda:",
        "buat_pass": "Buat Password Anda:", "btn_daftar": "Daftar Sekarang", "err_user_ada": "Username sudah terdaftar!",
        "sukses_daftar": "Pendaftaran Berhasil! Silakan log in.", "wajib_isi": "Semua kolom wajib diisi!",
        "bantuan_pulih": "Bantuan Pemulihan Akun Instan", "info_pulih": "Masukkan Gmail terdaftar Anda. Sistem akan mencari akun Anda lalu memindahkan Anda ke halaman login dan mengisi datanya secara otomatis!",
        "btn_pulih": "Pulihkan Akun & Pindah ke Log In", "err_email_salah": "Gmail tidak valid! Email tersebut belum terdaftar.",
        "pilih_email_dulu": "Harap masukkan email terlebih dahulu!", "galeri_title": "🎬 Galeri Kegiatan & Catatan Aktif",
        "filter_kat": "### 🔍 Filter Kategori", "pilih_jenis": "Pilih Jenis Dokumentasi:", "semua": "Semua",
        "catatan_saja": "Catatan saja", "foto": "Foto", "video": "Video", "pilih_f_internal": "📁 Pilih Folder di dalam Kategori",
        "semua_folder": "Semua Folder", "kosong": "Belum ada catatan kegiatan saat ini.", "sisa_waktu": "⏳ **Sisa Waktu Tampil:**",
        "hari": "Hari", "jam": "Jam", "menit": "Menit", "detik": "Detik", "permanen": "📌 Bersifat Permanen", "hanya_teks": "📌 Hanya Catatan Teks (Tidak Ada File)",
        "salin_share": "##### 🔗 Salin Catatan untuk Di-share:", "tanggal": "Tanggal", "detail": "Detail Keterangan",
        "menu_1": "🎬 Catatan & Dokumentasi Aktif", "menu_2": "➕ Input & Hapus Catatan", "menu_3": "📁 Manajemen Folder Kategori",
        "menu_4": "📊 Pusat Dashboard & Monitoring Log", "menu_5": "👥 Manajemen User & Password", "menu_6": "🎨 Pusat Tema GUI Global (Admin)", "pilih_hal": "Pilih Halaman:",
        "btn_refresh": "🔄 Perbarui Halaman", "msg_refresh": "Halaman berhasil diperbarui!", "halo": "Halo", "toast_logout": "👋 Berhasil Log Out dari sistem!",
        "toast_login_gagal": "❌ Login Gagal! Periksa kembali Username & Password Anda.", "toast_reg_gagal": "❌ Registrasi Gagal! Username sudah digunakan.",
        "toast_reg_kosong": "⚠️ Registrasi Gagal! Kolom tidak boleh kosong.", "toast_pulih_sukses": "Akun ditemukan! Data otomatis diisi.",
        "toast_pulih_gagal": "❌ Pemulihan Gagal! Gmail tidak terdaftar.", "toast_pulih_warning": "⚠️ Input Diperlukan! Isi Gmail terlebih dahulu.",
        "download_btn": "📥 Download", "toast_dl": "📥 File berhasil diunduh!", "toast_galeri_update": "Koleksi galeri berhasil di-update!",
        "admin_title_catatan": "🛠️ Pusat Kontrol Catatan (Akses Admin)", "tab_tambah_c": "➕ Tambah Catatan Baru", "tab_hapus_c": "🗑️ Hapus Catatan",
        "lbl_pilih_kat_dulu": "1. Pilih Jenis Kategori Terlebih Dahulu:", "lbl_nama_keg": "Nama Kegiatan/Catatan:", "lbl_folder": "Folder:",
        "lbl_upload_media": "Upload Media (Bisa pilih banyak file sekaligus):", "lbl_durasi_tampil": "### ⏱️ Atur Durasi Masa Tampil Konten",
        "lbl_jadikan_perm": "Jadikan Postingan Ini Permanen (Selalu Tampil)", "btn_publikasi": "Publikasikan", "msg_proses_upload": "⏳ Sedang memproses dan mengunggah semua file berkas Anda...",
        "msg_upload_sukses": "✅ Seluruh berkas sukses dipublikasikan!", "toast_form_bersih": "🚀 Form dibersihkan otomatis!", "msg_upload_gagal": "❌ Publikasi Gagal! Nama kegiatan wajib diisi.",
        "lbl_pilih_hapus_c": "Pilih Catatan yang Ingin Dihapus:", "btn_hapus_perm": "Hapus Secara Permanen", "msg_hapus_sukses": "🗑️ Catatan berhasil dihapus dari sistem!",
        "msg_hapus_gagal": "❌ Penghapusan Gagal! Catatan tidak valid.", "lbl_buat_f_baru": "### Buat Folder Kategori Baru", "lbl_nama_f_baru": "Nama Folder Baru:",
        "lbl_jenis_kat_f": "Pilih Jenis Kategori Folder:", "btn_buat_f": "Buat Folder Sekarang", "msg_f_sukses": "📁 Folder baru berhasil dibuat!",
        "msg_f_gagal_kosong": "⚠️ Pembuatan Gagal! Nama folder tidak boleh kosong.", "lbl_hapus_f_title": "### Hapus Folder Kategori",
        "lbl_f_warning": "🚨 PERINGATAN: Menghapus folder akan menghapus SELURUH FILE MEDIA di dalamnya secara permanen!", "lbl_pilih_f_hapus": "Pilih Folder yang Akan Dihapus Permanen:",
        "btn_hapus_f_perm": "Hapus Folder Secara Permanen", "msg_proses_hapus_f": "⏳ Sedang menghapus folder beserta seluruh isi berkas...",
        "msg_hapus_f_sukses": "🗑️ Folder sukses dimusnahkan dari server!", "msg_hapus_f_gagal": "❌ Gagal menghapus folder!", "msg_no_f_kustom": "Tidak ada folder kustom yang bisa dihapus.",
        "lbl_stats": "### 📈 Statistik Penyimpanan", "lbl_total_c": "Total Baris Catatan Kegiatan", "lbl_total_u": "Total Pengguna Sistem",
        "lbl_tema_aktif": "Tema Utama Aktif Web", "lbl_live_log": "### ⏱️ Live Log: Riwayat Login & Pendaftaran User", "lbl_info_log": "Tabel menampilkan data tanggal & jam secara riil berurutan dari yang paling baru:",
        "msg_log_kosong": "Belum ada riwayat aktivitas yang terekam.", "lbl_intip_db": "### 🔍 Intip File Database Mentah", "lbl_daftar_pengguna": "### 📋 Daftar Pengguna Terdaftar",
        "lbl_edit_akun_title": "### ✏️ Edit Data Akun (Gmail, Password & Role)", "lbl_pilih_u_edit": "Pilih Username yang Akan Diedit:", "lbl_ubah_gmail": "Ubah Gmail:",
        "lbl_ubah_pass": "Ubah Password:", "lbl_ubah_role": "Ubah Hak Akses (Role):", "btn_simpan_akun": "Simpan Perubahan Akun",
        "msg_edit_u_sukses": "✏️ Perubahan Akun Telah Berhasil Disimpan!", "msg_edit_u_gagal": "❌ Pembaruan Gagal! Gmail dan Password tidak boleh kosong.",
        "lbl_pilih_tema_all": "Pilih tema yang ingin langsung diterapkan di HP/Laptop semua user:", "btn_terapkan_tema": "Terapkan Tema ke Seluruh Website 🌍",
        "msg_tema_sukses": "🎨 Tema Telah Berhasil Diterapkan Global!", "msg_tema_gagal": "❌ Gagal Menerapkan! Pilihan tema tidak valid.",
        "lbl_buat_tema_kustom": "Nama Tema Baru (Contoh: Sweet Pink 🌸):", "lbl_c_bg": "Pilih Warna Latar Belakang (Background):",
        "lbl_c_side": "Pilih Warna Sidebar Samping:", "lbl_c_txt": "Pilih Warna Teks Utama:", "lbl_c_btn": "Pilih Warna Tombol Utama (Accent):",
        "lbl_c_card": "Pilih Warna Kotak Kartu Galeri (Card):", "btn_simpan_tema": "Simpan Tema Baru", "msg_buat_t_gagal": "❌ Pembuatan Gagal! Nama tema sudah terdaftar atau kosong."
    },
    "English": {
        "navigasi": "🧭 Navigation", "belum_login": "Status: Not Logged In", "logout": "Log Out",
        "menu_akses": "🔐 System Entry Access", "pilih_menu": "Select Access Menu:", "tab_masuk": "Log In",
        "tab_daftar": "Register New Account", "tab_lupa": "🔑 Forgot Username / Password", "username": "Username:",
        "password": "Password:", "btn_masuk": "Log In", "err_login": "Incorrect Username or Password!",
        "form_daftar": "Account Registration Form", "buat_user": "Create Username (No Spaces):", "masukan_email": "Enter Your Gmail:",
        "buat_pass": "Create Your Password:", "btn_daftar": "Register Now", "err_user_ada": "Username is already registered!",
        "sukses_daftar": "Registration Successful! Please log in.", "wajib_isi": "All fields are required!",
        "bantuan_pulih": "Instant Account Recovery Help", "info_pulih": "Enter your registered Gmail. The system will look up your account, automatically redirect you to the login page, and autofill your credentials!",
        "btn_pulih": "Recover Account & Go to Log In", "err_email_salah": "Invalid Gmail! This email is not registered.",
        "pilih_email_dulu": "Please enter your email first!", "galeri_title": "🎬 Active Gallery & Notes",
        "filter_kat": "### 🔍 Category Filter", "pilih_jenis": "Select Documentation Type:", "semua": "All",
        "catatan_saja": "Notes only", "foto": "Photos", "video": "Videos", "pilih_f_internal": "📁 Select Folder inside Category",
        "semua_folder": "All Folders", "kosong": "No active notes available at the moment.", "sisa_waktu": "⏳ **Remaining Display Time:**",
        "hari": "Days", "jam": "Hours", "menit": "Minutes", "detik": "Seconds", "permanen": "📌 Permanent Post", "hanya_teks": "📌 Text Note Only (No File Attached)",
        "salin_share": "##### 🔗 Copy Note to Share:", "tanggal": "Date", "detail": "Detail Description",
        "menu_1": "🎬 Active Gallery & Notes", "menu_2": "➕ Input & Delete Notes", "menu_3": "📁 Folder Management",
        "menu_4": "📊 Dashboard & Database Monitor", "menu_5": "👥 User & Password Management", "menu_6": "🎨 GUI Global Themes (Admin)", "pilih_hal": "Select Page:",
        "btn_refresh": "🔄 Refresh Page", "msg_refresh": "Page refreshed successfully!", "halo": "Hello", "toast_logout": "👋 Logged out successfully!",
        "toast_login_gagal": "❌ Login Failed! Check Username & Password.", "toast_reg_gagal": "❌ Registration Failed! Username taken.",
        "toast_reg_kosong": "⚠️ Registration Failed! Empty fields.", "toast_pulih_sukses": "Account found! Fields auto-filled.",
        "toast_pulih_gagal": "❌ Recovery Failed! Gmail not found.", "toast_pulih_warning": "⚠️ Input Required! Enter Gmail first.",
        "download_btn": "📥 Download", "toast_dl": "📥 File downloaded successfully!", "toast_galeri_update": "Gallery updated!",
        "admin_title_catatan": "🛠️ Note Control Center (Admin Access)", "tab_tambah_c": "➕ Add New Note", "tab_hapus_c": "🗑️ Delete Note",
        "lbl_pilih_kat_dulu": "1. Select Category Type First:", "lbl_nama_keg": "Activity Name/Note:", "lbl_folder": "Folder:",
        "lbl_upload_media": "Upload Media (Multiple files allowed):", "lbl_durasi_tampil": "### ⏱️ Set Content Display Duration",
        "lbl_jadikan_perm": "Make This Post Permanent (Always Display)", "btn_publikasi": "Publish", "msg_proses_upload": "⏳ Processing and uploading your files...",
        "msg_upload_sukses": "✅ All files published successfully!", "toast_form_bersih": "🚀 Form cleared automatically!", "msg_upload_gagal": "❌ Publication Failed! Name is required.",
        "lbl_pilih_hapus_c": "Select Note to Delete:", "btn_hapus_perm": "Delete Permanently", "msg_hapus_sukses": "🗑️ Note deleted successfully!",
        "msg_hapus_gagal": "❌ Delete Failed! Invalid note.", "lbl_buat_f_baru": "### Create New Category Folder", "lbl_nama_f_baru": "New Folder Name:",
        "lbl_jenis_kat_f": "Select Folder Category Type:", "btn_buat_f": "Create Folder Now", "msg_f_sukses": "📁 New folder created successfully!",
        "msg_f_gagal_kosong": "⚠️ Creation Failed! Folder name cannot be empty.", "lbl_hapus_f_title": "### Delete Category Folder",
        "lbl_f_warning": "🚨 WARNING: Deleting a folder will PERMANENTLY remove ALL MEDIA FILES inside it!", "lbl_pilih_f_hapus": "Select Folder to Delete Permanently:",
        "btn_hapus_f_perm": "Delete Folder Permanently", "msg_proses_hapus_f": "⏳ Deleting folder and its contents...",
        "msg_hapus_f_sukses": "🗑️ Folder destroyed from server!", "msg_hapus_f_gagal": "❌ Failed to delete folder!", "msg_no_f_kustom": "No custom folders available to delete.",
        "lbl_stats": "### 📈 Storage Statistics", "lbl_total_c": "Total Activity Log Rows", "lbl_total_u": "Total System Users",
        "lbl_tema_aktif": "Active Global Web Theme", "lbl_live_log": "### ⏱️ Live Log: Login & Registration History", "lbl_info_log": "Table displays real-time date & time sorted from newest:",
        "msg_log_kosong": "No activity history recorded yet.", "lbl_intip_db": "### 🔍 Inspect Raw Database Files", "lbl_daftar_pengguna": "### 📋 Registered Users List",
        "lbl_edit_akun_title": "### ✏️ Edit Account Details (Gmail, Password & Role)", "lbl_pilih_u_edit": "Select Username to Edit:", "lbl_ubah_gmail": "Change Gmail:",
        "lbl_ubah_pass": "Change Password:", "lbl_ubah_role": "Change Role:", "btn_simpan_akun": "Save Account Changes",
        "msg_edit_u_sukses": "✏️ Account changes saved successfully!", "msg_edit_u_gagal": "❌ Update Failed! Gmail and Password cannot be empty.",
        "lbl_pilih_tema_all": "Select theme to apply immediately to all users:", "btn_terapkan_tema": "Apply Theme Global 🌍",
        "msg_tema_sukses": "🎨 Theme Applied Globally Successfully!", "msg_tema_gagal": "❌ Application Failed! Invalid theme choice.",
        "lbl_buat_tema_kustom": "New Theme Name (e.g., Sweet Pink 🌸):", "lbl_c_bg": "Select Background Color:",
        "lbl_c_side": "Select Side Sidebar Color:", "lbl_c_txt": "Select Main Text Color:", "lbl_c_btn": "Select Main Button Color (Accent):",
        "lbl_c_card": "Select Gallery Card Color:", "btn_simpan_tema": "Save New Theme", "msg_buat_t_gagal": "❌ Creation Failed! Theme name already exists or empty."
    },
    "China (中文)": {
        "navigasi": "🧭 导航", "belum_login": "状态: 未登录", "logout": "退出登录 (Log Out)",
        "menu_akses": "🔐 系统登录访问", "pilih_menu": "选择访问菜单:", "tab_masuk": "登录 (Log In)",
        "tab_daftar": "注册新账号", "tab_lupa": "🔑 忘记账号/密码", "username": "用户名:",
        "password": "密码:", "btn_masuk": "登录", "err_login": "用户名或密码错误！",
        "form_daftar": "账号注册表单", "buat_user": "创建用户名 (不能有空格):", "masukan_email": "输入您的 Gmail:",
        "buat_pass": "创建您的密码:", "btn_daftar": "立即注册", "err_user_ada": "用户名已被注册！",
        "sukses_daftar": "注册成功！请登录。", "wajib_isi": "所有字段均为必填项！",
        "bantuan_pulih": "即时账号找回帮助", "info_pulih": "输入您注册的 Gmail。系统将查找您的账号，自动重定向到登录页面并自动填写您的凭据！",
        "btn_pulih": "找回账号并前往登录", "err_email_salah": "无效的 Gmail！此邮箱未注册。",
        "pilih_email_dulu": "请先输入电子邮件！", "galeri_title": "🎬 动态艺廊与即时笔记",
        "filter_kat": "### 🔍 分类筛选器", "pilih_jenis": "选择文档类型:", "semua": "显示全部",
        "catatan_saja": "仅限笔记", "foto": "照片", "video": "视频", "pilih_f_internal": "📁 选择分类内部的文件夹",
        "semua_folder": "所有文件夹", "kosong": "目前没有任何有效的动态内容。", "sisa_waktu": "⏳ **剩余显示时间:**",
        "hari": "天", "jam": "小时", "menit": "分钟", "detik": "秒", "permanen": "📌 永久告示物", "hanya_teks": "📌 仅纯文字内容 (无文件)",
        "salin_share": "##### 🔗 复制文本内容以便分享:", "tanggal": "日期", "detail": "详细说明",
        "menu_1": "🎬 动态艺廊与即时笔记", "menu_2": "➕ 新增与删除笔记", "menu_3": "📁 分类文件夹控制中心",
        "menu_4": "📊 数据主控台与日志监控", "menu_5": "👥 用户权限与密码管理", "menu_6": "🎨 GUI 全局主题管理 (管理员)", "pilih_hal": "选择页面:",
        "btn_refresh": "🔄 刷新页面", "msg_refresh": "页面刷新成功！", "halo": "你好", "toast_logout": "👋 成功退出系统！",
        "toast_login_gagal": "❌ 登录失败！请检查用户名和密码。", "toast_reg_gagal": "❌ 注册失败！用户名已被使用。",
        "toast_reg_kosong": "⚠️ 注册失败！字段不能为空。", "toast_pulih_sukses": "找到账号！已自动填写数据。",
        "toast_pulih_gagal": "❌ 找回失败！Gmail 未注册。", "toast_pulih_warning": "⚠️ 需要输入！请先填写 Gmail。",
        "download_btn": "📥 下载", "toast_dl": "📥 文件下载成功！", "toast_galeri_update": "艺廊已更新！",
        "admin_title_catatan": "🛠️ 笔记控制中心 (管理员权限)", "tab_tambah_c": "➕ 添加新笔记", "tab_hapus_c": "🗑️ 删除笔记",
        "lbl_pilih_kat_dulu": "1. 请先选择分类类型:", "lbl_nama_keg": "活动名称/笔记:", "lbl_folder": "文件夹:",
        "lbl_upload_media": "上传媒体 (可同时选择多个文件):", "lbl_durasi_tampil": "### ⏱️ 设置内容显示时长",
        "lbl_jadikan_perm": "使此帖永久化 (始终显示)", "btn_publikasi": "发布", "msg_proses_upload": "⏳ 正在处理并上传您的所有文件...",
        "msg_upload_sukses": "✅ 所有文件发布成功！", "toast_form_bersih": "🚀 表单已自动清除！", "msg_upload_gagal": "❌ 发布失败！活动名称必填。",
        "lbl_pilih_hapus_c": "选择要删除的笔记:", "btn_hapus_perm": "永久删除", "msg_hapus_sukses": "🗑️ 笔记已成功从系统删除！",
        "msg_hapus_gagal": "❌ 删除失败！无效的笔记。", "lbl_buat_f_baru": "### 创建新分类文件夹", "lbl_nama_f_baru": "新文件夹名称:",
        "lbl_jenis_kat_f": "选择文件夹分类类型:", "btn_buat_f": "立即创建文件夹", "msg_f_sukses": "📁 新文件夹创建成功！",
        "msg_f_gagal_kosong": "⚠️ 创建失败！文件夹名称不能为空。", "lbl_hapus_f_title": "### 删除分类文件夹",
        "lbl_f_warning": "🚨 警告: 删除文件夹将永久移除其中所有的媒体文件！", "lbl_pilih_f_hapus": "选择要永久删除的文件夹:",
        "btn_hapus_f_perm": "永久删除文件夹", "msg_proses_hapus_f": "⏳ 正在删除文件夹及其所有内容...",
        "msg_hapus_f_sukses": "🗑️ 文件夹已成功从服务器销毁！", "msg_hapus_f_gagal": "❌ 无法删除文件夹！", "msg_no_f_kustom": "没有可删除的自定义文件夹。",
        "lbl_stats": "### 📈 存储统计", "lbl_total_c": "活动日志总行数", "lbl_total_u": "系统用户总数",
        "lbl_tema_aktif": "全局活动网页主题", "lbl_live_log": "### ⏱️ 实时日志: 登录与注册历史", "lbl_info_log": "表格显示实时日期和时间，按最新排序：",
        "msg_log_kosong": "尚无记录的历史活动。", "lbl_intip_db": "### 🔍 查看原始数据库文件", "lbl_daftar_pengguna": "### 📋 已注册用户列表",
        "lbl_edit_akun_title": "### ✏️ 修改账号信息 (Gmail, 密码 & 权限)", "lbl_pilih_u_edit": "选择要编辑的用户名:", "lbl_ubah_gmail": "修改 Gmail:",
        "lbl_ubah_pass": "修改 密码:", "lbl_ubah_role": "修改 权限 (Role):", "btn_simpan_akun": "保存账号修改",
        "msg_edit_u_sukses": "✏️ 账号修改保存成功！", "msg_edit_u_gagal": "❌ 更新失败！Gmail 和密码不能为空。",
        "lbl_pilih_tema_all": "选择要立即应用于所有用户设备的网页主题:", "btn_terapkan_tema": "全局应用主题 🌍",
        "msg_tema_sukses": "🎨 全局主题应用成功！", "msg_tema_gagal": "❌ 应用失败！无效的主题选择。",
        "lbl_buat_tema_kustom": "新主题名称 (例如: Sweet Pink 🌸):", "lbl_c_bg": "选择背景颜色:",
        "lbl_c_side": "选择侧边栏颜色:", "lbl_c_txt": "选择主要文本颜色:", "lbl_c_btn": "选择主要按钮颜色 (Accent):",
        "lbl_c_card": "选择艺廊卡片背景颜色:", "btn_simpan_tema": "保存新主题", "msg_buat_t_gagal": "❌ 创建失败！主题名称已存在或为空。"
    },
    "Spanyol (Español)": {
        "navigasi": "🧭 Navegación", "belum_login": "Estado: No registrado", "logout": "Cerrar sesión",
        "menu_akses": "🔐 Acceso al Sistema", "pilih_menu": "Seleccione menú de acceso:", "tab_masuk": "Iniciar sesión",
        "tab_daftar": "Registrar nueva cuenta", "tab_lupa": "🔑 ¿Olvidó usuario / contraseña?", "username": "Usuario:",
        "password": "Contraseña:", "btn_masuk": "Entrar", "err_login": "¡Usuario o contraseña incorrectos!",
        "form_daftar": "Formulario de Registro de Cuenta", "buat_user": "Crear Usuario (Sin espacios):", "masukan_email": "Ingrese su Gmail:",
        "buat_pass": "Crear su Contraseña:", "btn_daftar": "Registrarse ahora", "err_user_ada": "¡El nombre de usuario ya está registrado!",
        "sukses_daftar": "¡Registro exitoso! Por favor inicie sesión.", "wajib_isi": "¡Todos los campos son obligatorios!",
        "bantuan_pulih": "Ayuda de Recuperación Instantánea", "info_pulih": "Ingrese su Gmail registrado. ¡El sistema buscará su cuenta, lo redirigirá automáticamente a la página de inicio de sesión y completará sus datos!",
        "btn_pulih": "Recuperar cuenta e ir a Iniciar sesión", "err_email_salah": "¡Gmail no válido! Este correo no está registrado.",
        "pilih_email_dulu": "¡Por favor ingrese su correo electrónico primero!", "galeri_title": "🎬 Galería Activa y Notas",
        "filter_kat": "### 🔍 Filtro de Categorías", "pilih_jenis": "Seleccione tipo de documentación:", "semua": "Todos",
        "catatan_saja": "Solo notas", "foto": "Fotos", "video": "Videos", "pilih_f_internal": "📁 Seleccionar carpeta dentro de la categoría",
        "semua_folder": "Todas las carpetas", "kosong": "No hay notas activas disponibles en este momento.", "sisa_waktu": "⏳ **Tiempo restante de visualización:**",
        "hari": "Días", "jam": "Horas", "menit": "Minutos", "detik": "Segundos", "permanen": "📌 Publicación permanente", "hanya_teks": "📌 Solo nota de texto (Sin archivo adjunto)",
        "salin_share": "##### 🔗 Copiar nota para compartir:", "tanggal": "Fecha", "detail": "Descripción detallada",
        "menu_1": "🎬 Galería Activa y Notas", "menu_2": "➕ Añadir y Eliminar Notas", "menu_3": "📁 Gestión de Carpetas de Categorías",
        "menu_4": "📊 Panel de Control y Monitor de Registro", "menu_5": "👥 Gestión de Usuarios y Contraseñas", "menu_6": "🎨 Temas GUI Globales (Admin)", "pilih_hal": "Seleccione página:",
        "btn_refresh": "🔄 Actualizar página", "msg_refresh": "¡Página actualizada con éxito!", "halo": "Hola", "toast_logout": "👋 ¡Sesión cerrada con éxito!",
        "toast_login_gagal": "❌ ¡Inicio de sesión fallido! Verifique usuario y contraseña.", "toast_reg_gagal": "❌ ¡Registro fallido! Nombre de usuario ya tomado.",
        "toast_reg_kosong": "⚠️ ¡Registro fallido! Campos vacíos.", "toast_pulih_sukses": "¡Cuenta encontrada! Datos autocompletados.",
        "toast_pulih_gagal": "❌ ¡Recuperación fallida! Gmail no registrado.", "toast_pulih_warning": "⚠️ ¡Entrada requerida! Ingrese Gmail primero.",
        "download_btn": "📥 Descargar", "toast_dl": "¡¡Archivo descargado con éxito!!", "toast_galeri_update": "¡Galería actualizada!",
        "admin_title_catatan": "🛠️ Centro de Control de Notas (Acceso Admin)", "tab_tambah_c": "➕ Añadir Nueva Nota", "tab_hapus_c": "🗑️ Eliminar Nota",
        "lbl_pilih_kat_dulu": "1. Seleccione primero el tipo de categoría:", "lbl_nama_keg": "Nombre de actividad/Nota:", "lbl_folder": "Carpeta:",
        "lbl_upload_media": "Subir medios (Se permiten varios archivos):", "lbl_durasi_tampil": "### ⏱️ Ajustar duración de visualización",
        "lbl_jadikan_perm": "Hacer que esta publicación sea permanente (Siempre visible)", "btn_publikasi": "Publicar", "msg_proses_upload": "⏳ Procesando y subiendo todos sus archivos...",
        "msg_upload_sukses": "¡¡Todos los archivos publicados con éxito!!", "toast_form_bersih": "🚀 ¡Formulario limpiado automáticamente!", "msg_upload_gagal": "❌ ¡Publicación fallida! El nombre es obligatorio.",
        "lbl_pilih_hapus_c": "Seleccione nota a eliminar:", "btn_hapus_perm": "Eliminar permanentemente", "msg_hapus_sukses": "🗑️ ¡Nota eliminada con éxito del sistema!",
        "msg_hapus_gagal": "❌ ¡Eliminación fallida! Nota no válida.", "lbl_buat_f_baru": "### Crear Nueva Carpeta de Categoría", "lbl_nama_f_baru": "Nombre de nueva carpeta:",
        "lbl_jenis_kat_f": "Seleccione tipo de categoría de carpeta:", "btn_buat_f": "Crear carpeta ahora", "msg_f_sukses": "📁 ¡Nueva carpeta creada con éxito!",
        "msg_f_gagal_kosong": "⚠️ ¡Creación fallida! El nombre de la carpeta no puede estar vacío.", "lbl_hapus_f_title": "### Eliminar Carpeta de Categoría",
        "lbl_f_warning": "🚨 ADVERTENCIA: ¡Eliminar una carpeta borrará PERMANENTEMENTE TODOS LOS ARCHIVOS DE MEDIOS que contenga!", "lbl_pilih_f_hapus": "Seleccione carpeta a eliminar permanentemente:",
        "btn_hapus_f_perm": "Eliminar carpeta permanentemente", "msg_proses_hapus_f": "⏳ Eliminando carpeta y todo su contenido...",
        "msg_hapus_f_sukses": "🗑️ ¡Carpeta eliminada con éxito del servidor!", "msg_hapus_f_gagal": "❌ ¡Error al eliminar la carpeta!", "msg_no_f_kustom": "No hay carpetas personalizadas disponibles para eliminar.",
        "lbl_stats": "### 📈 Estadísticas de almacenamiento", "lbl_total_c": "Filas totales de registro de actividad", "lbl_total_u": "Usuarios totales del sistema",
        "lbl_tema_aktif": "Tema web global activo", "lbl_live_log": "### ⏱️ Registro en vivo: Historial de inicios de sesión y registros", "lbl_info_log": "La tabla muestra fecha y hora en tiempo real ordenadas por novedades:",
        "msg_log_kosong": "No hay historial de actividad registrado aún.", "lbl_intip_db": "### 🔍 Inspeccionar archivos de base de datos sin procesar", "lbl_daftar_pengguna": "### 📋 Lista de usuarios registrados",
        "lbl_edit_akun_title": "### ✏️ Editar datos de la cuenta (Gmail, Contraseña y Rol)", "lbl_pilih_u_edit": "Seleccione usuario a editar:", "lbl_ubah_gmail": "Cambiar Gmail:",
        "lbl_ubah_pass": "Cambiar Contraseña:", "lbl_ubah_role": "Cambiar Rol:", "btn_simpan_akun": "Guardar cambios de cuenta",
        "msg_edit_u_sukses": "✏️ ¡Cambios de cuenta guardados con éxito!", "msg_edit_u_gagal": "❌ ¡Actualización fallida! Gmail y contraseña no pueden estar vacíos.",
        "lbl_pilih_tema_all": "Seleccione el tema para aplicar de inmediato a todos los usuarios:", "btn_terapkan_tema": "Aplicar tema globalmente 🌍",
        "msg_tema_sukses": "🎨 ¡Tema aplicado globalmente con éxito!", "msg_tema_gagal": "❌ ¡Error al aplicar! Selección de tema no válida.",
        "lbl_buat_tema_kustom": "Nombre del nuevo tema (Ej: Sweet Pink 🌸):", "lbl_c_bg": "Seleccione color de fondo:",
        "lbl_c_side": "Seleccione color de la barra lateral:", "lbl_c_txt": "Seleccione color del texto principal:", "lbl_c_btn": "Seleccione color del botón principal (Acento):",
        "lbl_c_card": "Seleccione color de tarjeta de galería:", "btn_simpan_tema": "Guardar nuevo tema", "msg_buat_t_gagal": "❌ ¡Creación fallida! El nombre del tema ya existe o está vacío."
    },
    "Brazil (Português)": {
        "navigasi": "🧭 Navegação", "belum_login": "Status: Não Logado", "logout": "Sair (Log Out)",
        "menu_akses": "🔐 Acesso ao Sistema", "pilih_menu": "Selecione o menu de acesso:", "tab_masuk": "Entrar (Log In)",
        "tab_daftar": "Registrar Nova Conta", "tab_lupa": "🔑 Esqueceu Usuário / Senha?", "username": "Usuário:",
        "password": "Senha:", "btn_masuk": "Entrar", "err_login": "Usuário ou Senha incorretos!",
        "form_daftar": "Formulário de Registro de Conta", "buat_user": "Criar Usuário (Sem espaços):", "masukan_email": "Insira seu Gmail:",
        "buat_pass": "Criar sua Senha:", "btn_daftar": "Registrar Agora", "err_user_ada": "Este nome de usuário já está registrado!",
        "sukses_daftar": "Registro feito com sucesso! Por favor, faça o login.", "wajib_isi": "Todos os campos são obrigatórios!",
        "bantuan_pulih": "Ajuda de Recuperação Instantânea de Conta", "info_pulih": "Insira seu Gmail registrado. O sistema buscará sua conta, redirecionará você automaticamente para a página de login e preencherá seus dados!",
        "btn_pulih": "Recuperar Conta & Ir para o Login", "err_email_salah": "Gmail inválido! Este e-mail não está cadastrado.",
        "pilih_email_dulu": "Por favor, insira seu e-mail primeiro!", "galeri_title": "🎬 Galeria Ativa & Notas",
        "filter_kat": "### 🔍 Filtro de Categorias", "pilih_jenis": "Selecione o tipo de documentação:", "semua": "Todos",
        "catatan_saja": "Apenas notas", "foto": "Fotos", "video": "Vídeos", "pilih_f_internal": "📁 Selecionar pasta dentro da categoria",
        "semua_folder": "Todas as pastas", "kosong": "Nenhuma nota ativa disponível no momento.", "sisa_waktu": "⏳ **Tempo restante de exibição:**",
        "hari": "Dias", "jam": "Horas", "menit": "Minutos", "detik": "Segundos", "permanen": "📌 Publicação Permanente", "hanya_teks": "📌 Apenas Nota de Texto (Sem Arquivo)",
        "salin_share": "##### 🔗 Copiar Nota para Compartilhar:", "tanggal": "Data", "detail": "Descrição detalhada",
        "menu_1": "🎬 Galeria Ativa & Notas", "menu_2": "➕ Inserir & Excluir Notas", "menu_3": "📁 Gerenciamento de Pastas por Categoria center",
        "menu_4": "📊 Painel de Controle & Monitor de Logs", "menu_5": "👥 Gerenciamento de Usuários & Senhas", "menu_6": "🎨 Temas Globais da GUI (Admin)", "pilih_hal": "Selecione a página:",
        "btn_refresh": "🔄 Atualizar Página", "msg_refresh": "Página atualizada com sucesso!", "halo": "Olá", "toast_logout": "👋 Deslogado com sucesso do sistema!",
        "toast_login_gagal": "❌ Falha no Login! Verifique o Usuário & Senha.", "toast_reg_gagal": "❌ Falha no Registro! Usuário já existente.",
        "toast_reg_kosong": "⚠️ Falha no Registro! Campos não podem ficar vazios.", "toast_pulih_sukses": "Conta encontrada! Dados preenchidos automaticamente.",
        "toast_pulih_gagal": "❌ Falha na Recuperação! Gmail não cadastrado.", "toast_pulih_warning": "⚠️ Entrada obrigatória! Digite o Gmail primeiro.",
        "download_btn": "📥 Baixar", "toast_dl": "📥 Arquivo baixado com sucesso!", "toast_galeri_update": "Coleção da galeria atualizada!",
        "admin_title_catatan": "🛠️ Centro de Controle de Notas (Acesso Admin)", "tab_tambah_c": "➕ Adicionar Nova Nota", "tab_hapus_c": "🗑️ Excluir Nota",
        "lbl_pilih_kat_dulu": "1. Selecione o tipo de categoria primeiro:", "lbl_nama_keg": "Nome da atividade/Nota:", "lbl_folder": "Pasta:",
        "lbl_upload_media": "Enviar Mídia (Vários arquivos permitidos):", "lbl_durasi_tampil": "### ⏱️ Definir Duração de Exibição do Conteúdo",
        "lbl_jadikan_perm": "Tornar este Post Permanente (Sempre Exibir)", "btn_publikasi": "Publicar", "msg_proses_upload": "⏳ Processando e enviando todos os seus arquivos...",
        "msg_upload_sukses": "✅ Todos os arquivos publicados com sucesso!", "toast_form_bersih": "🚀 Formulário limpo automaticamente!", "msg_upload_gagal": "❌ Falha na Publicação! O nome é obrigatório.",
        "lbl_pilih_hapus_c": "Selecione a nota para excluir:", "btn_hapus_perm": "Excluir Permanentemente", "msg_hapus_sukses": "🗑️ Nota excluída com sucesso do sistema!",
        "msg_hapus_gagal": "❌ Falha na Exclusão! Nota inválida.", "lbl_buat_f_baru": "### Criar Nova Pasta de Categoria", "lbl_nama_f_baru": "Nome da Nova Pasta:",
        "lbl_jenis_kat_f": "Selecione o tipo de categoria da pasta:", "btn_buat_f": "Criar Pasta Agora", "msg_f_sukses": "📁 Nova pasta criada com sucesso!",
        "msg_f_gagal_kosong": "⚠️ Falha na Criação! O nome da pasta não pode estar vazio.", "lbl_hapus_f_title": "### Excluir Pasta de Categoria",
        "lbl_f_warning": "🚨 AVISO: Excluir uma pasta removerá PERMANENTEMENTE TODOS OS ARQUIVOS DE MÍDIA dentro dela!", "lbl_pilih_f_hapus": "Selecione a pasta para excluir permanentemente:",
        "btn_hapus_f_perm": "Excluir Pasta Permanentemente", "msg_proses_hapus_f": "⏳ Excluindo pasta e todos os seus arquivos internos...",
        "msg_hapus_f_sukses": "🗑️ Pasta destruída com sucesso do servidor!", "msg_hapus_f_gagal": "❌ Falha ao excluir a pasta!", "msg_no_f_kustom": "Nenhuma pasta personalizada disponível para exclusão.",
        "lbl_stats": "### 📈 Estatísticas de Armazenamento", "lbl_total_c": "Total de Linhas de Notas de Atividades", "lbl_total_u": "Total de Usuários do Sistema",
        "lbl_tema_aktif": "Tema Principal Ativo da Web", "lbl_live_log": "### ⏱️ Logs ao Vivo: Histórico de Login e Registro de Usuários", "lbl_info_log": "A tabela mostra a data e hora em tempo real ordenadas a partir da mais recente:",
        "msg_log_kosong": "Nenhum histórico de atividade gravado ainda.", "lbl_intip_db": "### 🔍 Inspecionar Arquivos Brutos do Banco de Dados", "lbl_daftar_pengguna": "### 📋 Lista de Usuários Cadastrados",
        "lbl_edit_akun_title": "### ✏️ Editar Dados da Conta (Gmail, Senha & Função)", "lbl_pilih_u_edit": "Selecione o Usuário para Editar:", "lbl_ubah_gmail": "Alterar Gmail:",
        "lbl_ubah_pass": "Alterar Senha:", "lbl_ubah_role": "Alterar Nível de Acesso (Função):", "btn_simpan_akun": "Salvar Alterações da Conta",
        "msg_edit_u_sukses": "✏️ Alterações da conta salvas com sucesso!", "msg_edit_u_gagal": "❌ Falha na Atualização! Gmail e senha não podem ficar vazios.",
        "lbl_pilih_tema_all": "Selecione o tema para aplicar imediatamente no dispositivo de todos os usuários:", "btn_terapkan_tema": "Aplicar Tema Globalmente 🌍",
        "msg_tema_sukses": "🎨 Tema aplicado globalmente com sucesso!", "msg_tema_gagal": "❌ Falha ao Aplicar! Escolha de tema inválida.",
        "lbl_buat_tema_kustom": "Nome do Novo Tema (Ex: Sweet Pink 🌸):", "lbl_c_bg": "Selecione a Cor de Fundo (Background):",
        "lbl_c_side": "Selecione a Cor da Barra Lateral:", "lbl_c_txt": "Selecione a Cor do Texto Principal:", "lbl_c_btn": "Selecione a Cor do Botão Principal (Destaque):",
        "lbl_c_card": "Selecione a Cor dos Cards da Galeria:", "btn_simpan_tema": "Salvar Novo Tema", "msg_buat_t_gagal": "❌ Falha na Criação! Nome do tema já existente ou vazio."
    },
    "Korea (한국어)": {
        "navigasi": "🧭 탐색", "belum_login": "상태: 로그인하지 않음", "logout": "로그아웃",
        "menu_akses": "🔐 시스템 로그인", "pilih_menu": "접근 메뉴 선택:", "tab_masuk": "로그인",
        "tab_daftar": "새 계정 등록", "tab_lupa": "🔑 아이디 / 비밀번호 찾기", "username": "사용자 이름:",
        "password": "비밀번호:", "btn_masuk": "로그인", "err_login": "사용자 이름 또는 비밀번호가 틀렸습니다!",
        "form_daftar": "회원가입 양식", "buat_user": "사용자 이름 생성 (공백 없음):", "masukan_email": "Gmail 입력:",
        "buat_pass": "비밀번호 생성:", "btn_daftar": "지금 가입하기", "err_user_ada": "이미 등록된 사용자 이름입니다!",
        "sukses_daftar": "등록 완료! 로그인해주세요.", "wajib_isi": "모든 필드를 채워야 합니다!",
        "bantuan_pulih": "실시간 계정 복구 지원", "info_pulih": "등록된 Gmail을 입력하세요. 시스템이 계정을 찾아 자동으로 로그인 페이지로 이동하고 자격 증명을 자동 완성합니다!",
        "btn_pulih": "계정 복구 및 로그인 페이지로 이동", "err_email_salah": "잘못된 Gmail입니다! 등록되지 않은 이메일입니다.",
        "pilih_email_dulu": "먼저 이메일을 입력하세요!", "galeri_title": "🎬 활성 갤러리 및 노트",
        "filter_kat": "### 🔍 카테고리 필터", "pilih_jenis": "문서 유형 선택:", "semua": "전체",
        "catatan_saja": "노트만", "foto": "사진", "video": "동영상", "pilih_f_internal": "📁 카테고리 내부 폴더 선택",
        "semua_folder": "모든 폴더", "kosong": "현재 활성화된 노트가 없습니다.", "sisa_waktu": "⏳ **남은 표시 시간:**",
        "hari": "일", "jam": "時間", "menit": "분", "detik": "초", "permanen": "📌 영구 게시물", "hanya_teks": "📌 텍스트 노트 전용 (파일 없음)",
        "salin_share": "##### 🔗 공유할 노트 복사:", "tanggal": "날짜", "detail": "상세 설명",
        "menu_1": "🎬 활성 갤러리 및 노트", "menu_2": "➕ 노트 입력 및 삭제", "menu_3": "📁 폴더 관리",
        "menu_4": "📊 대시보드 및 데이터베이스 모니터링", "menu_5": "👥 사용자 및 비밀번호 관리", "menu_6": "🎨 GUI 글로벌 테마 (관리자)", "pilih_hal": "페이지 선택:",
        "btn_refresh": "🔄 페이지 새로고침", "msg_refresh": "새로고침되었습니다!", "halo": "안녕하세요", "toast_logout": "👋 로그아웃 되었습니다!",
        "toast_login_gagal": "❌ 로그인 실패! 사용자 이름과 비밀번호를 확인하십시오.", "toast_reg_gagal": "❌ 회원가입 실패! 이미 존재하는 사용자 이름.",
        "toast_reg_kosong": "⚠️ 회원가입 실패! 모든 필드를 채워주세요.", "toast_pulih_sukses": "계정 발견! 데이터가 자동으로 채워졌습니다.",
        "toast_pulih_gagal": "❌ 복구 실패! 등록되지 않은 Gmail.", "toast_pulih_warning": "⚠️ 입력 필요! Gmail을 먼저 입력하세요.",
        "download_btn": "📥 다운로드", "toast_dl": "📥 다운로드 완료!", "toast_galeri_update": "갤러리가 업데이트 되었습니다!",
        "admin_title_catatan": "🛠️ 노트 관리 센터 (관리자 전용)", "tab_tambah_c": "➕ 새 노트 추가", "tab_hapus_c": "🗑️ 노트 삭제",
        "lbl_pilih_kat_dulu": "1. 카테고리 유형을 먼저 선택하십시오:", "lbl_nama_keg": "활동 명칭/노트:", "lbl_folder": "폴더:",
        "lbl_upload_media": "미디어 업로드 (여러 파일 동시 선택 가능):", "lbl_durasi_tampil": "### ⏱️ 콘텐츠 표시 기간 설정",
        "lbl_jadikan_perm": "이 게시물을 영구 게시물로 지정 (항상 표시)", "btn_publikasi": "게시하기", "msg_proses_upload": "⏳ 파일 처리 및 업로드 중...",
        "msg_upload_sukses": "✅ 모든 파일이 성공적으로 게시되었습니다!", "toast_form_bersih": "🚀 양식이 자동으로 초기화되었습니다!", "msg_upload_gagal": "❌ 게시 실패! 활동 명칭은 필수 항목입니다.",
        "lbl_pilih_hapus_c": "삭제할 노트를 선택하십시오:", "btn_hapus_perm": "영구 삭제", "msg_hapus_sukses": "🗑️ 노트가 시스템에서 영구히 삭제되었습니다!",
        "msg_hapus_gagal": "❌ 삭제 실패! 올바르지 않은 노트 항목입니다.", "lbl_buat_f_baru": "### 새 카테고리 폴더 만들기", "lbl_nama_f_baru": "새 폴더 이름:",
        "lbl_jenis_kat_f": "폴더 카테고리 유형 선택:", "btn_buat_f": "지금 폴더 생성", "msg_f_sukses": "📁 새 폴더가 생성되었습니다!",
        "msg_f_gagal_kosong": "⚠️ 생성 실패! 폴더 이름은 비워둘 수 없습니다.", "lbl_hapus_f_title": "### 카테고리 폴더 삭제",
        "lbl_f_warning": "🚨 경고: 폴더를 삭제하면 내부의 모든 미디어 파일이 영구적으로 제거됩니다!", "lbl_pilih_f_hapus": "영구 삭제할 폴더를 선택하십시오:",
        "btn_hapus_f_perm": "폴더 영구 삭제", "msg_proses_hapus_f": "⏳ 폴더 및 내부 콘텐츠 전체 삭제 중...",
        "msg_hapus_f_sukses": "🗑️ 폴더가 서버에서 안전하게 파기되었습니다!", "msg_hapus_f_gagal": "❌ 폴더 삭제 실패!", "msg_no_f_kustom": "삭제할 수 있는 사용자 지정 폴더가 없습니다.",
        "lbl_stats": "### 📈 스토리지 통계", "lbl_total_c": "총 활동 로그 행 수", "lbl_total_u": "총 시스템 사용자 수",
        "lbl_tema_aktif": "현재 활성화된 글로벌 웹 테마", "lbl_live_log": "### ⏱️ 라이브 로그: 로그인 및 회원가입 기록", "lbl_info_log": "테이블에는 가장 최근 항목부터 순서대로 실시간 날짜와 시간이 표시됩니다.",
        "msg_log_kosong": "기록된 활동 내역이 없습니다.", "lbl_intip_db": "### 🔍 원본 데이터베이스 파일 확인", "lbl_daftar_pengguna": "### 📋 등록된 사용자 목록",
        "lbl_edit_akun_title": "### ✏️ 계정 데이터 수정 (Gmail, 비밀번호 및 권한)", "lbl_pilih_u_edit": "수정할 사용자 이름을 선택하십시오:", "lbl_ubah_gmail": "Gmail 변경:",
        "lbl_ubah_pass": "비밀번호 변경:", "lbl_ubah_role": "접근 권한 (Role) 변경:", "btn_simpan_akun": "계정 변경 사항 저장",
        "msg_edit_u_sukses": "✏️ 계정 정보가 성공적으로 저장되었습니다!", "msg_edit_u_gagal": "❌ 업데이트 실패! Gmail과 비밀번호는 필수 입력 항목입니다.",
        "lbl_pilih_tema_all": "모든 사용자 장치에 즉시 적용할 웹 테마를 선택하십시오:", "btn_terapkan_tema": "전체 웹사이트에 테마 적용 🌍",
        "msg_tema_sukses": "🎨 테마가 전체 웹에 성공적으로 적용되었습니다!", "msg_tema_gagal": "❌ 적용 실패! 유효하지 않은 테마 선택입니다.",
        "lbl_buat_tema_kustom": "새 테마 이름 (예: Sweet Pink 🌸):", "lbl_c_bg": "배경 색상 선택:",
        "lbl_c_side": "사이드바 색상 선택:", "lbl_c_txt": "메인 텍스트 색상 선택:", "lbl_c_btn": "메인 버튼 색상 선택 (Accent):",
        "lbl_c_card": "갤러리 카드 배경 색상 선택:", "btn_simpan_tema": "새 테마 저장", "msg_buat_t_gagal": "❌ 생성 실패! 이미 존재하거나 빈 테마 이름입니다."
    },
    "Jepang (日本語)": {
        "navigasi": "🧭 ナビゲーション", "belum_login": "ステータス: 未ログイン", "logout": "ログアウト",
        "menu_akses": "🔐 システムログイン", "pilih_menu": "アクセスメニューの選択:", "tab_masuk": "ログイン",
        "tab_daftar": "新規アカウント登録", "tab_lupa": "🔑 ユーザー名・パスワードを忘れた場合", "username": "ユーザー名:",
        "password": "パスワード:", "btn_masuk": "ログイン", "err_login": "ユーザー名またはパスワードが正しくありません！",
        "form_daftar": "アカウント登録フォーム", "buat_user": "ユーザー名作成（スペースなし）:", "masukan_email": "Gmailを入力してください:",
        "buat_pass": "パスワード作成:", "btn_daftar": "今すぐ登録", "err_user_ada": "このユーザー名は既に登録されています！",
        "sukses_daftar": "登録が完了しました！ログインしてください。", "wajib_isi": "すべての項目が必須です！",
        "bantuan_pulih": "インスタントアカウント復旧ヘルプ", "info_pulih": "登録済みのGmailを入力してください。システムがアカウントを検索し、自動的にログインページにリダイレクトして情報を自動入力します！",
        "btn_pulih": "アカウントを復旧してログインへ", "err_email_salah": "無効なGmailです！このメールは登録されていません。",
        "pilih_email_dulu": "最初にメールアドレスを入力してください！", "galeri_title": "🎬 アクティブギャラリー＆ノート",
        "filter_kat": "### 🔍 カテゴリフィルター", "pilih_jenis": "ドキュメント形式の選択:", "semua": "すべて",
        "catatan_saja": "ノートのみ", "foto": "写真", "video": "動画", "pilih_f_internal": "📁 カテゴリ内のフォルダ選択",
        "semua_folder": "すべてのフォルダ", "kosong": "現在、アクティブなノートはありません。", "sisa_waktu": "⏳ **表示残り時間:**",
        "hari": "日", "jam": "時間", "menit": "分", "detik": "秒", "permanen": "📌 常時表示", "hanya_teks": "📌 テキストノートのみ（ファイルなし）",
        "salin_share": "##### 🔗 共有用ノートをコピー:", "tanggal": "日付", "detail": "詳細説明",
        "menu_1": "🎬 アクティブギャラリー＆ノート", "menu_2": "➕ ノートの追加・削除", "menu_3": "📁 フォルダ管理 Centre",
        "menu_4": "📊 Dashboard＆データベース監視", "menu_5": "👥 ユーザー＆パスワード管理中心", "menu_6": "🎨 GUI グローバルテーマ (管理者)", "pilih_hal": "ページ選択:",
        "btn_refresh": "🔄 ページを更新", "msg_refresh": "ページが正常に更新されました！", "halo": "こんにちは", "toast_logout": "👋 システムからログアウトしました！",
        "toast_login_gagal": "❌ ログイン失敗！ユーザー名とパスワードを再確認してください。", "toast_reg_gagal": "❌ 登録失敗！そのユーザー名は既に使われています。",
        "toast_reg_kosong": "⚠️ 登録失敗！空の欄があります。", "toast_pulih_sukses": "アカウント発見！データが自動入力されました。",
        "toast_pulih_gagal": "❌ 復旧失敗！Gmailが未登録です。", "toast_pulih_warning": "⚠️ 入力が必要です！最初にGmailを記入してください。",
        "download_btn": "📥 ダウンロード", "toast_dl": "📥 ファイルが正常にダウンロードされました！", "toast_galeri_update": "ギャラリーが更新されました！",
        "admin_title_catatan": "🛠️ ノートコントロールセンター (管理者権限)", "tab_tambah_c": "➕ 新規ノート追加", "tab_hapus_c": "🗑️ ノート削除",
        "lbl_pilih_kat_dulu": "1. 最初にカテゴリの種類を選択してください:", "lbl_nama_keg": "活動名・ノート項目:", "lbl_folder": "フォルダ:",
        "lbl_upload_media": "メディアをアップロード (複数ファイル選択可):", "lbl_durasi_tampil": "### ⏱️ 表示有効期限の設定",
        "lbl_jadikan_perm": "この投稿を常時表示 (永続) にする", "btn_publikasi": "公開する", "msg_proses_upload": "⏳ ファイルを処理してサーバーにアップロード中...",
        "msg_upload_sukses": "✅ すべてのファイルが正常に公開されました！", "toast_form_bersih": "🚀 フォームが自動的にリセットされました！", "msg_upload_gagal": "❌ 公開失敗！活動名は必須項目です。",
        "lbl_pilih_hapus_c": "削除するノートを選択してください:", "btn_hapus_perm": "永久削除", "msg_hapus_sukses": "🗑️ ノートがシステムから永久に削除されました！",
        "msg_hapus_gagal": "❌ 削除失敗！無効なノート項目です。", "lbl_buat_f_baru": "### 新規カテゴリフォルダ作成", "lbl_nama_f_baru": "新規フォルダ名:",
        "lbl_jenis_kat_f": "フォルダカテゴリの種類:", "btn_buat_f": "今すぐフォルダを作成", "msg_f_sukses": "📁 新しいフォルダが作成されました！",
        "msg_f_gagal_kosong": "⚠️ 作成失敗！フォルダ名は空にできません。", "lbl_hapus_f_title": "### カテゴリフォルダの削除",
        "lbl_f_warning": "🚨 警告: フォルダを削除すると、内部のすべてのメディアファイルが永久に消去されます！", "lbl_pilih_f_hapus": "永久削除するフォルダを選択してください:",
        "btn_hapus_f_perm": "フォルダを永久削除", "msg_proses_hapus_f": "⏳ フォルダおよびすべての内部コンテンツを消去中...",
        "msg_hapus_f_sukses": "🗑️ フォルダがサーバーから完全に消去されました！", "msg_hapus_f_gagal": "❌ フォルダの削除に失敗しました！", "msg_no_f_kustom": "削除可能なカスタムフォルダがありません。",
        "lbl_stats": "### 📈 ストレージ統計情報", "lbl_total_c": "活動ログの総行数", "lbl_total_u": "登録ユーザー総数",
        "lbl_tema_aktif": "現在アクティブなシステムウェブテーマ", "lbl_live_log": "### ⏱️ ライブログ: ログインおよび新規登録の履歴", "lbl_info_log": "テーブルには、最新の項目から順にリアルタイムの動的ログが表示されます。",
        "msg_log_kosong": "記録されたアクティビティ履歴はまだありません。", "lbl_intip_db": "### 🔍 生のデータベースファイルを確認", "lbl_daftar_pengguna": "### 📋 登録ユーザー一覧",
        "lbl_edit_akun_title": "### ✏️ アカウントデータの編集 (Gmail、パスワード、権限)", "lbl_pilih_u_edit": "編集するユーザー名を選択してください:", "lbl_ubah_gmail": "Gmailの変更:",
        "lbl_ubah_pass": "パスワードの変更:", "lbl_ubah_role": "アクセス権限 (Role) の変更:", "btn_simpan_akun": "アカウントの変更を保存",
        "msg_edit_u_sukses": "✏️ アカウント情報が正常に保存されました！", "msg_edit_u_gagal": "❌ 更新失敗！Gmailとパスワードは空にできません。",
        "lbl_pilih_tema_all": "すべてのユーザー端末に即座に反映させる公式ウェブテーマを選択:", "btn_terapkan_tema": "テーマをグローバルに適用する 🌍",
        "msg_tema_sukses": "🎨 テーマがウェブ全体にグローバル適用されました！", "msg_tema_gagal": "❌ 適用失敗！無効なテーマ選択です。",
        "lbl_buat_tema_kustom": "新しいカスタムテーマ名 (例: Sweet Pink 🌸):", "lbl_c_bg": "背景色の選択:",
        "lbl_c_side": "サイドバーの色の選択:", "lbl_c_txt": "メインテキストの色の選択:", "lbl_c_btn": "メインボタン（アクセント）の色の選択:",
        "lbl_c_card": "ギャラリーカード背景色の選択:", "btn_simpan_tema": "新しいテーマを保存", "msg_buat_t_gagal": "❌ 作成失敗！既に存在するテーマ名か、入力が空です。"
    },
    "Thailand (ไทย)": {
        "navigasi": "🧭 แถบนำทาง", "belum_login": "สถานะ: ยังไม่ได้ล็อกอิน", "logout": "ออกจากระบบ",
        "menu_akses": "🔐 เข้าสู่ระบบ", "pilih_menu": "เลือกเมนูเข้าใช้งาน:", "tab_masuk": "ล็อกอิน",
        "tab_daftar": "ลงทะเบียนบัญชีใหม่", "tab_lupa": "🔑 ลืมชื่อผู้ใช้ / รหัสผ่าน", "username": "ชื่อผู้ใช้:",
        "password": "รหัสผ่าน:", "btn_masuk": "เข้าสู่ระบบ", "err_login": "ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง!",
        "form_daftar": "แบบฟอร์มลงทะเบียน", "buat_user": "สร้างชื่อผู้ใช้ (ห้ามเว้นวรรค):", "masukan_email": "กรอก Gmail ของคุณ:",
        "buat_pass": "สร้างรหัสผ่านของคุณ:", "btn_daftar": "ลงทะเบียนตอนนี้", "err_user_ada": "ชื่อผู้ใช้นี้ถูกใช้งานแล้ว!",
        "sukses_daftar": "ลงทะเบียนสำเร็จ! กรุณาเข้าสู่ระบบ", "wajib_isi": "กรุณากรอกข้อมูลให้ครบทุกช่อง!",
        "bantuan_pulih": "ระบบกู้คืนบัญชีด่วน", "info_pulih": "กรอก Gmail ที่ลงทะเบียนไว้ ระบบจะค้นหาบัญชีของคุณ ย้ายกลับไปที่หน้าล็อกอิน และกรอกข้อมูลให้โดยอัตมัติทันที!",
        "btn_pulih": "กู้คืนบัญชี & ไปที่หน้าล็อกอิน", "err_email_salah": "Gmail ไม่ถูกต้อง! ไม่พบอีเมลนี้ในระบบ",
        "pilih_email_dulu": "กรุณากรอกอีเมลก่อน!", "galeri_title": "🎬 แกลเลอรีและบันทึกกิจกรรม",
        "filter_kat": "### 🔍 ตัวกรองหมวดหมู่", "pilih_jenis": "เลือกประเภทเอกสาร:", "semua": "ทั้งหมด",
        "catatan_saja": "เฉพาะบันทึกข้อความ", "foto": "รูปภาพ", "video": "วิดีโอ", "pilih_f_internal": "📁 เลือกโฟลเดอร์ในหมวดหมู่",
        "semua_folder": "ทุกโฟลเดอร์", "kosong": "ไม่มีบันทึกกิจกรรมในขณะนี้", "sisa_waktu": "⏳ **เวลาที่เหลือในการแสดง:**",
        "hari": "วัน", "jam": "ชั่วโมง", "menit": "นาที", "detik": "วินาที", "permanen": "📌 โพสต์ถาวร", "hanya_teks": "📌 เฉพาะบันทึกข้อความ (ไม่มีไฟล์แนบ)",
        "salin_share": "##### 🔗 คัดลอกข้อความเพื่อแชร์:", "tanggal": "วันที่", "detail": "รายละเอียด",
        "menu_1": "🎬 แกลเลอรีและบันทึกกิจกรรม", "menu_2": "➕ เพิ่มและลบบันทึก", "menu_3": "📁 จัดการโฟลเดอร์",
        "menu_4": "📊 แดชบอร์ดและระบบตรวจสอบบันทึก", "menu_5": "👥 จัดการผู้ใช้งาน & รหัสผ่าน", "menu_6": "🎨 ปรับแต่งธีมแผงควบคุม (ผู้ดูแล)", "pilih_hal": "เลือกหน้า:",
        "btn_refresh": "🔄 รีเฟรชหน้าเว็บ", "msg_refresh": "รีเฟรชหน้าเว็บสำเร็จแล้ว!", "halo": "สวัสดี", "toast_logout": "👋 ออกจากระบบสำเร็จแล้ว!",
        "toast_login_gagal": "❌ ล็อกอินไม่สำเร็จ! ตรวจสอบชื่อผู้ใช้และรหัสผ่านอีกครั้ง", "toast_reg_gagal": "❌ ลงทะเบียนไม่สำเร็จ! มีชื่อผู้ใช้นี้ในระบบแล้ว",
        "toast_reg_kosong": "⚠️ ลงทะเบียนไม่สำเร็จ! ห้ามปล่อยช่องว่างไว้", "toast_pulih_sukses": "พบบัญชีแล้ว! กรอกข้อมูลอัตโนมัติสำเร็จ",
        "toast_pulih_gagal": "❌ กู้คืนไม่สำเร็จ! ไม่พบอีเมลนี้ในระบบ", "toast_pulih_warning": "⚠️ จำเป็นต้องระบุข้อมูล! กรุณากรอก Gmail ก่อน",
        "download_btn": "📥 ดาวน์โหลด", "toast_dl": "📥 ดาวน์โหลดไฟล์สำเร็จแล้ว!", "toast_galeri_update": "อัปเดตคอลเลกชันแกลเลอรีเรียบร้อยแล้ว!",
        "admin_title_catatan": "🛠️ ศูนย์ควบคุมบันทึกข้อมูล (สิทธิ์ผู้ดูแลระบบ)", "tab_tambah_c": "➕ เพิ่มบันทึกใหม่", "tab_hapus_c": "🗑️ ลบบันทึกข้อมูล",
        "lbl_pilih_kat_dulu": "1. เลือกประเภทหมวดหมู่ก่อน:", "lbl_nama_keg": "ชื่อกิจกรรม/ข้อความบันทึก:", "lbl_folder": "โฟลเดอร์:",
        "lbl_upload_media": "อัปโหลดสื่อไฟล์ (เลือกได้หลายไฟล์พร้อมกัน):", "lbl_durasi_tampil": "### ⏱️ ตั้งค่าเวลาในการแสดงผลเนื้อหา",
        "lbl_jadikan_perm": "กำหนดให้โพสต์นี้เป็นแบบถาวร (แสดงตลอดเวลา)", "btn_publikasi": "เผยแพร่ข้อมูล", "msg_proses_upload": "⏳ กำลังประมวลผลและอัปโหลดสื่อไฟล์ทั้งหมดของคุณ...",
        "msg_upload_sukses": "✅ เผยแพร่ไฟล์ทั้งหมดเสร็จสมบูรณ์เรียบร้อยแล้ว!", "toast_form_bersih": "🚀 ล้างข้อมูลฟอร์มโดยอัตโนมัติ!", "msg_upload_gagal": "❌ เผยแพร่ไม่สำเร็จ! จำเป็นต้องระบุชื่อกิจกรรม",
        "lbl_pilih_hapus_c": "เลือกบันทึกที่ต้องการลบ:", "btn_hapus_perm": "ลบออกอย่างถาวร", "msg_hapus_sukses": "🗑️ ลบบันทึกออกจากระบบเรียบร้อยแล้ว!",
        "msg_hapus_gagal": "❌ ลบไม่สำเร็จ! บันทึกข้อมูลไม่ถูกต้อง", "lbl_buat_f_baru": "### สร้างโฟลเดอร์หมวดหมู่ใหม่", "lbl_nama_f_baru": "ชื่อโฟลเดอร์ใหม่:",
        "lbl_jenis_kat_f": "เลือกประเภทหมวดหมู่ของโฟลเดอร์:", "btn_buat_f": "สร้างโฟลเดอร์ทันที", "msg_f_sukses": "📁 สร้างโฟลเดอร์ใหม่เรียบร้อยแล้ว!",
        "msg_f_gagal_kosong": "⚠️ สร้างไม่สำเร็จ! ชื่อโฟลเดอร์ห้ามเป็นช่องว่าง", "lbl_hapus_f_title": "### ลบโฟลเดอร์หมวดหมู่",
        "lbl_f_warning": "🚨 คำเตือน: การลบโฟลเดอร์จะลบไฟล์สื่อทั้งหมดที่อยู่ภายในนั้นอย่างถาวร!", "lbl_pilih_f_hapus": "เลือกโฟลเดอร์ที่จะลบอย่างถาวร:",
        "btn_hapus_f_perm": "ลบโฟลเดอร์อย่างถาวร", "msg_proses_hapus_f": "⏳ กำลังลบโฟลเดอร์และเนื้อหาทั้งหมด...",
        "msg_hapus_f_sukses": "🗑️ ทำลายโฟลเดอร์ออกจากเซิร์ฟเวอร์เสร็จสมบูรณ์!", "msg_hapus_f_gagal": "❌ ลบโฟลเดอร์ไม่สำเร็จ!", "msg_no_f_kustom": "ไม่มีโฟลเดอร์ที่กำหนดเองที่สามารถลบได้",
        "lbl_stats": "### 📈 สถิติการจัดเก็บข้อมูล", "lbl_total_c": "แถวล็อกข้อมูลบันทึกกิจกรรมทั้งหมด", "lbl_total_u": "ผู้ใช้ระบบทั้งหมด",
        "lbl_tema_aktif": "ธีมหลักของเว็บไซต์ที่ใช้งานอยู่", "lbl_live_log": "### ⏱️ Live Log: ประวัติการล็อกอินและการลงทะเบียน", "lbl_info_log": "ตารางแสดงวันและเวลาแบบเรียลไทม์ เรียงลำดับจากใหม่ล่าสุดไปเก่าที่สุด:",
        "msg_log_kosong": "ยังไม่มีประวัติกิจกรรมถูกบันทึกไว้ในระบบ", "lbl_intip_db": "### 🔍 ตรวจสอบฐานข้อมูลดิบ", "lbl_daftar_pengguna": "### 📋 รายชื่อผู้ใช้ที่ลงทะเบียนแล้ว",
        "lbl_edit_akun_title": "### ✏️ แก้ไขข้อมูลบัญชี (Gmail, รหัสผ่าน & สิทธิ์เข้าถึง)", "lbl_pilih_u_edit": "เลือกชื่อผู้ใช้ที่ต้องการแก้ไข:", "lbl_ubah_gmail": "เปลี่ยน Gmail:",
        "lbl_ubah_pass": "เปลี่ยนรหัสผ่าน:", "lbl_ubah_role": "เปลี่ยนระดับสิทธิ์เข้าถึง (Role):", "btn_simpan_akun": "บันทึกการเปลี่ยนแปลงบัญชี",
        "msg_edit_u_sukses": "✏️ บันทึกการเปลี่ยนแปลงบัญชีผู้ใช้เรียบร้อยแล้ว!", "msg_edit_u_gagal": "❌ อัปเดตไม่สำเร็จ! Gmail และรหัสผ่านห้ามเว้นว่าง",
        "lbl_pilih_tema_all": "เลือกธีมที่ต้องการปรับใช้บนหน้าจอของผู้ใช้ทุกคนทันที:", "btn_terapkan_tema": "ปรับใช้ธีมทั่วทั้งเว็บไซต์ 🌍",
        "msg_tema_sukses": "🎨 ปรับใช้ธีมพร้อมกันทั่วทั้งระบบสำเร็จแล้ว!", "msg_tema_gagal": "❌ ปรับใช้ไม่สำเร็จ! ตัวเลือกธีมไม่ถูกต้อง",
        "lbl_buat_tema_kustom": "ชื่อธีมใหม่ (ตัวอย่าง: Sweet Pink 🌸):", "lbl_c_bg": "เลือกสีพื้นหลัง (Background):",
        "lbl_c_side": "เลือกสีแถบเมนูด้านข้าง:", "lbl_c_txt": "เลือกสีข้อความหลัก:", "lbl_c_btn": "เลือกสีปุ่มกดหลัก (Accent Color):",
        "lbl_c_card": "เลือกสีกล่องการ์ดแกลเลอรี (Card):", "btn_simpan_tema": "บันทึกธีมใหม่", "msg_buat_t_gagal": "❌ สร้างไม่สำเร็จ! มีชื่อธีมนี้อยู่แล้วหรือปล่อยว่างไว้"
    },
    "Philippines (Tagalog)": {
        "navigasi": "🧭 Nabigasyon", "belum_login": "Status: Hindi pa Naka-log in", "logout": "Mag-log Out",
        "menu_akses": "🔐 Access sa System", "pilih_menu": "Pumili ng Menu:", "tab_masuk": "Mag-log In",
        "tab_daftar": "Magrehistro ng Bagong Account", "tab_lupa": "🔑 Nakalimutan ang Username / Password", "username": "Username:",
        "password": "Password:", "btn_masuk": "Mag-log In", "err_login": "Maling Username o Password!",
        "form_daftar": "Form ng Pagpaparehistro", "buat_user": "Gumawa ng Username (Walang Espasyo):", "masukan_email": "Ilagay ang iyong Gmail:",
        "buat_pass": "Gumawa ng iyong Password:", "btn_daftar": "Magrehistro Ngayon", "err_user_ada": "Ang Username ay nakarehistro na!",
        "sukses_daftar": "Matagumpay ang pagpaparehistro! Mangyaring mag-log in.", "wajib_isi": "Lahat ng patlang ay kinakailangan!",
        "bantuan_pulih": "Tulong sa Instant na Pagbawi ng Account", "info_pulih": "Ilagay ang iyong nakarehistrong Gmail. Hahanapin ng system ang iyong account, awtomatikong ire-redirect ka sa login page, at i-autofill ang iyong mga kredensyal!",
        "btn_pulih": "Bawiin ang Account & Pumunta sa Log In", "err_email_salah": "Di-wastong Gmail! Ang email na ito ay hindi nakarehistro.",
        "pilih_email_dulu": "Mangyaring ilay muna ang iyong email!", "galeri_title": "🎬 Aktibong Gallery at mga Tala",
        "filter_kat": "### 🔍 Filter ng Kategorya", "pilih_jenis": "Pumili ng Uri ng Dokumentasyon:", "semua": "Lahat",
        "catatan_saja": "Mga Tala lamang", "foto": "Mga Larawan", "video": "Mga Video", "pilih_f_internal": "📁 Pumili ng Folder sa loob ng Kategorya",
        "semua_folder": "Lahat ng Folder", "kosong": "Walang aktibong mga tala sa kasalukuyan.", "sisa_waktu": "⏳ **Natitirang Oras ng Display:**",
        "hari": "Araw", "jam": "Oras", "menit": "Minuto", "detik": "Segundo", "permanen": "📌 Permanenteng Post", "hanya_teks": "📌 Tala ng Teksto Lamang (Walang File)",
        "salin_share": "##### 🔗 Kopyahin ang Tala para Ibahagi:", "tanggal": "Petsa", "detail": "Detalyadong Paglalarawan",
        "menu_1": "🎬 Aktibong Gallery at mga Tala", "menu_2": "➕ Magdagdag at Magbura ng Tala", "menu_3": "📁 Pamamahala ng Folder",
        "menu_4": "📊 Dashboard at Pagsubaybay sa Database", "menu_5": "👥 Pamamahala ng User at Password", "menu_6": "🎨 Pamamahala ng Tema (Admin)", "pilih_hal": "Pumili ng Pahina:",
        "btn_refresh": "🔄 I-refresh ang Pahina", "msg_refresh": "Matagumpay na nai-refresh ang pahina!", "halo": "Kamusta", "toast_logout": "👋 Matagumpay na naka-log out!",
        "toast_login_gagal": "❌ Sawi ang Pag-log in! Suriin ang Username at Password.", "toast_reg_gagal": "❌ Sawi ang Pagrehistro! May gumagamit na sa username.",
        "toast_reg_kosong": "⚠️ Sawi ang Pagrehistro! May bakanteng patlang.", "toast_pulih_sukses": "Nahanap ang account! Awtomatikong pinunan ang mga patlang.",
        "toast_pulih_gagal": "❌ Sawi ang Pagbawi! Hindi nakarehistro ang Gmail.", "toast_pulih_warning": "⚠️ Kailangan ng Input! Ilagay muna ang Gmail.",
        "download_btn": "📥 I-download", "toast_dl": "📥 Matagumpay na nai-download ang file!", "toast_galeri_update": "Nai-update ang gallery!",
        "admin_title_catatan": "🛠️ Control Center ng mga Tala (Akses ng Admin)", "tab_tambah_c": "➕ Magdagdag ng Bagong Tala", "tab_hapus_c": "🗑️ Burahin ang Tala",
        "lbl_pilih_kat_dulu": "1. Pumili muna ng Uri ng Kategorya:", "lbl_nama_keg": "Pangalan ng Aktibidad/Tala:", "lbl_folder": "Folder:",
        "lbl_upload_media": "I-upload ang Media (Maaaring maramihang file):", "lbl_durasi_tampil": "### ⏱️ Itakda ang Tagal ng Display ng Nilalaman",
        "lbl_jadikan_perm": "Gawing Permanente ang Post na Ito (Palaging Ipakita)", "btn_publikasi": "I-publish", "msg_proses_upload": "⏳ Pinoproseso at ina-upload ang iyong mga file...",
        "msg_upload_sukses": "✅ Matagumpay na nai-publish ang lahat ng file!", "toast_form_bersih": "🚀 Awtomatikong nilinis ang form!", "msg_upload_gagal": "❌ Sawi ang Pag-publish! Kailangan ang pangalan.",
        "lbl_pilih_hapus_c": "Pumili ng Tala na Buruburahin:", "btn_hapus_perm": "Burahin nang Permanente", "msg_hapus_sukses": "🗑️ Matagumpay na nabura ang tala sa system!",
        "msg_hapus_gagal": "❌ Sawi ang Pagbura! Di-wastong tala.", "lbl_buat_f_baru": "### Gumawa ng Bagong Folder ng Kategorya", "lbl_nama_f_baru": "Pangalan ng Bagong Folder:",
        "lbl_jenis_kat_f": "Pumili ng Uri ng Kategorya ng Folder:", "btn_buat_f": "Gumawa ng Folder Ngayon", "msg_f_sukses": "📁 Matagumpay na nakagawa ng bagong folder!",
        "msg_f_gagal_kosong": "⚠️ Sawi ang Paggawa! Hindi maaaring bakante ang pangalan ng folder.", "lbl_hapus_f_title": "### Burahin ang Folder ng Kategorya",
        "lbl_f_warning": "🚨 BABALA: Ang pagbura sa folder ay PERMANENTENG mag-aalis sa LAHAT NG FILE NG MEDIA sa loob nito!", "lbl_pilih_f_hapus": "Pumili ng Folder na Buruburahin nang Permanente:",
        "btn_hapus_f_perm": "Burahin ang Folder nang Permanente", "msg_proses_hapus_f": "⏳ Binubura ang folder at ang mga laman nito...",
        "msg_hapus_f_sukses": "🗑️ Matagumpay na winasak ang folder mula sa server!", "msg_hapus_f_gagal": "❌ Sawi sa pagbura ng folder!", "msg_no_f_kustom": "Walang magagamit na custom folder para burahin.",
        "lbl_stats": "### 📈 Estadistika ng Storage", "lbl_total_c": "Kabuuan ng mga Hilera ng Tala", "lbl_total_u": "Kabuuan ng mga User ng System",
        "lbl_tema_aktif": "Aktibong Global Web Theme", "lbl_live_log": "### ⏱️ Live Log: Kasaysayan ng Log-in at Pagrehistro", "lbl_info_log": "Ipinapakita ng talahanayan ang petsa at oras na nakaayos mula sa pinakabago:",
        "msg_log_kosong": "Wala pang naitalang kasaysayan ng aktibidad.", "lbl_intip_db": "### 🔍 Siyasatin ang Raw Files ng Database", "lbl_daftar_pengguna": "### 📋 Listahan ng mga Nakarehistrong User",
        "lbl_edit_akun_title": "### ✏️ I-edit ang Detalye ng Account (Gmail, Password at Role)", "lbl_pilih_u_edit": "Pumili ng Username na I-eedit:", "lbl_ubah_gmail": "Baguhin ang Gmail:",
        "lbl_ubah_pass": "Baguhin ang Password:", "lbl_ubah_role": "Baguhin ang Role:", "btn_simpan_akun": "I-save ang mga Pagbabago",
        "msg_edit_u_sukses": "✏️ Matagumpay na nai-save ang mga pagbabago sa account!", "msg_edit_u_gagal": "❌ Sawi ang Pag-update! Hindi maaaring bakante ang Gmail at Password.",
        "lbl_pilih_tema_all": "Pumili ng tema na ilalapat agad sa lahat ng user:", "btn_terapkan_tema": "Ilapat ang Tema sa Buong Web 🌍",
        "msg_tema_sukses": "🎨 Matagumpay na nailapat ang tema sa buong system!", "msg_tema_gagal": "❌ Sawi sa Paglapat! Di-wastong pagpili ng tema.",
        "lbl_buat_tema_kustom": "Pangalan ng Bagong Tema (Hal., Sweet Pink 🌸):", "lbl_c_bg": "Pumili ng Kulay ng Background:",
        "lbl_c_side": "Pumili ng Kulay ng Sidebar sa Gilid:", "lbl_c_txt": "Pumili ng Kulay ng Pangunahing Teksto:", "lbl_c_btn": "Pumili ng Kulay ng Pangunahing Button (Accent):",
        "lbl_c_card": "Pumili ng Kulay ng Gallery Card:", "btn_simpan_tema": "I-save ang Bagong Tema", "msg_buat_t_gagal": "❌ Sawi ang Paglikha! Ang pangalan ng tema ay umiiral na o bakante."
    },
    "Taiwan (繁體中文)": {
        "navigasi": "🧭 導覽功能", "belum_login": "狀態: 未登入", "logout": "登出系統",
        "menu_akses": "🔐 系統安全登入", "pilih_menu": "選擇功能選單:", "tab_masuk": "使用者登入",
        "tab_daftar": "註冊新帳號", "tab_lupa": "🔑 忘記帳號或密碼", "username": "使用者名稱:",
        "password": "密碼:", "btn_masuk": "登入", "err_login": "使用者名稱或密碼錯誤！",
        "form_daftar": "新用戶註冊表單", "buat_user": "建立用戶名稱 (不可包含空格):", "masukan_email": "輸入您的 Gmail 帳號:",
        "buat_pass": "建立您的密碼:", "btn_daftar": "立即註冊", "err_user_ada": "此用戶名稱已被註冊！",
        "sukses_daftar": "註冊成功！請返回登入。", "wajib_isi": "所有欄位皆為必填項目！",
        "bantuan_pulih": "即時帳戶自主修復協助", "info_pulih": "輸入您註冊的 Gmail。系統將自動比對資料庫，成功後會直接引導回登入頁面並自動帶入您的帳密！",
        "btn_pulih": "修復帳戶並前往登入", "err_email_salah": "無效的 Gmail！此信箱尚未在本系統註冊。",
        "pilih_email_dulu": "請先輸入您的電子郵件！", "galeri_title": "🎬 動態藝廊與即時筆記",
        "filter_kat": "### 🔍 分類篩選器", "pilih_jenis": "選取檔案類型:", "semua": "顯示全部",
        "catatan_saja": "僅顯示文字筆記", "foto": "相片紀錄", "video": "影片紀錄", "pilih_f_internal": "📁 選擇分類底下的專屬資料夾",
        "semua_folder": "所有資料夾", "kosong": "目前沒有任何有效的動態筆記內容。", "sisa_waktu": "⏳ **剩餘顯示時間:**",
        "hari": "天", "jam": "小時", "menit": "分鐘", "detik": "秒", "permanen": "📌 永久告示物", "hanya_teks": "📌 僅純文字內容 (無附加多媒體檔案)",
        "salin_share": "##### 🔗 複製文本內容以便分享:", "tanggal": "活動日期", "detail": "詳細說明備註",
        "menu_1": "🎬 動態藝廊與即時筆記", "menu_2": "➕ 新增與刪除動態筆記", "menu_3": "📁 分類資料夾控制中心",
        "menu_4": "📊 數據主控台與實時日誌監控", "menu_5": "👥 用戶權限與密碼管理中心", "menu_6": "🎨 GUI 全局網頁視覺主題 (管理員專屬)", "pilih_hal": "選擇頁面:",
        "btn_refresh": "🔄 重新整理頁面", "msg_refresh": "頁面重新整理成功！", "halo": "您好", "toast_logout": "👋 成功登出系統！",
        "toast_login_gagal": "❌ 登入失敗！請重新檢查帳號與密碼。", "toast_reg_gagal": "❌ 註冊失敗！此使用者名稱已被使用。",
        "toast_reg_kosong": "⚠️ 註冊失敗！欄位不可為空。", "toast_pulih_sukses": "找到帳號！已自動填入資料。",
        "toast_pulih_gagal": "❌ 修復失敗！該 Gmail 未註冊。", "toast_pulih_warning": "⚠️ 需要輸入！請先填寫 Gmail。",
        "download_btn": "📥 下載", "toast_dl": "📥 檔案下載成功！", "toast_galeri_update": "藝廊內容已更新！",
        "admin_title_catatan": "🛠️ 筆記控制中心 (管理員權限)", "tab_tambah_c": "➕ 新增動態筆記", "tab_hapus_c": "🗑️ 刪除動態筆記",
        "lbl_pilih_kat_dulu": "1. 請先選擇檔案類型:", "lbl_nama_keg": "活動名稱/筆記備註:", "lbl_folder": "專屬資料夾:",
        "lbl_upload_media": "上傳多媒體檔案 (支援選取多個檔案):", "lbl_durasi_tampil": "### ⏱️ 設定內容動態顯示時間",
        "lbl_jadikan_perm": "將此貼文設定為永久告示 (始終顯示)", "btn_publikasi": "發布動態", "msg_proses_upload": "⏳ 正在處理並上傳您的多媒體檔案...",
        "msg_upload_sukses": "✅ 所有檔案已成功發布！", "toast_form_bersih": "🚀 表單內容已自動清除！", "msg_upload_gagal": "❌ 發布失敗！活動名稱為必填。",
        "lbl_pilih_hapus_c": "選擇欲刪除的動態筆記:", "btn_hapus_perm": "永久刪除", "msg_hapus_sukses": "🗑️ 該筆記已成功自系統移除！",
        "msg_hapus_gagal": "❌ 刪除失敗！無效的筆記內容。", "lbl_buat_f_baru": "### 建立新分類資料夾", "lbl_nama_f_baru": "新資料夾名稱:",
        "lbl_jenis_kat_f": "選取資料夾專屬檔案分類:", "btn_buat_f": "立即建立資料夾", "msg_f_sukses": "📁 新資料夾建立成功！",
        "msg_f_gagal_kosong": "⚠️ 建立失敗！資料夾名稱不可為空。", "lbl_hapus_f_title": "### 刪除分類資料夾",
        "lbl_f_warning": "🚨 警告: 刪除資料夾將會永久移除該資料夾底下的「所有媒體檔案」！", "lbl_pilih_f_hapus": "選擇欲永久刪除的資料夾:",
        "btn_hapus_f_perm": "永久刪除資料夾", "msg_proses_hapus_f": "⏳ 正在清除資料夾及其所有內部檔案...",
        "msg_hapus_f_sukses": "🗑️ 資料夾已成功自伺服器端銷毀！", "msg_hapus_f_gagal": "❌ 無法刪除資料夾！", "msg_no_f_kustom": "目前沒有自訂資料夾可供刪除。",
        "lbl_stats": "### 📈 系統儲存數據數據", "lbl_total_c": "活動筆記資料庫總行數", "lbl_total_u": "系統註冊用戶總數",
        "lbl_tema_aktif": "當前全局活動網頁視覺主題", "lbl_live_log": "### ⏱️ 即時動態日誌: 登入與註冊歷史紀錄", "lbl_info_log": "表格顯示即時動態時間戳記，依最新順序排序：",
        "msg_log_kosong": "目前尚無任何系統活動紀錄。", "lbl_intip_db": "### 🔍 檢視原始資料庫檔案", "lbl_daftar_pengguna": "### 📋 已註冊用戶清單",
        "lbl_edit_akun_title": "### ✏️ 修改用戶帳戶資料 (Gmail, 密碼 與 權限)", "lbl_pilih_u_edit": "選擇欲編輯的用戶名稱:", "lbl_ubah_gmail": "修改 Gmail:",
        "lbl_ubah_pass": "修改 密碼:", "lbl_ubah_role": "修改 系統控制權限 (Role):", "btn_simpan_akun": "儲存帳戶權限變更",
        "msg_edit_u_sukses": "✏️ 帳戶權限與變更已成功儲存！", "msg_edit_u_gagal": "❌ 更新失敗！Gmail與密碼欄位不可為空。",
        "lbl_pilih_tema_all": "選擇欲套用至所有使用者裝置的網頁視覺主題:", "btn_terapkan_tema": "全局套用網頁主題 🌍",
        "msg_tema_sukses": "🎨 網頁視覺主題已全局套用成功！", "msg_tema_gagal": "❌ 套用失敗！無效的主題選擇。",
        "lbl_buat_tema_kustom": "建立新視覺主題名稱 (例如: Sweet Pink 🌸):", "lbl_c_bg": "選取背景底色 (Background):",
        "lbl_c_side": "選取側邊控制欄顏色:", "lbl_c_txt": "選取全局主要文字顏色:", "lbl_c_btn": "選取主要按鈕顏色 (Accent):",
        "lbl_c_card": "選取藝廊區塊背景顏色 (Card):", "btn_simpan_tema": "儲存新視覺主題", "msg_buat_t_gagal": "❌ 建立失敗！視覺主題名稱已存在或為空值。"
    }
}

# --- DETEKSI BAHASA OTOMATIS BERDASARKAN DEVICE ---
if "bahasa_pilihan" not in st.session_state:
    try:
        kode_lang = st_javascript("navigator.language || navigator.userLanguage;")
        kode_clean = str(kode_lang).lower()
        if kode_clean.startswith("id"): st.session_state.bahasa_pilihan = "Indonesia"
        elif kode_clean.startswith("zh-tw") or kode_clean.startswith("zh-hk"): st.session_state.bahasa_pilihan = "Taiwan (繁體中文)"
        elif kode_clean.startswith("zh"): st.session_state.bahasa_pilihan = "China (中文)"
        elif kode_clean.startswith("es"): st.session_state.bahasa_pilihan = "Spanyol (Español)"
        elif kode_clean.startswith("pt"): st.session_state.bahasa_pilihan = "Brazil (Português)"
        elif kode_clean.startswith("ko"): st.session_state.bahasa_pilihan = "Korea (한국어)"
        elif kode_clean.startswith("ja"): st.session_state.bahasa_pilihan = "Jepang (日本語)"
        elif kode_clean.startswith("th"): st.session_state.bahasa_pilihan = "Thailand (ไทย)"
        elif kode_clean.startswith("tl") or kode_clean.startswith("fil"): st.session_state.bahasa_pilihan = "Philippines (Tagalog)"
        else: st.session_state.bahasa_pilihan = "English"
    except:
        st.session_state.bahasa_pilihan = "Indonesia"

# --- SISTEM LOGIN STATE ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = "Belum Login"

if "autofill_user" not in st.session_state: st.session_state.autofill_user = ""
if "autofill_pass" not in st.session_state: st.session_state.autofill_pass = ""
if "indeks_tab" not in st.session_state: st.session_state.indeks_tab = 0

# Ekstrak objek kamus aktif agar otomatis sinkron secara realtime global
txt = KAMUS.get(st.session_state.bahasa_pilihan, KAMUS["Indonesia"])

# --- SIDEBAR ATAS: NAVIGASI ---
st.sidebar.title(txt["navigasi"])

lang_list = list(KAMUS.keys())
idx_lang = lang_list.index(st.session_state.bahasa_pilihan) if st.session_state.bahasa_pilihan in lang_list else 0
pilih_lang_manual = st.sidebar.selectbox("🌐 Language / Bahasa:", lang_list, index=idx_lang)
if pilih_lang_manual != st.session_state.bahasa_pilihan:
    st.session_state.bahasa_pilihan = pilih_lang_manual
    st.toast(f"Language changed to {pilih_lang_manual}", icon="🌐")
    st.rerun()

# --- AMBIL TEMA GLOBAL ---
df_tema_all = baca_tema()
nama_tema_wajib = ambil_tema_aktif_sistem()

if nama_tema_wajib not in df_tema_all["Nama_Tema"].values:
    nama_tema_wajib = df_tema_all["Nama_Tema"].iloc[0]
    set_tema_aktif_sistem(nama_tema_wajib)

data_tema_terpilih = df_tema_all[df_tema_all["Nama_Tema"] == nama_tema_wajib].iloc[0]

# --- SUNTIKAN CSS KUSTOM ---
css_kustom = f"""
<style>
    .stApp {{ background-color: {data_tema_terpilih['Bg_Color']} !important; color: {data_tema_terpilih['Text_Color']} !important; }}
    [data-testid="stSidebar"] {{ background-color: {data_tema_terpilih['Sidebar_Color']} !important; }}
    h1, h2, h3, h4, h5, h6, p, label, .stMarkdown, span, .stRadio label {{ color: {data_tema_terpilih['Text_Color']} !important; }}
    button[kind="secondary"], button[kind="primary"] {{ background-color: {data_tema_terpilih['Button_Color']} !important; color: #ffffff !important; border-radius: 8px !important; border: none !important; }}
    div[data-testid="stVerticalBlockBorderWrapper"] {{ background-color: {data_tema_terpilih['Card_Bg']} !important; border: 1px solid {data_tema_terpilih['Button_Color']} !important; border-radius: 12px !important; padding: 15px !important; }}
</style>
"""
st.markdown(css_kustom, unsafe_allow_html=True)
st.sidebar.markdown("---")

if st.session_state.logged_in:
    st.sidebar.success(f"{txt['halo']}, {st.session_state.username} ({st.session_state.role})")
    if st.sidebar.button(txt["logout"]):
        catat_log(st.session_state.username, "Log Out", "Pengguna keluar dari aplikasi.")
        st.session_state.logged_in = False; st.session_state.username = ""; st.session_state.role = "Belum Login"
        st.session_state.autofill_user = ""; st.session_state.autofill_pass = ""
        st.session_state.indeks_tab = 0
        st.toast(txt["toast_logout"], icon="👋")
        st.rerun()
else:
    st.sidebar.info(txt["belum_login"])

pilihan_menu = []
if not st.session_state.logged_in:
    pilihan_menu = [txt["tab_masuk"] + " / " + txt["tab_daftar"]]
else:
    pilihan_menu.append(txt["menu_1"])
    if st.session_state.role == "Admin":
        pilihan_menu.append(txt["menu_2"])
        pilihan_menu.append(txt["menu_3"])
        pilihan_menu.append(txt["menu_6"]) 
        pilihan_menu.append(txt["menu_4"])
        pilihan_menu.append(txt["menu_5"])

menu = st.sidebar.selectbox(txt["pilih_hal"], pilihan_menu)

# --- HALAMAN: LOG IN / DAFTAR AKUN ---
if menu == (txt["tab_masuk"] + " / " + txt["tab_daftar"]):
    st.title(txt["menu_akses"])
    
    if st.button(txt["btn_refresh"], key="ref_akses"): 
        st.toast(txt["msg_refresh"], icon="🔄")
        st.rerun()
        
    pilihan_tab = [txt["tab_masuk"], txt["tab_daftar"], txt["tab_lupa"]]
    tab_terpilih = st.radio(txt["pilih_menu"], pilihan_tab, index=st.session_state.indeks_tab, horizontal=True)
    st.markdown("---")
    
    if tab_terpilih == txt["tab_masuk"]:
        st.session_state.indeks_tab = 0
        input_user = st.text_input(txt["username"], value=st.session_state.autofill_user)
        input_pass = st.text_input(txt["password"], type="password", value=st.session_state.autofill_pass)
        if st.button(txt["btn_masuk"]):
            df_users = baca_users()
            user_cocok = df_users[(df_users['username'] == input_user) & (df_users['password'] == input_pass)]
            if not user_cocok.empty:
                st.session_state.logged_in = True
                st.session_state.username = input_user
                st.session_state.role = user_cocok.iloc[0]['role']
                catat_log(input_user, "Log In", f"Berhasil masuk sistem sebagai {st.session_state.role}")
                st.toast(f"🎉 {txt['halo']}, {input_user}!", icon="✅")
                st.rerun()
            else: 
                st.error(txt["err_login"])
                st.toast(txt["toast_login_gagal"], icon="❌")
                
    elif tab_terpilih == txt["tab_daftar"]:
        st.session_state.indeks_tab = 1
        reg_user = st.text_input(txt["buat_user"])
        reg_gmail = st.text_input(txt["masukan_email"])
        reg_pass = st.text_input(txt["buat_pass"], type="password")
        if st.button(txt["btn_daftar"]):
            if reg_user and reg_gmail and reg_pass:
                df_users = baca_users()
                if reg_user in df_users['username'].values: 
                    st.error(txt["err_user_ada"])
                    st.toast(txt["toast_reg_gagal"], icon="⚠️")
                else:
                    df_users = pd.concat([df_users, pd.DataFrame([{"username": reg_user, "email": reg_gmail, "password": reg_pass, "role": "User"}])], ignore_index=True)
                    simpan_users(df_users)
                    catat_log(reg_user, "Pendaftaran Akun Baru", f"Mendaftar menggunakan Gmail: {reg_gmail}")
                    st.success(txt["sukses_daftar"])
                    st.toast("💚 Account Created!", icon="💚")
            else: 
                st.error(txt["wajib_isi"])
                st.toast(txt["toast_reg_kosong"], icon="🛑")

    elif tab_terpilih == txt["tab_lupa"]:
        st.session_state.indeks_tab = 2
        input_email_pulih = st.text_input(txt["masukan_email"]).strip()
        if st.button(txt["btn_pulih"]):
            if input_email_pulih:
                df_users = baca_users()
                user_ditemukan = df_users[df_users['email'].str.strip() == input_email_pulih]
                if not user_ditemukan.empty:
                    st.session_state.autofill_user = user_ditemukan.iloc[0]['username']
                    st.session_state.autofill_pass = user_ditemukan.iloc[0]['password']
                    catat_log(st.session_state.autofill_user, "Pemulihan Akun", f"Melakukan pencarian password via Gmail.")
                    st.toast(txt["toast_pulih_sukses"], icon="🔑")
                    st.session_state.indeks_tab = 0; st.rerun()
                else: 
                    st.error(txt["err_email_salah"])
                    st.toast(txt["toast_pulih_gagal"], icon="❌")
            else: 
                st.warning(txt["pilih_email_dulu"])
                st.toast(txt["toast_pulih_warning"], icon="📝")

# --- HALAMAN 1: CATATAN AKTIF ---
elif menu == txt["menu_1"]:
    st.title(txt["galeri_title"])
    
    if st.button(txt["btn_refresh"], key="ref_h1"): 
        st.toast(txt["toast_galeri_update"], icon="🔄")
        st.rerun()
        
    df_kegiatan = baca_kegiatan()
    st.markdown(txt["filter_kat"])
    
    # Menyamakan value radio agar tetap sinkron saat bahasa berganti
    media_pilihan = st.radio(txt["pilih_jenis"], [txt["semua"], txt["catatan_saja"], txt["foto"], txt["video"]], horizontal=True)
    pilihan_clean = "Semua"
    if media_pilihan == txt["catatan_saja"]: pilihan_clean = "Catatan saja"
    elif media_pilihan == txt["foto"]: pilihan_clean = "Foto"
    elif media_pilihan == txt["video"]: pilihan_clean = "Video"
    
    folder_pilihan = "Semua Folder"
    if pilihan_clean in ["Foto", "Video"]:
        list_folder_filter = ambil_daftar_folder("Foto" if pilihan_clean == "Foto" else "Video")
        folder_pilihan = st.selectbox(f"{txt['pilih_f_internal']}:", [txt["semua_folder"]] + list_folder_filter)
        
    st.markdown("---")
    if df_kegiatan.empty:
        st.info(txt["kosong"])
    else:
        waktu_sekarang = datetime.now(WIB).replace(tzinfo=None)
        ada_catatan_aktif = False
        for index, row in df_kegiatan.iterrows():
            # Filter Kategori Independen Bahasa
            row_kat = str(row["Kategori"])
            if pilihan_clean == "Catatan saja" and row_kat != "Catatan saja": continue
            if pilihan_clean == "Foto" and row_kat != "Foto": continue
            if pilihan_clean == "Video" and row_kat != "Video": continue
            
            if pilihan_clean in ["Foto", "Video"] and folder_pilihan != txt["semua_folder"]:
                if str(row.get("Folder", "Umum")) != folder_pilihan: continue
                    
            waktu_upload = datetime.strptime(row["Waktu_Upload"], "%Y-%m-%d %H:%M:%S")
            masa_berlaku_input = int(row["Masa_Berlaku_Menit"])
            
            is_permanen = (masa_berlaku_input >= 99999999)
            waktu_kadaluarsa = waktu_upload + timedelta(minutes=masa_berlaku_input)
            
            if is_permanen or (waktu_sekarang < waktu_kadaluarsa):
                ada_catatan_aktif = True
                
                with st.container(border=True):
                    col1, col2 = st.columns([1, 2])
                    file_path = row["File Dokumentasi"]
                    file_tersedia = pd.notna(file_path) and os.path.exists(str(file_path)) and str(file_path) != ""
                    
                    with col1:
                         if file_tersedia:
                             if row_kat == "Video": st.video(str(file_path))
                             else: st.image(str(file_path), use_container_width=True)
                             with open(str(file_path), "rb") as file_data:
                                 # Mengubah label teks kategori dinamis sesuai bahasa terpilih
                                 kat_label = txt["foto"] if row_kat == "Foto" else txt["video"]
                                 if st.download_button(label=f"{txt['download_btn']} {kat_label}", data=file_data, file_name=os.path.basename(str(file_path)), mime="video/mp4" if row_kat == "Video" else "image/jpeg", key=f"dl_{row['ID']}"):
                                     st.toast(txt["toast_dl"], icon="✅")
                         else: st.info(txt["hanya_teks"])
                             
                    with col2:
                        st.subheader(row["Nama Kegiatan"])
                        info_folder = f" | 📁 {txt['lbl_folder']} **{row.get('Folder', 'Umum')}**" if row_kat in ["Foto", "Video"] else ""
                        st.caption(f"📅 {txt['tanggal']}: {row['Tanggal']} | 🏷️ {txt['lbl_jenis_kat_f']}: **{txt['foto'] if row_kat == 'Foto' else (txt['video'] if row_kat == 'Video' else txt['catatan_saja'])}**{info_folder}")
                        
                        if is_permanen:
                            st.write(f"⏳ {txt['sisa_waktu']} {txt['permanen']}")
                        else:
                            sisa_waktu = waktu_kadaluarsa - waktu_sekarang
                            sisa_hari = sisa_waktu.days
                            sisa_jam = sisa_waktu.seconds // 3600
                            sisa_menit = (sisa_waktu.seconds % 3600) // 60
                            sisa_detik = sisa_waktu.seconds % 60
                            st.write(f"⏳ {txt['sisa_waktu']} {sisa_hari} {txt['hari']} {sisa_jam} {txt['jam']} {sisa_menit} {txt['menit']} {sisa_detik} {txt['detik']}")
                            
                        st.write(row["Detail"])
                        st.markdown(txt["salin_share"])
                        teks_bagikan = f"📢 *{row['Nama Kegiatan']}*\n📅 {txt['tanggal']}: {row['Tanggal']}\n📝 {txt['detail']}:\n{row['Detail']}"
                        st.code(teks_bagikan, language="text")
        if not ada_catatan_aktif: st.info(txt["kosong"])

# --- HALAMAN 2: INPUT & HAPUS CATATAN ---
elif menu == txt["menu_2"] and st.session_state.role == "Admin":
    st.title(txt["admin_title_catatan"])
    
    if st.button(txt["btn_refresh"], key="ref_h2"): 
        st.toast(txt["msg_refresh"], icon="🔄")
        st.rerun()
        
    tab_input, tab_hapus = st.tabs([txt["tab_tambah_c"], txt["tab_hapus_c"]])
    with tab_input:
        kat_terpilih = st.selectbox(txt["lbl_pilih_kat_dulu"], [txt["catatan_saja"], txt["foto"], txt["video"]])
        kat_clean = "Catatan saja"
        if kat_terpilih == txt["foto"]: kat_clean = "Foto"
        elif kat_terpilih == txt["video"]: kat_clean = "Video"
        
        with st.form("form_upload_catatan", clear_on_submit=False):
            name = st.text_input(txt["lbl_nama_keg"])
            folder_tujuan = st.selectbox(txt["lbl_folder"], ambil_daftar_folder(kat_clean)) if kat_clean in ["Foto", "Video"] else "Umum"
            detail = st.text_area(txt["detail"] + ":")
            
            uploaded_files = st.file_uploader(txt["lbl_upload_media"], type=["png", "jpg", "jpeg", "mp4"], accept_multiple_files=True)
            
            st.markdown(txt["lbl_durasi_tampil"])
            set_permanen = st.checkbox(txt["lbl_jadikan_perm"], value=False)
            
            disabled_inputs = True if set_permanen else False
            c_day, c_hr, c_min, c_sec = st.columns(4)
            with c_day: durasi_hari = st.number_input(txt["hari"]+":", min_value=0, value=1, disabled=disabled_inputs)
            with c_hr: durasi_jam = st.number_input(txt["jam"]+":", min_value=0, max_value=23, value=0, disabled=disabled_inputs)
            with c_min: durasi_menit = st.number_input(txt["menit"]+":", min_value=0, max_value=59, value=0, disabled=disabled_inputs)
            with c_sec: durasi_detik = st.number_input(txt["detik"]+":", min_value=0, max_value=59, value=0, disabled=disabled_inputs)
            
            submit_button = st.form_submit_button(txt["btn_publikasi"])
            
        if submit_button:
            if name:
                if set_permanen:
                    total_menit_simpan = 99999999
                else:
                    total_menit_simpan = (durasi_hari * 1440) + (durasi_jam * 60) + durasi_menit + (durasi_detik / 60.0)
                    if total_menit_simpan <= 0:
                        total_menit_simpan = 1
                
                with st.spinner(txt["msg_proses_upload"]):
                    df_k = baca_kegiatan()
                    waktu_skrg_wib = datetime.now(WIB)
                    
                    if not uploaded_files:
                        new_rec = {
                            "ID": str(int(waktu_skrg_wib.timestamp())), 
                            "Tanggal": waktu_skrg_wib.strftime("%Y-%m-%d"), 
                            "Nama Kegiatan": name, 
                            "Kategori": kat_clean, 
                            "Folder": folder_tujuan, 
                            "Detail": detail, 
                            "File Dokumentasi": "", 
                            "Waktu_Upload": waktu_skrg_wib.strftime("%Y-%m-%d %H:%M:%S"), 
                            "Masa_Berlaku_Menit": total_menit_simpan, 
                            "Oleh_Admin": st.session_state.username
                        }
                        df_k = pd.concat([df_k, pd.DataFrame([new_rec])], ignore_index=True)
                    
                    else:
                        for i, file_satuan in enumerate(uploaded_files):
                            timestamp_unik = int(waktu_skrg_wib.timestamp()) + i
                            nama_file_fisik = f"{timestamp_unik}_{file_satuan.name}"
                            file_path = os.path.join(FOLDER_UTAMA_MEDIA, kat_clean, folder_tujuan, nama_file_fisik)
                            
                            # Buat folder jika mendadak terhapus di server backend
                            os.makedirs(os.path.dirname(file_path), exist_ok=True)
                            with open(file_path, "wb") as f: 
                                f.write(file_satuan.getbuffer())
                            
                            nama_kegiatan_final = f"{name} ({i+1})" if len(uploaded_files) > 1 else name
                            
                            new_rec = {
                                "ID": str(timestamp_unik), 
                                "Tanggal": waktu_skrg_wib.strftime("%Y-%m-%d"), 
                                "Nama Kegiatan": nama_kegiatan_final, 
                                "Kategori": kat_clean, 
                                "Folder": folder_tujuan, 
                                "Detail": detail, 
                                "File Dokumentasi": file_path, 
                                "Waktu_Upload": waktu_skrg_wib.strftime("%Y-%m-%d %H:%M:%S"), 
                                "Masa_Berlaku_Menit": total_menit_simpan, 
                                "Oleh_Admin": st.session_state.username
                            }
                            df_k = pd.concat([df_k, pd.DataFrame([new_rec])], ignore_index=True)
                    
                    simpan_kegiatan(df_k)
                    catat_log(st.session_state.username, "Upload Kegiatan", f"Mengupload catatan baru multipel: '{name}'")
                    time.sleep(1)
                
                st.success(txt["msg_upload_sukses"])
                st.toast(txt["toast_form_bersih"], icon="🧼")
                st.rerun()
            else:
                st.error(txt["msg_upload_gagal"])

    with tab_hapus:
        df_hapus = baca_kegiatan()
        if df_hapus.empty: st.info(txt["kosong"])
        else:
            pilihan_hapus = st.selectbox(txt["lbl_pilih_hapus_c"], df_hapus["Nama Kegiatan"].tolist())
            if st.button(txt["btn_hapus_perm"]):
                if pilihan_hapus:
                    df_baru_hapus = df_hapus[df_hapus["Nama Kegiatan"] != pilihan_hapus]
                    simpan_kegiatan(df_baru_hapus)
                    catat_log(st.session_state.username, "Hapus Kegiatan", f"Menghapus catatan: '{pilihan_hapus}'")
                    
                    st.success(txt["msg_hapus_sukses"])
                    st.rerun()
                else:
                    st.error(txt["msg_hapus_gagal"])

# --- HALAMAN 3: MANAJEMEN FOLDER KATEGORI ---
elif menu == txt["menu_3"] and st.session_state.role == "Admin":
    st.title(txt["menu_3"])
    
    if st.button(txt["btn_refresh"], key="ref_h3"): 
        st.toast(txt["msg_refresh"], icon="🔄")
        st.rerun()
        
    tab_buat_f, tab_hapus_f = st.tabs([txt["tab_tambah_c"], txt["tab_hapus_c"]])
    
    with tab_buat_f:
        st.markdown(txt["lbl_buat_f_baru"])
        nama_f = st.text_input(txt["lbl_nama_f_baru"])
        kat_f = st.selectbox(txt["lbl_jenis_kat_f"], [txt["foto"], txt["video"]], key="kat_buat")
        kat_f_clean = "Foto" if kat_f == txt["foto"] else "Video"
        
        if st.button(txt["btn_buat_f"]):
            if nama_f:
                os.makedirs(os.path.join(PATH_FOTO if kat_f_clean == "Foto" else PATH_VIDEO, nama_f), exist_ok=True)
                catat_log(st.session_state.username, "Buat Folder", f"Membuat folder '{nama_f}' di kategori {kat_f_clean}")
                
                st.success(txt["msg_f_sukses"])
                st.rerun()
            else:
                st.warning(txt["msg_f_gagal_kosong"])
                
    with tab_hapus_f:
        st.markdown(txt["lbl_hapus_f_title"])
        st.warning(txt["lbl_f_warning"])
        
        kat_hapus = st.selectbox(txt["lbl_jenis_kat_f"], [txt["foto"], txt["video"]], key="kat_hapus")
        kat_hapus_clean = "Foto" if kat_hapus == txt["foto"] else "Video"
        list_folder_tersedia = ambil_daftar_folder(kat_hapus_clean)
        
        if "Umum" in list_folder_tersedia:
            list_folder_tersedia.remove("Umum")
            
        if not list_folder_tersedia:
            st.info(txt["msg_no_f_kustom"])
        else:
            folder_target_hapus = st.selectbox(txt["lbl_pilih_f_hapus"], list_folder_tersedia)
            
            if st.button(txt["btn_hapus_f_perm"], type="primary"):
                path_target_direktori = os.path.join(PATH_FOTO if kat_hapus_clean == "Foto" else PATH_VIDEO, folder_target_hapus)
                
                with st.spinner(txt["msg_proses_hapus_f"]):
                    try:
                        shutil.rmtree(path_target_direktori)
                        catat_log(st.session_state.username, "Hapus Folder", f"Menghapus folder kustom '{folder_target_hapus}' pada kategori {kat_hapus_clean}")
                        time.sleep(1)
                        
                        st.success(txt["msg_hapus_f_sukses"])
                        st.rerun()
                    except Exception as e:
                        st.error(f"{txt['msg_hapus_f_gagal']} Error: {str(e)}")

# --- HALAMAN 4: MONITORING DATABASE & LOG LIVE ---
elif menu == txt["menu_4"] and st.session_state.role == "Admin":
    st.title(txt["menu_4"])
    
    if st.button(txt["btn_refresh"], key="ref_h4"): 
        st.toast(txt["msg_refresh"], icon="🔄")
        st.rerun()
        
    df_keg = baca_kegiatan()
    df_us = baca_users()
    df_log_aktivitas = baca_log()
    
    st.markdown(txt["lbl_stats"])
    c1, c2, c3 = st.columns(3)
    with c1: st.metric(label=txt["lbl_total_c"], value=len(df_keg))
    with c2: st.metric(label=txt["lbl_total_u"], value=len(df_us))
    with c3: st.metric(label=txt["lbl_tema_aktif"], value=ambil_tema_aktif_sistem())
        
    st.markdown("---")
    st.markdown(txt["lbl_live_log"])
    st.write(txt["lbl_info_log"])
    
    if df_log_aktivitas.empty:
        st.info(txt["msg_log_kosong"])
    else:
        st.dataframe(df_log_aktivitas.iloc[::-1], use_container_width=True)
        
    st.markdown("---")
    st.markdown(txt["lbl_intip_db"])
    tab_f1, tab_f2, tab_f3 = st.tabs([f"📄 {DATABASE_FILE}", f"📄 {USER_FILE}", f"📄 {STATUS_THEME_FILE}"])
    
    with tab_f1: st.dataframe(df_keg, use_container_width=True)
    with tab_f2: st.dataframe(df_us, use_container_width=True)
    with tab_f3: st.code(ambil_tema_aktif_sistem(), language="text")

# --- HALAMAN 5: MANAJEMEN USER & PASSWORD ---
elif menu == txt["menu_5"] and st.session_state.role == "Admin":
    st.title(txt["menu_5"])
    
    if st.button(txt["btn_refresh"], key="ref_h5"): 
        st.toast(txt["msg_refresh"], icon="🔄")
        st.rerun()
        
    df_users = baca_users()
    st.markdown(txt["lbl_daftar_pengguna"])
    st.dataframe(df_users, use_container_width=True)
    st.markdown("---")
    st.markdown(txt["lbl_edit_akun_title"])
    
    list_username = df_users["username"].tolist()
    user_pilihan = st.selectbox(txt["lbl_pilih_u_edit"], list_username)
    
    if user_pilihan:
        data_user_lama = df_users[df_users["username"] == user_pilihan].iloc[0]
        with st.form("form_edit_user"):
            st.info(f"Account: **{user_pilihan}**")
            input_gmail_baru = st.text_input(txt["lbl_ubah_gmail"], value=str(data_user_lama["email"]))
            input_pass_baru = st.text_input(txt["lbl_ubah_pass"], value=str(data_user_lama["password"]))
            role_sekarang = data_user_lama["role"]
            idx_role = 0 if role_sekarang == "Admin" else 1
            input_role_baru = st.selectbox(txt["lbl_ubah_role"], ["Admin", "User"], index=idx_role)
            
            if st.form_submit_button(txt["btn_simpan_akun"]):
                if input_gmail_baru and input_pass_baru:
                    df_users.loc[df_users["username"] == user_pilihan, "email"] = input_gmail_baru
                    df_users.loc[df_users["username"] == user_pilihan, "password"] = input_pass_baru
                    df_users.loc[df_users["username"] == user_pilihan, "role"] = input_role_baru
                    simpan_users(df_users)
                    catat_log(st.session_state.username, "Edit Akun User", f"Mengubah data profile akun '{user_pilihan}'")
                    
                    st.success(txt["msg_edit_u_sukses"])
                    st.rerun()
                else: 
                    st.error(txt["msg_edit_u_gagal"])

# --- HALAMAN 6: PUSAT TEMA GUI GLOBAL ---
elif menu == txt["menu_6"] and st.session_state.role == "Admin":
    st.title(txt["menu_6"])
    
    if st.button(txt["btn_refresh"], key="ref_h6"): 
        st.toast(txt["msg_refresh"], icon="🔄")
        st.rerun()
        
    df_t_list = baca_tema()
    semua_tema_tersedia = df_t_list["Nama_Tema"].tolist()
    tema_saat_ini = ambil_tema_aktif_sistem()
    
    idx_default_tema = semua_tema_tersedia.index(tema_saat_ini) if tema_saat_ini in semua_tema_tersedia else 0
    pilih_tema_admin = st.selectbox(txt["lbl_pilih_tema_all"], semua_tema_tersedia, index=idx_default_tema)
    
    if st.button(txt["btn_terapkan_tema"], type="primary"):
        if pilih_tema_admin:
            set_tema_aktif_sistem(pilih_tema_admin)
            catat_log(st.session_state.username, "Ganti Tema Global", f"Menerapkan tema '{pilih_tema_admin}' ke seluruh web.")
            
            st.success(txt["msg_tema_sukses"])
            st.rerun()
        else:
            st.error(txt["msg_tema_gagal"])
        
    st.markdown("---")
    with st.form("form_buat_tema", clear_on_submit=True):
        nama_t = st.text_input(txt["lbl_buat_tema_kustom"])
        c_bg = st.color_picker(txt["lbl_c_bg"], "#000000")
        c_side = st.color_picker(txt["lbl_c_side"], "#111111")
        c_txt = st.color_picker(txt["lbl_c_txt"], "#ffffff")
        c_btn = st.color_picker(txt["lbl_c_btn"], "#ff0000")
        c_card = st.color_picker(txt["lbl_c_card"], "#222222")
        if st.form_submit_button(txt["btn_simpan_tema"]):
            if nama_t:
                df_t = baca_tema()
                if nama_t in df_t["Nama_Tema"].values: 
                    st.error(txt["msg_buat_t_gagal"])
                else:
                    df_t = pd.concat([df_t, pd.DataFrame([{"Nama_Tema": nama_t, "Bg_Color": c_bg, "Sidebar_Color": c_side, "Text_Color": c_txt, "Button_Color": c_btn, "Card_Bg": c_card}])], ignore_index=True)
                    simpan_tema(df_t); set_tema_aktif_sistem(nama_t)
                    catat_log(st.session_state.username, "Buat Tema Kustom", f"Membuat dan menerapkan tema baru '{nama_t}'")
                    
                    st.success(txt["msg_tema_sukses"])
                    st.rerun()
            else:
                st.error(txt["msg_buat_t_gagal"])