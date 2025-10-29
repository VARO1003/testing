# -*- coding: utf-8 -*-
"""
INTEND - Intelligence Doll Dashboard
Dashboard utama untuk monitoring kesehatan mental Generasi Z
"""

import streamlit as st
import pandas as pd
import numpy as np
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
    .speech-transcript {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #e74c3c;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Mock database - DIUBAH sesuai structure data real dari client
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
                "transkrip_lengkap": """
                [10:00:15] Saya merasa sangat lelah akhir-akhir ini
                [10:00:22] Sering bangun tengah malam dan susah tidur lagi
                [10:00:35] Rasanya semua jadi hampa dan nggak ada semangat
                [10:00:45] Capek banget, kayak beban terus aja
                [10:01:02] Kadang merasa sendirian meskipun ada orang sekitar
                """,
                "kata_kunci": "lelah hampa beban capek sendirian nggak berguna kosong capek lelah hampa beban nggak minat bodoh lelah capek beban hampa",
                "analisis_sentimen": {
                    "skor": -0.72,
                    "kategori": "Negatif",
                    "kata_positif": 2,
                    "kata_negatif": 15,
                    "kata_netral": 8
                },
                "gejala_terdeteksi": {
                    "fatigue": 8,
                    "insomnia": 3,
                    "loneliness": 5,
                    "hopelessness": 4,
                    "anhedonia": 3
                },
                "pola_bicara": {
                    "kata_per_menit": 42,
                    "kecepatan_bicara": "Lambat",
                    "frekuensi_jeda": "Tinggi"
                }
            },
            "file_mentah": {
                "video": "https://link-ke-cloud.com/pasienA_20251017.mp4",
                "audio": "https://link-ke-cloud.com/pasienA_20251017.wav",
                "transkrip": "https://link-ke-cloud.com/pasienA_20251017.txt",
                "data_teknis": "https://link-ke-cloud.com/pasienA_20251017.json"
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
                "transkrip_lengkap": """
                [09:30:10] Hari ini biasa aja sih
                [09:30:25] Cuma agak mager dan bosen
                [09:30:40] Tugas kuliah numpuk terus
                [09:30:55] Tapi masih bisa dikerjain kok
                """,
                "kata_kunci": "biasa aja mager bosen tugas kuliah capek",
                "analisis_sentimen": {
                    "skor": -0.15,
                    "kategori": "Netral",
                    "kata_positif": 3,
                    "kata_negatif": 4,
                    "kata_netral": 6
                },
                "gejala_terdeteksi": {
                    "fatigue": 4,
                    "academic_stress": 3,
                    "boredom": 2
                },
                "pola_bicara": {
                    "kata_per_menit": 65,
                    "kecepatan_bicara": "Normal", 
                    "frekuensi_jeda": "Sedang"
                }
            },
            "file_mentah": {
                "video": "https://link-ke-cloud.com/pasienA_20251016.mp4",
                "audio": "https://link-ke-cloud.com/pasienA_20251016.wav",
                "transkrip": "https://link-ke-cloud.com/pasienA_20251016.txt",
                "data_teknis": "https://link-ke-cloud.com/pasienA_20251016.json"
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
                "transkrip_lengkap": """
                [11:15:05] Nggak apa-apa kok, udah lebih baik
                [11:15:18] Tugas akhirnya udah selesai
                [11:15:30] Sekarang tinggal nunggu sidang aja
                [11:15:45] Lumayan lega sih akhirnya
                """,
                "kata_kunci": "nggak apa-apa udah lebih baik tugas selesai lega sidang",
                "analisis_sentimen": {
                    "skor": 0.05,
                    "kategori": "Netral",
                    "kata_positif": 5,
                    "kata_negatif": 1,
                    "kata_netral": 7
                },
                "gejala_terdeteksi": {
                    "academic_stress": 2,
                    "relief": 3
                },
                "pola_bicara": {
                    "kata_per_menit": 70,
                    "kecepatan_bicara": "Normal",
                    "frekuensi_jeda": "Rendah"
                }
            },
            "file_mentah": {
                "video": "https://link-ke-cloud.com/pasienB_20251017.mp4",
                "audio": "https://link-ke-cloud.com/pasienB_20251017.wav",
                "transkrip": "https://link-ke-cloud.com/pasienB_20251017.txt",
                "data_teknis": "https://link-ke-cloud.com/pasienB_20251017.json"
            }
        }
    }
}

