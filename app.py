import os
import sys
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import pytz
from streamlit_javascript import st_javascript
import time

# Konfigurasi Halaman - Wajib di baris pertama setelah import
st.set_page_config(page_title="Sistem Dokumentasi Privat v15", layout="wide")

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

# --- PERUBAHAN PASSWORD ADMIN BAWAAN MENJADI 'adminsaja' ---
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
    path_base = PATH_FOTO if kategori == "Foto" else PATH_VIDEO
    return [f for f in os.listdir(path_base) if os.path.isdir(os.path.join(path_base, f))]

def ambil_tema_aktif_sistem():
    with open(STATUS_THEME_FILE, "r", encoding="utf-8") as f:
        return f.read().strip()

def set_tema_aktif_sistem(nama_tema):
    with open(STATUS_THEME_FILE, "w", encoding="utf-8") as f:
        f.write(nama_tema)

# --- KAMUS MULTI-BAHASA LENGKAP (7 BAHASA UTUH) ---
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
        "menu_4": "📊 Pusat Dashboard & Monitoring Log", "menu_5": "👥 Manajemen User & Password", "menu_6": "🎨 Pusat Tema GUI Global (Admin)", "pilih_hal": "Pilih Halaman:"
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
        "menu_4": "📊 Dashboard & Database Monitor", "menu_5": "👥 User & Password Management", "menu_6": "🎨 GUI Global Themes (Admin)", "pilih_hal": "Select Page:"
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
        "hari": "일", "jam": "시간", "menit": "분", "detik": "초", "permanen": "📌 영구 게시물", "hanya_teks": "📌 텍스트 노트 전용 (파일 없음)",
        "salin_share": "##### 🔗 공유할 노트 복사:", "tanggal": "날짜", "detail": "상세 설명",
        "menu_1": "🎬 활성 갤러리 및 노트", "menu_2": "➕ 노트 입력 및 삭제", "menu_3": "📁 폴더 관리",
        "menu_4": "📊 대시보드 및 데이터베이스 모니터링", "menu_5": "👥 사용자 및 비밀번호 관리", "menu_6": "🎨 GUI 글로벌 테마 (관리자)", "pilih_hal": "페이지 선택:"
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
        "menu_1": "🎬 アクティブギャラリー＆ノート", "menu_2": "➕ ノートの追加・削除", "menu_3": "📁 フォルダ管理",
        "menu_4": "📊 Dashboard＆データベース監視", "menu_5": "👥 ユーザー＆パスワード管理", "menu_6": "🎨 GUI グローバルテーマ (管理者)", "pilih_hal": "ページ選択:"
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
        "menu_4": "📊 แดชบอร์ดและระบบตรวจสอบบันทึก", "menu_5": "👥 จัดการผู้ใช้งาน & รหัสผ่าน", "menu_6": "🎨 ปรับแต่งธีมแผงควบคุม (ผู้ดูแล)", "pilih_hal": "เลือกหน้า:"
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
        "pilih_email_dulu": "Mangyaring ilagay muna ang iyong email!", "galeri_title": "🎬 Aktibong Gallery at mga Tala",
        "filter_kat": "### 🔍 Filter ng Kategorya", "pilih_jenis": "Pumili ng Uri ng Dokumentasyon:", "semua": "Lahat",
        "catatan_saja": "Mga Tala lamang", "foto": "Mga Larawan", "video": "Mga Video", "pilih_f_internal": "📁 Pumili ng Folder sa loob ng Kategorya",
        "semua_folder": "Lahat ng Folder", "kosong": "Walang aktibong mga tala sa kasalukuyan.", "sisa_waktu": "⏳ **Natitirang Oras ng Display:**",
        "hari": "Araw", "jam": "Oras", "menit": "Minuto", "detik": "Segundo", "permanen": "📌 Permanenteng Post", "hanya_teks": "📌 Tala ng Teksto Lamang (Walang File)",
        "salin_share": "##### 🔗 Kopyahin ang Tala para Ibahagi:", "tanggal": "Petsa", "detail": "Detalyadong Paglalarawan",
        "menu_1": "🎬 Aktibong Gallery at mga Tala", "menu_2": "➕ Magdagdag at Magbura ng Tala", "menu_3": "📁 Pamamahala ng Folder",
        "menu_4": "📊 Dashboard at Pagsubaybay sa Database", "menu_5": "👥 Pamamahala ng User at Password", "menu_6": "🎨 Pamamahala ng Tema (Admin)", "pilih_hal": "Pumili ng Pahina:"
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
        "menu_4": "📊 數據主控台與實時日誌監控", "menu_5": "👥 用戶權限與密碼管理中心", "menu_6": "🎨 GUI 全局網頁視覺主題 (管理員專屬)", "pilih_hal": "選擇頁面:"
    }
}

