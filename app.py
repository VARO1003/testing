# -*- coding: utf-8 -*-
"""
INTEND - Intelligence Doll Dashboard
Dashboard utama untuk monitoring kesehatan mental Generasi Z
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Konfigurasi halaman
st.set_page_config(
    page_title="INTEND - Intelligence Doll",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #2c3e50;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #3498db;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #3498db;
    }
    .feature-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Mock database untuk demo
MOCK_DATABASE = {
    "Bpk. Budi Setiawan": {
        "demografi": {
            "usia": 22,
            "jenis_kelamin": "Laki-laki", 
            "pekerjaan": "Mahasiswa",
            "tanggal_mulai": "2025-09-01"
        },
        "2025-10-17": {
            "emosi_dominan": "Sedih",
            "skor_sentimen": -0.72,
            "durasi_sesi": "7 menit 12 detik",
            "deteksi_wajah": {
                "senang": 0.05,
                "sedih": 0.72,
                "netral": 0.15,
                "marah": 0.08
            },
            "analisis_suara": {
                "kata_kunci": "lelah hampa beban capek sendirian nggak berguna kosong capek lelah hampa beban nggak minat bodoh lelah capek beban hampa",
                "intensitas": "Tinggi",
                "kecepatan_bicara": "Lambat"
            },
            "file_mentah": {
                "video": "https://link-ke-cloud.com/pasienA_20251017.mp4",
                "audio": "https://link-ke-cloud.com/pasienA_20251017.wav",
                "transkrip": "https://link-ke-cloud.com/pasienA_20251017.txt"
            }
        },
        "2025-10-16": {
            "emosi_dominan": "Netral", 
            "skor_sentimen": -0.15,
            "durasi_sesi": "5 menit 45 detik",
            "deteksi_wajah": {
                "senang": 0.10,
                "sedih": 0.25,
                "netral": 0.55,
                "marah": 0.10
            },
            "analisis_suara": {
                "kata_kunci": "biasa aja mager bosen tugas kuliah capek",
                "intensitas": "Sedang", 
                "kecepatan_bicara": "Normal"
            },
            "file_mentah": {
                "video": "https://link-ke-cloud.com/pasienA_20251016.mp4",
                "audio": "https://link-ke-cloud.com/pasienA_20251016.wav", 
                "transkrip": "https://link-ke-cloud.com/pasienA_20251016.txt"
            }
        }
    },
    "Ibu Citra Wahyuningsih": {
        "demografi": {
            "usia": 21,
            "jenis_kelamin": "Perempuan",
            "pekerjaan": "Mahasiswi", 
            "tanggal_mulai": "2025-09-15"
        },
        "2025-10-17": {
            "emosi_dominan": "Netral",
            "skor_sentimen": 0.05,
            "durasi_sesi": "4 menit 02 detik",
            "deteksi_wajah": {
                "senang": 0.20,
                "sedih": 0.15,
                "netral": 0.60,
                "marah": 0.05
            },
            "analisis_suara": {
                "kata_kunci": "nggak apa-apa udah lebih baik tugas selesai",
                "intensitas": "Rendah",
                "kecepatan_bicara": "Normal"
            },
            "file_mentah": {
                "video": "https://link-ke-cloud.com/pasienB_20251017.mp4",
                "audio": "https://link-ke-cloud.com/pasienB_20251017.wav",
                "transkrip": "https://link-ke-cloud.com/pasienB_20251017.txt"
            }
        }
    }
}

def show_dashboard():
    """Dashboard Psikolog"""
    st.title("👨‍⚕️ Dashboard Psikolog INTEND")
    st.markdown("Analisis emosional mendetail untuk setiap pasien")
    
    # Sidebar navigation
    st.sidebar.header("Navigasi Pasien")
    selected_patient = st.sidebar.selectbox(
        "Pilih Pasien:", 
        options=list(MOCK_DATABASE.keys())
    )
    
    if selected_patient:
        patient_data = MOCK_DATABASE[selected_patient]
        sessions = [key for key in patient_data.keys() if key != "demografi"]
        
        selected_session_date = st.sidebar.selectbox(
            "Pilih Tanggal Sesi:", 
            options=sessions
        )
        
        # Main content
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.header(f"Profil: {selected_patient}")
            demografi = patient_data["demografi"]
            st.write(f"**Usia:** {demografi['usia']} tahun")
            st.write(f"**Jenis Kelamin:** {demografi['jenis_kelamin']}")
            st.write(f"**Pekerjaan:** {demografi['pekerjaan']}")
            st.write(f"**Terapi dimulai:** {demografi['tanggal_mulai']}")
        
        with col2:
            st.header("Statistik Ringkas")
            total_sessions = len(sessions)
            st.metric("Total Sesi", total_sessions)
            
            if sessions:
                latest_session = patient_data[sessions[0]]
                st.metric("Emosi Terakhir", latest_session["emosi_dominan"])
        
        st.markdown("---")
        
        # Session analysis
        if selected_session_date:
            session_data = patient_data[selected_session_date]
            
            st.header(f"Analisis Sesi: {selected_session_date}")
            
            # Key metrics
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Emosi Dominan", session_data["emosi_dominan"])
            col2.metric("Skor Sentimen", f"{session_data['skor_sentimen']:.2f}")
            col3.metric("Durasi Sesi", session_data["durasi_sesi"])
            col4.metric("Intensitas Suara", session_data["analisis_suara"]["intensitas"])
            
            # Visualization row
            col1, col2 = st.columns(2)
            
            with col1:
                # Emotion distribution chart
                st.subheader("Distribusi Ekspresi Wajah")
                emotion_data = session_data["deteksi_wajah"]
                fig = px.pie(
                    values=list(emotion_data.values()),
                    names=list(emotion_data.keys()),
                    color=list(emotion_data.keys()),
                    color_discrete_map={
                        'senang': '#2ecc71',
                        'sedih': '#3498db', 
                        'netral': '#95a5a6',
                        'marah': '#e74c3c'
                    }
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Word cloud
                st.subheader("Kata Kunci Dominan")
                text = session_data["analisis_suara"]["kata_kunci"]
                if text.strip():
                    try:
                        from wordcloud import WordCloud
                        wordcloud = WordCloud(
                            width=800, 
                            height=400, 
                            background_color='white',
                            colormap='viridis'
                        ).generate(text)
                        
                        fig, ax = plt.subplots(figsize=(10, 5))
                        ax.imshow(wordcloud, interpolation='bilinear')
                        ax.axis("off")
                        st.pyplot(fig)
                    except Exception as e:
                        st.error(f"Error generating word cloud: {e}")
                else:
                    st.info("Tidak ada kata kunci yang cukup untuk ditampilkan.")
            
            # Raw file access
            st.subheader("🗂️ Akses File Mentah Sesi")
            col_vid, col_aud, col_txt = st.columns(3)
            
            file_data = session_data["file_mentah"]
            col_vid.link_button("🎬 Rekaman Video", file_data["video"])
            col_aud.link_button("🎧 Audio Sesi", file_data["audio"]) 
            col_txt.link_button("📄 Transkrip Lengkap", file_data["transkrip"])

def show_about():
    """Halaman Tentang INTEND"""
    st.title("🤖 Tentang INTEND")
    st.markdown("Intelligence Doll untuk Kesehatan Mental Generasi Z")
    
    # Problem statement
    st.header("🎯 Latar Belakang Masalah")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Fakta Mengkhawatirkan")
        st.write("""
        - **Generasi Z**: Prevalensi depresi tertinggi (2%)
        - **Hanya 10.4%** yang mencari bantuan profesional  
        - **48%** merasa bisa mengatasi sendiri
        - **45%** terkendala biaya
        - **24%** tidak tahu cara akses layanan
        """)
    
    with col2:
        st.subheader("Solusi Konvensional")
        st.write("""
        - Aplikasi kesehatan mental: **Hanya 3.3%** user retention setelah 30 hari
        - Terapi tradisional: Bergantung pada **laporan retrospektif** yang bias
        - Kurangnya **interaksi manusiawi** dan **dukungan personal**
        """)
    
    st.markdown("---")
    
    # INTEND Solution
    st.header("💡 Solusi INTEND")
    
    st.write("""
    **INTEND (Intelligence Doll)** menghadirkan solusi inovatif dengan mengintegrasikan:
    - **AI Emotion Detection** - Deteksi ekspresi wajah real-time
    - **Voice Analysis** - Analisis suara dan speech-to-text  
    - **Empathic Interaction** - Respons AI yang personal
    - **Clinical Dashboard** - Monitoring untuk psikolog
    """)
    
    # Specifications
    st.header("🔧 Spesifikasi Teknis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Spesifikasi Fisik")
        st.write("""
        - **Dimensi**: 61×35×88 cm
        - **Berat**: 1.4 Kg  
        - **Material Eksterior**: Kain Rasfur
        - **Material Interior**: Bahan Cetak 3D
        """)
    
    with col2:
        st.subheader("Spesifikasi Elektronik")
        st.write("""
        - **Processor**: LattePanda V1
        - **Sensor**: Kamera 1080p + Mikrofon
        - **Output**: Speaker + LCD Touchscreen
        - **Daya**: Power Bank 10000mAh
        """)

def show_home():
    """Dashboard Utama"""
    st.markdown('<h1 class="main-header">INTEND</h1>', unsafe_allow_html=True)
    st.markdown('<h2 class="sub-header">Intelligence Doll untuk Kesehatan Mental Generasi Z</h2>', unsafe_allow_html=True)
    
    # Quick stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Pasien", len(MOCK_DATABASE))
    
    with col2:
        total_sessions = sum(len(patient_data) - 1 for patient_data in MOCK_DATABASE.values())
        st.metric("Total Sesi", total_sessions)
    
    with col3:
        st.metric("Akurasi Deteksi Wajah", "90%")
    
    with col4:
        st.metric("Akurasi Voice-to-Text", "98%")
    
    st.markdown("---")
    
    # Features overview
    st.subheader("🎯 Fitur Utama INTEND")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        with st.container():
            st.markdown("""
            <div class="feature-card">
                <h3>🤖 Deteksi Ekspresi Wajah</h3>
                <p>Analisis real-time 6 fitur geometris wajah dengan akurasi 90%</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        with st.container():
            st.markdown("""
            <div class="feature-card">
                <h3>🎤 Analisis Suara</h3>
                <p>Speech-to-text 98% akurat + analisis leksikal gejala depresi</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col3:
        with st.container():
            st.markdown("""
            <div class="feature-card">
                <h3>📊 Dashboard Psikolog</h3>
                <p>Monitoring data emosional pasien secara real-time</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col4:
        with st.container():
            st.markdown("""
            <div class="feature-card">
                <h3>💬 Interaksi Empatik</h3>
                <p>Respons AI yang personal berdasarkan kondisi emosional</p>
            </div>
            """, unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.image("https://via.placeholder.com/150x50/2c3e50/ffffff?text=INTEND", use_column_width=True)
st.sidebar.title("🧭 Navigasi")

# Main page selection
page = st.sidebar.radio("Pilih Halaman:", [
    "🏠 Dashboard Utama",
    "📊 Dashboard Psikolog", 
    "🤖 Tentang INTEND"
])

# Route to selected page
if page == "🏠 Dashboard Utama":
    show_home()
elif page == "📊 Dashboard Psikolog":
    show_dashboard()
elif page == "🤖 Tentang INTEND":
    show_about()

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #7f8c8d;'>"
    "INTEND - Intelligence Doll © 2025 | Universitas Airlangga"
    "</div>", 
    unsafe_allow_html=True
)
