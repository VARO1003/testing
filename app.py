# -*- coding: utf-8 -*-
# DASHBOARD PSIKOLOG INTEND v6.0 - Ambil Semua File JSON Otomatis dari Drive Publik
# ---------------------------------------------------------------------------

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import json, os, glob
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

# ------------------ KONFIGURASI ------------------
st.set_page_config(page_title="Dashboard Psikolog - INTEND", layout="wide")
LOCAL_DATA_PATH = "logs_drive/"  # folder lokal untuk cache file JSON
os.makedirs(LOCAL_DATA_PATH, exist_ok=True)

# Google Drive folder publik
# Isi dengan Folder ID saja: https://drive.google.com/drive/folders/<FOLDER_ID>
DRIVE_FOLDER_ID = "19vfH8Nij2D5BDSrH9K16vkLVvIvX99na"

# ------------------ LOGIN SEDERHANA ------------------
PASSWORD = "INTENDsecure"
st.title("🔒 Login Tenaga Ahli INTEND")
pwd_input = st.text_input("Masukkan password:", type="password")
if pwd_input != PASSWORD:0000
    st.warning("Password salah! Hanya tenaga ahli yang bisa mengakses.")
    st.stop()
st.success("✅ Login berhasil. Selamat datang!")

# ------------------ FUNGSIONALITAS GOOGLE DRIVE ------------------
@st.cache_data
def download_json_from_drive(folder_id, local_path):
    """
    Download semua file JSON dari folder publik Google Drive ke folder lokal.
    Memakai PyDrive.
    """
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()  # login pertama kali
    drive = GoogleDrive(gauth)

    # List semua file di folder
    file_list = drive.ListFile({'q': f"'{folder_id}' in parents and trashed=false"}).GetList()
    for file in file_list:
        if file['title'].lower().endswith(".json"):
            local_file = os.path.join(local_path, file['title'])
            if not os.path.exists(local_file):
                file.GetContentFile(local_file)

@st.cache_data
def load_sessions_from_folder(folder_path):
    """Load semua JSON dari folder lokal menjadi satu dict"""
    data = {}
    json_files = glob.glob(os.path.join(folder_path, "*.json"))
    for file in json_files:
        try:
            with open(file, "r", encoding="utf-8") as f:
                session = json.load(f)
                data.update(session)
        except Exception as e:
            st.error(f"Gagal membaca {file}: {e}")
    return data

# ------------------ AMBIL DATA DARI DRIVE ------------------
download_json_from_drive(DRIVE_FOLDER_ID, LOCAL_DATA_PATH)
MOCK_DATABASE = load_sessions_from_folder(LOCAL_DATA_PATH)

if not MOCK_DATABASE:
    st.info(f"Belum ada data sesi. Pastikan file JSON tersedia di Drive folder {DRIVE_FOLDER_ID}")
    st.stop()

# ------------------ SIDEBAR PASIEN ------------------
st.sidebar.subheader("👨‍⚕️ Pilih Pasien & Sesi")
selected_patient = st.sidebar.selectbox("Pilih Pasien:", options=list(MOCK_DATABASE.keys()))
selected_session_date = st.sidebar.selectbox("Pilih Tanggal Sesi:", options=list(MOCK_DATABASE[selected_patient].keys()))
session_data = MOCK_DATABASE[selected_patient][selected_session_date]

# ------------------ DASHBOARD ------------------
st.title(f"📊 Dashboard Emosional - {selected_patient}")
st.subheader(f"Sesi tanggal: {selected_session_date}")
st.markdown("---")

# Ringkasan utama
col1, col2, col3 = st.columns(3)
col1.metric("Emosi Dominan", session_data.get("emosi_dominan", "-"))
col2.metric("Skor Sentimen", session_data.get("skor_sentimen", "-"))
col3.metric("Durasi Sesi", session_data.get("durasi_sesi", "-"))

st.markdown("---")

# Akses file mentah
st.subheader("🗂️ File Mentah & Hasil Analisis")
col_vid, col_aud, col_txt = st.columns(3)
if session_data.get("link_video"):
    col_vid.link_button("🎬 Lihat Video", session_data["link_video"])
if session_data.get("link_audio"):
    col_aud.link_button("🎧 Dengarkan Audio", session_data["link_audio"])
if session_data.get("link_transkrip"):
    col_txt.link_button("📄 Baca Transkrip", session_data["link_transkrip"])

st.markdown("---")

# Visualisasi kata kunci
st.subheader("☁️ Word Cloud Kata Kunci")
try:
    teks = session_data.get("teks_kata_kunci", "")
    if teks:
        wordcloud = WordCloud(width=800, height=300, background_color="white", colormap="viridis").generate(teks)
        fig, ax = plt.subplots(figsize=(12,5))
        ax.imshow(wordcloud, interpolation="bilinear")
        ax.axis("off")
        st.pyplot(fig)
    else:
        st.info("Tidak ada kata kunci yang cukup untuk ditampilkan.")
except Exception as e:
    st.error(f"Gagal menampilkan WordCloud: {e}")

st.markdown("---")

# Tabel log seluruh sesi
st.subheader("🧾 Log Semua Sesi Pasien")
log_data = []
for patient, sessions in MOCK_DATABASE.items():
    for date, info in sessions.items():
        log_data.append({
            "Pasien": patient,
            "Tanggal": date,
            "Emosi Dominan": info.get("emosi_dominan", "-"),
            "Skor Sentimen": info.get("skor_sentimen", "-"),
            "Durasi": info.get("durasi_sesi", "-"),
        })

df_log = pd.DataFrame(log_data).sort_values(by=["Tanggal"], ascending=False)
st.dataframe(df_log, use_container_width=True)

st.markdown("---")
st.caption("📁 Semua file JSON otomatis diambil dari Google Drive publik.")
st.caption("🔒 Akses terbatas untuk tenaga ahli dengan password yang valid.")