# --- DETEKSI BAHASA OTOMATIS BERDASARKAN DEVICE ---
if "bahasa_pilihan" not in st.session_state:
    try:
        kode_lang = st_javascript("navigator.language || navigator.userLanguage;")
        kode_clean = str(kode_lang).lower()
        if kode_clean.startswith("id"): st.session_state.bahasa_pilihan = "Indonesia"
        elif kode_clean.startswith("ko"): st.session_state.bahasa_pilihan = "Korea (한국어)"
        elif kode_clean.startswith("ja"): st.session_state.bahasa_pilihan = "Jepang (日本語)"
        elif kode_clean.startswith("th"): st.session_state.bahasa_pilihan = "Thailand (ไทย)"
        elif kode_clean.startswith("tl") or kode_clean.startswith("fil"): st.session_state.bahasa_pilihan = "Philippines (Tagalog)"
        elif kode_clean.startswith("zh-tw") or kode_clean.startswith("zh-hk"): st.session_state.bahasa_pilihan = "Taiwan (繁體中文)"
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

txt = KAMUS.get(st.session_state.bahasa_pilihan, KAMUS["Indonesia"])

# --- SIDEBAR ATAS: NAVIGASI ---
st.sidebar.title(txt["navigasi"])

lang_list = list(KAMUS.keys())
idx_lang = lang_list.index(st.session_state.bahasa_pilihan) if st.session_state.bahasa_pilihan in lang_list else 0
pilih_lang_manual = st.sidebar.selectbox("🌐 Language / Bahasa:", lang_list, index=idx_lang)
if pilih_lang_manual != st.session_state.bahasa_pilihan:
    st.session_state.bahasa_pilihan = pilih_lang_manual
    st.toast(f"Bahasa diubah ke {pilih_lang_manual}", icon="🌐")
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
    st.sidebar.success(f"Halo, {st.session_state.username} ({st.session_state.role})")
    if st.sidebar.button(txt["logout"]):
        catat_log(st.session_state.username, "Log Out", "Pengguna keluar dari aplikasi.")
        st.session_state.logged_in = False; st.session_state.username = ""; st.session_state.role = "Belum Login"
        st.session_state.autofill_user = ""; st.session_state.autofill_pass = ""
        st.session_state.indeks_tab = 0
        st.toast("👋 Berhasil Log Out dari sistem!", icon="ℹ️")
        st.rerun()
else:
    st.sidebar.info(txt["belum_login"])