def _sorted_session_keys(patient_data):
    """
    Return session keys sorted descending by date (ISO yyyy-mm-dd).
    If parsing fails, fallback to the original insertion order.
    """
    session_keys = [k for k in patient_data.keys() if k != "demografi"]
    try:
        sorted_keys = sorted(
            session_keys,
            key=lambda d: datetime.strptime(d, "%Y-%m-%d"),
            reverse=True
        )
        return sorted_keys
    except Exception:
        return session_keys

def show_speech_analysis_detail(speech_data):
    """Tampilkan analisis detail speech recognition"""
    st.subheader("🎤 Analisis Percakapan Detail")
    
    # Tab untuk berbagai analisis
    tab1, tab2, tab3, tab4 = st.tabs(["📝 Transkrip", "🔍 Analisis Sentimen", "🩺 Gejala Klinis", "🗣️ Pola Bicara"])
    
    with tab1:
        # Transkrip lengkap
        st.markdown("### 📝 Transkrip Percakapan")
        transcript = speech_data.get("transkrip_lengkap", "")
        if transcript:
            st.markdown(f'<div class="speech-transcript">{transcript}</div>', unsafe_allow_html=True)
        else:
            st.info("Tidak ada transkrip yang tersedia")
    
    with tab2:
        # Analisis sentimen
        st.markdown("### 🔍 Analisis Sentimen")
        sentiment = speech_data.get("analisis_sentimen", {})
        if sentiment:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                score = sentiment.get("skor", 0)
                st.metric("Skor Sentimen", f"{score:.2f}")
                
                # Progress bar sentiment
                sentiment_progress = (score + 1) / 2  # Convert -1 to 1 range to 0 to 1
                st.progress(sentiment_progress)
                
                category = sentiment.get("kategori", "Tidak diketahui")
                st.write(f"**Kategori:** {category}")
            
            with col2:
                positive = sentiment.get("kata_positif", 0)
                st.metric("Kata Positif", positive)
            
            with col3:
                negative = sentiment.get("kata_negatif", 0)
                st.metric("Kata Negatif", negative)
            
            with col4:
                neutral = sentiment.get("kata_netral", 0)
                st.metric("Kata Netral", neutral)
            
            # Sentiment chart
            sentiment_counts = [positive, negative, neutral]
            sentiment_labels = ['Positif', 'Negatif', 'Netral']
            
            fig_sentiment = px.pie(
                values=sentiment_counts,
                names=sentiment_labels,
                title="Distribusi Kata Berdasarkan Sentimen",
                color=sentiment_labels,
                color_discrete_map={
                    'Positif': '#2ecc71',
                    'Negatif': '#e74c3c', 
                    'Netral': '#3498db'
                }
            )
            st.plotly_chart(fig_sentiment, use_container_width=True)
        else:
            st.info("Analisis sentimen belum tersedia")
    
    with tab3:
        # Analisis gejala klinis
        st.markdown("### 🩺 Gejala Klinis Terdeteksi")
        symptoms = speech_data.get("gejala_terdeteksi", {})
        if symptoms:
            # Convert to DataFrame untuk visualisasi
            symptoms_df = pd.DataFrame({
                'Gejala': list(symptoms.keys()),
                'Frekuensi': list(symptoms.values())
            }).sort_values('Frekuensi', ascending=False)
            
            # Bar chart gejala
            fig_symptoms = px.bar(
                symptoms_df,
                x='Gejala',
                y='Frekuensi',
                title="Frekuensi Gejala Klinis yang Terdeteksi",
                color='Frekuensi'
            )
            st.plotly_chart(fig_symptoms, use_container_width=True)
            
            # Symptoms metrics
            st.markdown("#### 📊 Metrik Gejala")
            total_symptoms = sum(symptoms.values())
            unique_symptoms = len(symptoms)
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Deteksi Gejala", total_symptoms)
            with col2:
                st.metric("Jenis Gejala Unik", unique_symptoms)
        else:
            st.info("Tidak ada gejala klinis yang terdeteksi")
    
    with tab4:
        # Analisis pola bicara
        st.markdown("### 🗣️ Analisis Pola Bicara")
        speech_patterns = speech_data.get("pola_bicara", {})
        if speech_patterns:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                wpm = speech_patterns.get("kata_per_menit", 0)
                st.metric("Kata per Menit", wpm)
                
                # WPM indicator
                if wpm < 50:
                    st.info("⏱️ Kecepatan bicara: Lambat")
                elif wpm < 80:
                    st.success("⏱️ Kecepatan bicara: Normal") 
                else:
                    st.warning("⏱️ Kecepatan bicara: Cepat")
            
            with col2:
                speed = speech_patterns.get("kecepatan_bicara", "Tidak diketahui")
                st.metric("Kecepatan Bicara", speed)
            
            with col3:
                pause_freq = speech_patterns.get("frekuensi_jeda", "Tidak diketahui")
                st.metric("Frekuensi Jeda", pause_freq)
            
            # Speech pattern insights
            st.markdown("#### 💡 Insight Pola Bicara")
            if speech_patterns.get("kecepatan_bicara") == "Lambat":
                st.info("Pola bicara lambat dapat mengindikasikan fatigue atau depresi")
            if speech_patterns.get("frekuensi_jeda") == "Tinggi":
                st.info("Frekuensi jeda yang tinggi dapat mengindikasikan kesulitan konsentrasi")
        else:
            st.info("Analisis pola bicara belum tersedia")

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

    if not selected_patient:
        st.info("Pilih pasien dari sidebar.")
        return

    patient_data = MOCK_DATABASE[selected_patient]
    sessions = _sorted_session_keys(patient_data)

    if not sessions:
        st.info("Belum ada sesi untuk pasien ini.")
        return

    selected_session_date = st.sidebar.selectbox(
        "Pilih Tanggal Sesi:",
        options=sessions,
        index=0
    )

    # Main content
    col_main, col_side = st.columns([2, 1])

    with col_main:
        st.header(f"Profil: {selected_patient}")
        demografi = patient_data.get("demografi", {})
        st.write(f"**Usia:** {demografi.get('usia', 'N/A')} tahun")
        st.write(f"**Jenis Kelamin:** {demografi.get('jenis_kelamin', 'N/A')}")
        st.write(f"**Pekerjaan:** {demografi.get('pekerjaan', 'N/A')}")
        st.write(f"**Terapi dimulai:** {demografi.get('tanggal_mulai', 'N/A')}")

    with col_side:
        st.header("Statistik Ringkas")
        total_sessions = len(sessions)
        st.metric("Total Sesi", total_sessions)

        # latest session by sorted order
        latest_key = sessions[0] if sessions else None
        if latest_key:
            latest_session = patient_data.get(latest_key, {})
            st.metric("Emosi Terakhir", latest_session.get("emosi_dominan", "N/A"))

    st.markdown("---")

    # Session analysis
    if selected_session_date:
        session_data = patient_data.get(selected_session_date, {})
        st.header(f"Analisis Sesi: {selected_session_date}")

        # Key metrics - DIUBAH: Hapus intensitas suara
        mcol1, mcol2, mcol3 = st.columns(3)
        mcol1.metric("Emosi Dominan", session_data.get("emosi_dominan", "N/A"))
        
        # Format skor sentimen
        try:
            sentiment = session_data.get("skor_sentimen")
            sentiment_str = f"{sentiment:.2f}" if isinstance(sentiment, (int, float)) else str(sentiment)
        except Exception:
            sentiment_str = str(session_data.get("skor_sentimen", "N/A"))
        mcol2.metric("Skor Sentimen", sentiment_str)
        mcol3.metric("Durasi Sesi", session_data.get("durasi_sesi", "N/A"))

        # Visualization row
        vcol1, vcol2 = st.columns(2)

        with vcol1:
            # Emotion distribution chart
            st.subheader("Distribusi Ekspresi Wajah")
            emotion_data = session_data.get("deteksi_wajah", {})
            if emotion_data:
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
            else:
                st.info("Tidak ada data deteksi wajah untuk sesi ini.")

        with vcol2:
            # Kata kunci text analysis (tags + bar chart)
            st.subheader("Kata Kunci Dominan")
            text = session_data.get("analisis_suara", {}).get("kata_kunci", "")
            if isinstance(text, str) and text.strip():
                words = text.split()
                word_counts = {}
                for word in words:
                    normalized = word.strip().lower()
                    if not normalized:
                        continue
                    word_counts[normalized] = word_counts.get(normalized, 0) + 1

                if word_counts:
                    # Top words
                    sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:10]

                    tags_html = "<div style='display: flex; flex-wrap: wrap; gap: 10px; margin: 10px 0;'>"
                    for word, count in sorted_words:
                        size = min(12 + count * 3, 28)  # font-size in px (more reasonable)
                        tags_html += f"""
                        <span style='
                            background: #3498db;
                            color: white;
                            padding: 6px 10px;
                            border-radius: 12px;
                            font-size: {size}px;
                            font-weight: 600;
                        '>{word} ({count})</span>
                        """
                    tags_html += "</div>"

                    st.markdown(tags_html, unsafe_allow_html=True)

                    # Bar chart
                    words_df = pd.DataFrame(sorted_words, columns=['Kata', 'Frekuensi'])
                    fig_bar = px.bar(
                        words_df,
                        x='Kata',
                        y='Frekuensi',
                        title="Frekuensi Kata Kunci",
                        color='Frekuensi'
                    )
                    st.plotly_chart(fig_bar, use_container_width=True)
                else:
                    st.info("Tidak ada kata kunci yang cukup untuk ditampilkan.")
            else:
                st.info("Tidak ada kata kunci yang cukup untuk ditampilkan.")

        st.markdown("---")
        
        # SPEECH ANALYSIS DETAIL SECTION - BARU
        speech_data = session_data.get("analisis_suara", {})
        if speech_data:
            show_speech_analysis_detail(speech_data)
        else:
            st.info("Analisis percakapan belum tersedia untuk sesi ini")

        # Raw file access
        st.subheader("🗂️ Akses File Mentah Sesi")
        col_vid, col_aud, col_txt, col_data = st.columns(4)  # TAMBAH kolom data teknis

        file_data = session_data.get("file_mentah", {})
        vid_url = file_data.get("video")
        aud_url = file_data.get("audio")
        txt_url = file_data.get("transkrip")
        data_url = file_data.get("data_teknis")

        if vid_url:
            col_vid.markdown(f'<a href="{vid_url}" target="_blank">🎬 Rekaman Video</a>', unsafe_allow_html=True)
        else:
            col_vid.write("—")

        if aud_url:
            col_aud.markdown(f'<a href="{aud_url}" target="_blank">🎧 Audio Sesi</a>', unsafe_allow_html=True)
        else:
            col_aud.write("—")

        if txt_url:
            col_txt.markdown(f'<a href="{txt_url}" target="_blank">📄 Transkrip Lengkap</a>', unsafe_allow_html=True)
        else:
            col_txt.write("—")

        if data_url:
            col_data.markdown(f'<a href="{data_url}" target="_blank">📊 Data Teknis</a>', unsafe_allow_html=True)
        else:
            col_data.write("—")

# ... (fungsi show_about dan show_home tetap sama seperti sebelumnya)

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
        total_sessions = sum(len([k for k in pdict.keys() if k != "demografi"]) for pdict in MOCK_DATABASE.values())
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
st.sidebar.title("🧭 Navigasi INTEND")

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