pilihan_menu = []
if not st.session_state.logged_in:
    pilihan_menu = ["Log In / Daftar Akun"]
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
if menu == "Log In / Daftar Akun":
    st.title(txt["menu_akses"])
    
    if st.button("🔄 Refresh Halaman Ini", key="ref_akses"): 
        st.toast("Halaman berhasil diperbarui!", icon="🔄")
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
                st.success(f"🎉 Login Berhasil! Selamat datang, {input_user}.")
                st.toast(f"🎉 Login Berhasil! Selamat datang, {input_user}.", icon="✅")
                st.rerun()
            else: 
                st.error(txt["err_login"])
                st.toast("❌ Login Gagal! Periksa kembali Username & Password Anda.", icon="❌")
                
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
                    st.toast("❌ Registrasi Gagal! Username sudah digunakan.", icon="⚠️")
                else:
                    df_users = pd.concat([df_users, pd.DataFrame([{"username": reg_user, "email": reg_gmail, "password": reg_pass, "role": "User"}])], ignore_index=True)
                    simpan_users(df_users)
                    catat_log(reg_user, "Pendaftaran Akun Baru", f"Mendaftar menggunakan Gmail: {reg_gmail}")
                    st.success(txt["sukses_daftar"])
                    st.toast("💚 Akun baru berhasil didaftarkan!", icon="💚")
            else: 
                st.error(txt["wajib_isi"])
                st.toast("⚠️ Registrasi Gagal! Kolom tidak boleh kosong.", icon="🛑")

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
                    st.success("🔑 Akun Ditemukan! Mengalihkan ke form login...")
                    st.toast("Akun ditemukan! Data otomatis diisi.", icon="🔑")
                    st.session_state.indeks_tab = 0; st.rerun()
                else: 
                    st.error(txt["err_email_salah"])
                    st.toast("❌ Pemulihan Gagal! Gmail tidak terdaftar.", icon="❌")
            else: 
                st.warning(txt["pilih_email_dulu"])
                st.toast("⚠️ Input Diperlukan! Isi Gmail terlebih dahulu.", icon="📝")

# --- HALAMAN 1: CATATAN AKTIF ---
elif menu == txt["menu_1"]:
    st.title(txt["galeri_title"])
    
    if st.button("🔄 Refresh Halaman Ini", key="ref_h1"): 
        st.toast("Koleksi galeri berhasil di-update!", icon="🔄")
        st.rerun()
        
    df_kegiatan = baca_kegiatan()
    st.markdown(txt["filter_kat"])
    
    media_pilihan = st.radio(txt["pilih_jenis"], [txt["semua"], txt["catatan_saja"], txt["foto"], txt["video"]], horizontal=True)
    pilihan_clean = "Semua"
    if media_pilihan == txt["catatan_saja"]: pilihan_clean = "Catatan saja"
    elif media_pilihan == txt["foto"]: pilihan_clean = "Foto"
    elif media_pilihan == txt["video"]: pilihan_clean = "Video"
    
    folder_pilihan = "Semua Folder"
    if pilihan_clean in ["Foto", "Video"]:
        list_folder_filter = ambil_daftar_folder(pilihan_clean)
        folder_pilihan = st.selectbox(f"{txt['pilih_f_internal']} {media_pilihan}:", [txt["semua_folder"]] + list_folder_filter)
        
    st.markdown("---")
    if df_kegiatan.empty:
        st.info(txt["kosong"])
    else:
        waktu_sekarang = datetime.now(WIB).replace(tzinfo=None)
        ada_catatan_aktif = False
        for index, row in df_kegiatan.iterrows():
            if pilihan_clean != "Semua" and row["Kategori"] != pilihan_clean: continue
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
                             if row["Kategori"] == "Video": st.video(str(file_path))
                             else: st.image(str(file_path), use_container_width=True)
                             with open(str(file_path), "rb") as file_data:
                                 if st.download_button(label=f"📥 Download {row['Kategori']}", data=file_data, file_name=os.path.basename(str(file_path)), mime="video/mp4" if row["Kategori"] == "Video" else "image/jpeg", key=f"dl_{row['ID']}"):
                                     st.toast("📥 File berhasil diunduh!", icon="✅")
                         else: st.info(txt["hanya_teks"])
                             
                    with col2:
                        st.subheader(row["Nama Kegiatan"])
                        info_folder = f" | 📁 Folder: **{row.get('Folder', 'Umum')}**" if row["Kategori"] in ["Foto", "Video"] else ""
                        st.caption(f"📅 {txt['tanggal']}: {row['Tanggal']} | 🏷️ Kategori: **{row['Kategori']}**{info_folder}")
                        
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
    st.title("🛠️ Pusat Kontrol Catatan (Akses Admin)")
    
    if st.button("🔄 Refresh Halaman Ini", key="ref_h2"): 
        st.toast("Form dan database berhasil dimuat ulang!", icon="🔄")
        st.rerun()
        
    tab_input, tab_hapus = st.tabs(["➕ Tambah Catatan Baru", "🗑️ Hapus Catatan"])
    with tab_input:
        kat_terpilih = st.selectbox("1. Pilih Jenis Kategori Terlebih Dahulu:", ["Catatan saja", "Foto", "Video"])
        
        # Menggunakan struktur form bawaan tanpa modifikasi state eksternal yang rumit
        with st.form("form_upload_catatan", clear_on_submit=False):
            name = st.text_input("Nama Kegiatan/Catatan:")
            folder_tujuan = st.selectbox("Folder:", ambil_daftar_folder(kat_terpilih)) if kat_terpilih in ["Foto", "Video"] else "Tidak Butuh Folder"
            detail = st.text_area("Detail Keterangan:")
            
            # FITUR BARU: Menambahkan accept_multiple_files=True agar bisa pilih banyak media sekaligus
            uploaded_files = st.file_uploader("Upload Media (Bisa pilih banyak file sekaligus):", type=["png", "jpg", "jpeg", "mp4"], accept_multiple_files=True)
            
            st.markdown("### ⏱️ Atur Durasi Masa Tampil Konten")
            set_permanen = st.checkbox("Jadikan Postingan Ini Permanen (Selalu Tampil)", value=False)
            
            disabled_inputs = True if set_permanen else False
            c_day, c_hr, c_min, c_sec = st.columns(4)
            with c_day: durasi_hari = st.number_input("Hari:", min_value=0, value=1, disabled=disabled_inputs)
            with c_hr: durasi_jam = st.number_input("Jam:", min_value=0, max_value=23, value=0, disabled=disabled_inputs)
            with c_min: durasi_menit = st.number_input("Menit:", min_value=0, max_value=59, value=0, disabled=disabled_inputs)
            with c_sec: durasi_detik = st.number_input("Detik:", min_value=0, max_value=59, value=0, disabled=disabled_inputs)
            
            submit_button = st.form_submit_button("Publikasikan")
            
        if submit_button:
            if name:
                if set_permanen:
                    total_menit_simpan = 99999999
                else:
                    total_menit_simpan = (durasi_hari * 1440) + (durasi_jam * 60) + durasi_menit + (durasi_detik / 60.0)
                    if total_menit_simpan <= 0:
                        total_menit_simpan = 1
                
                # EFISIENSI & SINCRONISASI LOADING: Seluruh baris pemrosesan dibungkus st.spinner
                with st.spinner("⏳ Sedang memproses dan mengunggah semua file berkas Anda ke database v6..."):
                    df_k = baca_kegiatan()
                    waktu_skrg_wib = datetime.now(WIB)
                    
                    # Logika jika tidak ada file (Hanya Catatan Teks)
                    if not uploaded_files:
                        new_rec = {
                            "ID": str(int(waktu_skrg_wib.timestamp())), 
                            "Tanggal": waktu_skrg_wib.strftime("%Y-%m-%d"), 
                            "Nama Kegiatan": name, 
                            "Kategori": kat_terpilih, 
                            "Folder": folder_tujuan, 
                            "Detail": detail, 
                            "File Dokumentasi": "", 
                            "Waktu_Upload": waktu_skrg_wib.strftime("%Y-%m-%d %H:%M:%S"), 
                            "Masa_Berlaku_Menit": total_menit_simpan, 
                            "Oleh_Admin": st.session_state.username
                        }
                        df_k = pd.concat([df_k, pd.DataFrame([new_rec])], ignore_index=True)
                    
                    # Logika looping jika mengupload banyak file sekaligus
                    else:
                        for i, file_satuan in enumerate(uploaded_files):
                            # Beri nama unik tiap file agar tidak saling menimpa jika nama filenya sama
                            timestamp_unik = int(waktu_skrg_wib.timestamp()) + i
                            nama_file_fisik = f"{timestamp_unik}_{file_satuan.name}"
                            file_path = os.path.join(FOLDER_UTAMA_MEDIA, kat_terpilih, folder_tujuan, nama_file_fisik)
                            
                            # Simpan file ke storage baru
                            with open(file_path, "wb") as f: 
                                f.write(file_satuan.getbuffer())
                            
                            # Beri penamaan judul berbeda tipis untuk tiap file di visual tabel database
                            nama_kegiatan_final = f"{name} ({i+1})" if len(uploaded_files) > 1 else name
                            
                            new_rec = {
                                "ID": str(timestamp_unik), 
                                "Tanggal": waktu_skrg_wib.strftime("%Y-%m-%d"), 
                                "Nama Kegiatan": nama_kegiatan_final, 
                                "Kategori": kat_terpilih, 
                                "Folder": folder_tujuan, 
                                "Detail": detail, 
                                "File Dokumentasi": file_path, 
                                "Waktu_Upload": waktu_skrg_wib.strftime("%Y-%m-%d %H:%M:%S"), 
                                "Masa_Berlaku_Menit": total_menit_simpan, 
                                "Oleh_Admin": st.session_state.username
                            }
                            df_k = pd.concat([df_k, pd.DataFrame([new_rec])], ignore_index=True)
                    
                    # Simpan akumulasi data ke file CSV baru
                    simpan_kegiatan(df_k)
                    catat_log(st.session_state.username, "Upload Kegiatan", f"Mengupload catatan baru multipel: '{name}'")
                    
                    # Efek jeda opsional sepersekian detik agar pengguna merasakan loading selesai penuh
                    time.sleep(1)
                
                # SISTEM PEMBERSIHAN FORMULIR TOTAL: Pemicu refresh paksa agar halaman bersih kembali semula
                st.success("✅ Seluruh berkas sukses dipublikasikan!")
                st.toast("🚀 Form dibersihkan otomatis!", icon="🧼")
                st.rerun()
            else:
                st.error("❌ Publikasi Gagal! Nama kegiatan wajib diisi.")
                st.toast("❌ Gagal publikasi konten!", icon="🛑")

    with tab_hapus:
        df_hapus = baca_kegiatan()
        if df_hapus.empty: st.info("Tidak ada catatan untuk dihapus.")
        else:
            pilihan_hapus = st.selectbox("Pilih Catatan yang Ingin Dihapus:", df_hapus["Nama Kegiatan"].tolist())
            if st.button("Hapus Secara Permanen"):
                if pilihan_hapus:
                    df_baru_hapus = df_hapus[df_hapus["Nama Kegiatan"] != pilihan_hapus]
                    simpan_kegiatan(df_baru_hapus)
                    catat_log(st.session_state.username, "Hapus Kegiatan", f"Menghapus catatan: '{pilihan_hapus}'")
                    
                    st.success(f"🗑️ Catatan '{pilihan_hapus}' berhasil dihapus dari sistem!")
                    st.toast("🗑️ Catatan terhapus permanen!", icon="🗑️")
                    st.rerun()
                else:
                    st.error("❌ Penghapusan Gagal! Catatan tidak valid.")
                    st.toast("❌ Gagal menghapus catatan!", icon="❌")

# --- HALAMAN 3: MANAJEMEN FOLDER KATEGORI ---
elif menu == txt["menu_3"] and st.session_state.role == "Admin":
    st.title("📁 Manajemen Folder Kategori")
    
    if st.button("🔄 Refresh Halaman Ini", key="ref_h3"): 
        st.toast("Struktur direktori diperbarui!", icon="🔄")
        st.rerun()
        
    nama_f = st.text_input("Nama Folder Baru:")
    kat_f = st.selectbox("Kategori:", ["Foto", "Video"])
    if st.button("Buat Folder"):
        if nama_f:
            os.makedirs(os.path.join(PATH_FOTO if kat_f == "Foto" else PATH_VIDEO, nama_f), exist_ok=True)
            catat_log(st.session_state.username, "Buat Folder", f"Membuat folder '{nama_f}' di kategori {kat_f}")
            
            st.success(f"📁 Folder '{nama_f}' berhasil dibuat di kategori {kat_f}!")
            st.toast("📁 Folder baru sukses dibuat!", icon="📁")
            st.rerun()
        else:
            st.warning("⚠️ Pembuatan Gagal! Nama folder tidak boleh kosong.")
            st.toast("⚠️ Nama folder kosong!", icon="🛑")

# --- HALAMAN 4: MONITORING DATABASE & LOG LIVE ---
elif menu == txt["menu_4"] and st.session_state.role == "Admin":
    st.title(txt["menu_4"])
    
    if st.button("🔄 Refresh Halaman Ini", key="ref_h4"): 
        st.toast("Data log terupdate langsung dari server!", icon="🔄")
        st.rerun()
        
    st.write("Pantau langsung data fisik server serta jejak rekam login dan registrasi di bawah ini.")
    
    df_keg = baca_kegiatan()
    df_us = baca_users()
    df_log_aktivitas = baca_log()
    
    st.markdown("### 📈 Statistik Penyimpanan")
    c1, c2, c3 = st.columns(3)
    with c1: st.metric(label="Total Baris Catatan Kegiatan", value=len(df_keg))
    with c2: st.metric(label="Total Pengguna Sistem", value=len(df_us))
    with c3: st.metric(label="Tema Utama Aktif Web", value=ambil_tema_aktif_sistem())
        
    st.markdown("---")
    st.markdown("### ⏱️ Live Log: Riwayat Login & Pendaftaran User")
    st.write("Tabel menampilkan data tanggal & jam pengguna secara riil berurutan dari yang paling baru:")
    
    if df_log_aktivitas.empty:
        st.info("Belum ada riwayat aktivitas yang terekam.")
    else:
        st.dataframe(df_log_aktivitas.iloc[::-1], use_container_width=True)
        
    st.markdown("---")
    st.markdown("### 🔍 Intip File Database Mentah")
    tab_f1, tab_f2, tab_f3 = st.tabs([f"📄 {DATABASE_FILE}", f"📄 {USER_FILE}", f"📄 {STATUS_THEME_FILE}"])
    
    with tab_f1: st.dataframe(df_keg, use_container_width=True)
    with tab_f2: st.dataframe(df_us, use_container_width=True)
    with tab_f3: st.code(ambil_tema_aktif_sistem(), language="text")

# --- HALAMAN 5: MANAJEMEN USER & PASSWORD ---
elif menu == txt["menu_5"] and st.session_state.role == "Admin":
    st.title("👥 Manajemen User & Password (Akses Admin)")
    
    if st.button("🔄 Refresh Halaman Ini", key="ref_h5"): 
        st.toast("Daftar user berhasil dimuat ulang!", icon="🔄")
        st.rerun()
        
    df_users = baca_users()
    st.markdown("### 📋 Daftar Pengguna Terdaftar")
    st.dataframe(df_users, use_container_width=True)
    st.markdown("---")
    st.markdown("### ✏️ Edit Data Akun (Gmail, Password & Role)")
    
    list_username = df_users["username"].tolist()
    user_pilihan = st.selectbox("Pilih Username yang Akan Diedit:", list_username)
    
    if user_pilihan:
        data_user_lama = df_users[df_users["username"] == user_pilihan].iloc[0]
        with st.form("form_edit_user"):
            st.info(f"Mengedit Akun: **{user_pilihan}**")
            input_gmail_baru = st.text_input("Ubah Gmail:", value=str(data_user_lama["email"]))
            input_pass_baru = st.text_input("Ubah Password:", value=str(data_user_lama["password"]))
            role_sekarang = data_user_lama["role"]
            idx_role = 0 if role_sekarang == "Admin" else 1
            input_role_baru = st.selectbox("Ubah Hak Akses (Role):", ["Admin", "User"], index=idx_role)
            
            if st.form_submit_button("Simpan Perubahan Akun"):
                if input_gmail_baru and input_pass_baru:
                    df_users.loc[df_users["username"] == user_pilihan, "email"] = input_gmail_baru
                    df_users.loc[df_users["username"] == user_pilihan, "password"] = input_pass_baru
                    df_users.loc[df_users["username"] == user_pilihan, "role"] = input_role_baru
                    simpan_users(df_users)
                    catat_log(st.session_state.username, "Edit Akun User", f"Mengubah data profile akun '{user_pilihan}'")
                    
                    st.success(f"✏️ Perubahan Akun '{user_pilihan}' Telah Berhasil Disimpan!")
                    st.toast("👤 Profil pengguna terupdate!", icon="👤")
                    st.rerun()
                else: 
                    st.error("❌ Pembaruan Gagal! Gmail dan Password tidak boleh dikosongkan.")
                    st.toast("❌ Data tidak boleh kosong!", icon="🛑")

# --- HALAMAN 6: PUSAT TEMA GUI GLOBAL ---
elif menu == txt["menu_6"] and st.session_state.role == "Admin":
    st.title("🎨 Pusat Kontrol Tema GUI Global (Eksklusif Admin)")
    
    if st.button("🔄 Refresh Halaman Ini", key="ref_h6"): 
        st.toast("Daftar konfigurasi tema dimuat ulang!", icon="🔄")
        st.rerun()
        
    df_t_list = baca_tema()
    semua_tema_tersedia = df_t_list["Nama_Tema"].tolist()
    tema_saat_ini = ambil_tema_aktif_sistem()
    
    idx_default_tema = semua_tema_tersedia.index(tema_saat_ini) if tema_saat_ini in semua_tema_tersedia else 0
    pilih_tema_admin = st.selectbox("Pilih tema yang ingin langsung diterapkan di HP/Laptop semua user:", semua_tema_tersedia, index=idx_default_tema)
    
    if st.button("Terapkan Tema ke Seluruh Website 🌍", type="primary"):
        if pilih_tema_admin:
            set_tema_aktif_sistem(pilih_tema_admin)
            catat_log(st.session_state.username, "Ganti Tema Global", f"Menerapkan tema '{pilih_tema_admin}' ke seluruh web.")
            
            st.success(f"🎨 Tema '{pilih_tema_admin}' Telah Berhasil Diterapkan Global!")
            st.toast("✨ Tema web resmi berubah!", icon="✨")
            st.rerun()
        else:
            st.error("❌ Gagal Menerapkan! Pilihan tema tidak valid.")
            st.toast("❌ Gagal ganti tema!", icon="🛑")
        
    st.markdown("---")
    with st.form("form_buat_tema", clear_on_submit=True):
        nama_t = st.text_input("Nama Tema Baru (Contoh: Sweet Pink 🌸):")
        c_bg = st.color_picker("Pilih Warna Latar Belakang (Background):", "#000000")
        c_side = st.color_picker("Pilih Warna Sidebar Samping:", "#111111")
        c_txt = st.color_picker("Pilih Warna Teks Utama:", "#ffffff")
        c_btn = st.color_picker("Pilih Warna Tombol Utama (Accent):", "#ff0000")
        c_card = st.color_picker("Pilih Warna Kotak Kartu Galeri (Card):", "#222222")
        if st.form_submit_button("Simpan Tema Baru"):
            if nama_t:
                df_t = baca_tema()
                if nama_t in df_t["Nama_Tema"].values: 
                    st.error("❌ Pembuatan Gagal! Nama tema sudah terdaftar.")
                    st.toast("⚠️ Nama tema sudah ada!", icon="⚠️")
                else:
                    df_t = pd.concat([df_t, pd.DataFrame([{"Nama_Tema": nama_t, "Bg_Color": c_bg, "Sidebar_Color": c_side, "Text_Color": c_txt, "Button_Color": c_btn, "Card_Bg": c_card}])], ignore_index=True)
                    simpan_tema(df_t); set_tema_aktif_sistem(nama_t)
                    catat_log(st.session_state.username, "Buat Tema Kustom", f"Membuat dan menerapkan tema baru '{nama_t}'")
                    
                    st.success(f"✨ Pembuatan Tema Kustom '{nama_t}' Telah Berhasil!")
                    st.toast("🎨 Tema baru aktif!", icon="🎨")
                    st.rerun()
            else:
                st.error("❌ Pembuatan Gagal! Nama tema wajib diisi.")
                st.toast("❌ Form nama tema kosong!", icon="🛑")