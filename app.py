# -*- coding: utf-8 -*-
"""
INTEND - Intelligence Doll Dashboard 
Dashboard hybrid dengan real-time data dari FastAPI server
VERSION FIXED - No OpenCV, Better Error Handling
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
import time
import json
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
    .status-live {
        color: #27ae60;
        font-weight: bold;
    }
    .status-offline {
        color: #e74c3c;
        font-weight: bold;
    }
    .patient-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Configuration - SESUAIKAN DENGAN IP SERVER ANDA
SERVER_URL = "http://192.168.113.76:8000"  # IP MSI Laptop Anda
REFRESH_INTERVAL = 15  # seconds

class INTENDDataManager:
    """Manager untuk handle data dari FastAPI server"""
    
    def __init__(self, server_url):
        self.server_url = server_url
        self.last_update = None
        
    def get_dashboard_data(self):
        """Ambil data dashboard dari FastAPI"""
        try:
            response = requests.get(f"{self.server_url}/dashboard-data", timeout=10)
            if response.status_code == 200:
                self.last_update = datetime.now()
                return response.json()
            else:
                st.error(f"Server error: {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            return None
    
    def get_export_data(self):
        """Ambil semua data untuk export"""
        try:
            response = requests.get(f"{self.server_url}/export-data", timeout=10)
            if response.status_code == 200:
                return response.json()
            return None
        except:
            return None
    
    def get_server_status(self):
        """Cek status koneksi server"""
        try:
            response = requests.get(f"{self.server_url}/dashboard-data", timeout=5)
            return response.status_code == 200
        except:
            return False

# Initialize data manager
data_manager = INTENDDataManager(SERVER_URL)

def create_mock_patient_data():
    """Create mock data untuk demo ketika server offline"""
    return {
        "Bpk. Budi Setiawan": {
            "demografi": {
                "usia": 22,
                "jenis_kelamin": "Laki-laki", 
                "pekerjaan": "Mahasiswa",
                "tanggal_mulai": "2024-01-15"
            },
            "sessions": {
                datetime.now().strftime("%Y-%m-%d"): {
                    "emosi_dominan": "Netral",
                    "skor_sentimen": -0.15,
                    "durasi_sesi": "6 menit 30 detik",
                    "deteksi_wajah": {
                        "senang": 0.25,
                        "sedih": 0.15,
                        "netral": 0.55,
                        "marah": 0.05
                    },
                    "analisis_suara": {
                        "transkrip_lengkap": """
                        [10:00:15] Halo, saya merasa cukup baik hari ini
                        [10:00:30] Tapi ada sedikit tekanan dari tugas kuliah
                        [10:00:45] Semoga bisa menyelesaikan semuanya tepat waktu
                        [10:01:00] Terima kasih sudah mendengarkan
                        """,
                        "kata_kunci": "baik tekanan tugas kuliah semoga selesai tepat waktu terima kasih",
                        "analisis_sentimen": {
                            "skor": -0.15,
                            "kategori": "Netral",
                            "kata_positif": 4,
                            "kata_negatif": 2,
                            "kata_netral": 8
                        },
                        "pola_bicara": {
                            "kata_per_menit": 68,
                            "kecepatan_bicara": "Normal",
                            "frekuensi_jeda": "Sedang"
                        }
                    }
                }
            }
        }
    }

def transform_to_patient_structure(api_data):
    """
    Transform data dari FastAPI format ke structure dashboard
    """
    patients = {}
    
    if not api_data:
        return create_mock_patient_data()
    
    # Transform biodata
    biodata_list = api_data.get("recent_biodata", [])
    for biodata in biodata_list:
        patient_name = biodata.get('nama', 'Unknown Patient')
        
        # Create patient structure
        patients[patient_name] = {
            "demografi": {
                "usia": biodata.get('usia', 'N/A'),
                "jenis_kelamin": biodata.get('jenis_kelamin', 'N/A'),
                "pekerjaan": biodata.get('pekerjaan', 'N/A'),
                "tanggal_mulai": biodata.get('received_at', datetime.now().isoformat())
            },
            "sessions": {}
        }
    
    # Transform chat sessions menjadi patient sessions
    chat_sessions = api_data.get("chat_sessions", {})
    for session_id, messages in chat_sessions.items():
        if messages and patients:
            # Use first patient for demo
            first_patient = list(patients.keys())[0]
            date_key = datetime.now().strftime("%Y-%m-%d")
            
            # Create session data from chat
            user_messages = [msg['user'] for msg in messages if 'user' in msg]
            all_text = " ".join(user_messages)
            
            # Simple sentiment analysis based on keywords
            positive_words = ['senang', 'baik', 'bagus', 'terima kasih', 'semangat']
            negative_words = ['lelah', 'capek', 'tekanan', 'susah', 'masalah']
            
            positive_count = sum(1 for word in positive_words if word in all_text.lower())
            negative_count = sum(1 for word in negative_words if word in all_text.lower())
            
            total_words = len(all_text.split())
            sentiment_score = (positive_count - negative_count) / max(total_words, 1)
            
            patients[first_patient]["sessions"][date_key] = {
                "emosi_dominan": "Sedih" if sentiment_score < -0.1 else "Senang" if sentiment_score > 0.1 else "Netral",
                "skor_sentimen": sentiment_score,
                "durasi_sesi": f"{len(messages)} menit",
                "deteksi_wajah": {
                    "senang": max(0.1, min(0.9, 0.5 + sentiment_score)),
                    "sedih": max(0.1, min(0.9, 0.5 - sentiment_score)),
                    "netral": 0.3,
                    "marah": 0.1
                },
                "analisis_suara": {
                    "transkrip_lengkap": "\n".join([f"[{datetime.fromtimestamp(msg.get('timestamp', 0)).strftime('%H:%M:%S')}] {msg.get('user', '')}" 
                                                  for msg in messages]),
                    "kata_kunci": " ".join(user_messages),
                    "analisis_sentimen": {
                        "skor": sentiment_score,
                        "kategori": "Positif" if sentiment_score > 0.1 else "Negatif" if sentiment_score < -0.1 else "Netral",
                        "kata_positif": positive_count,
                        "kata_negatif": negative_count,
                        "kata_netral": max(0, total_words - positive_count - negative_count)
                    },
                    "pola_bicara": {
                        "kata_per_menit": min(120, max(40, len(all_text) // len(messages))),
                        "kecepatan_bicara": "Normal",
                        "frekuensi_jeda": "Sedang"
                    }
                }
            }
    
    # If no patients created, use mock data
    if not patients:
        return create_mock_patient_data()
    
    return patients

def show_speech_analysis_detail(speech_data):
    """Tampilkan analisis detail speech recognition"""
    st.subheader("🎤 Analisis Percakapan Detail")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📝 Transkrip", "🔍 Analisis Sentimen", "🩺 Gejala Klinis", "🗣️ Pola Bicara"])
    
    with tab1:
        st.markdown("### 📝 Transkrip Percakapan")
        transcript = speech_data.get("transkrip_lengkap", "")
        if transcript and transcript.strip():
            st.markdown(f'<div class="speech-transcript">{transcript}</div>', unsafe_allow_html=True)
        else:
            st.info("Tidak ada transkrip yang tersedia untuk sesi ini")
    
    with tab2:
        st.markdown("### 🔍 Analisis Sentimen")
        sentiment = speech_data.get("analisis_sentimen", {})
        if sentiment:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                score = sentiment.get("skor", 0)
                st.metric("Skor Sentimen", f"{score:.2f}")
                
                # Convert -1 to 1 range to 0 to 1 for progress bar
                sentiment_progress = (score + 1) / 2
                st.progress(float(sentiment_progress))
                
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
            
            if sum(sentiment_counts) > 0:
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
        st.markdown("### 🩺 Gejala Klinis Terdeteksi")
        
        # Simple symptom detection based on keywords
        transcript_text = speech_data.get("transkrip_lengkap", "").lower()
        keywords = {
            "Kecemasan": ['cemas', 'khawatir', 'takut', 'gelisah'],
            "Depresi": ['sedih', 'putus asa', 'hampa', 'tidak berguna'],
            "Fatigue": ['lelah', 'capek', 'lesu', 'tidak bertenaga'],
            "Insomnia": ['susah tidur', 'insomnia', 'terbangun'],
            "Stress": ['tekanan', 'stress', 'tertekan', 'pusing']
        }
        
        symptoms_detected = {}
        for symptom, words in keywords.items():
            count = sum(1 for word in words if word in transcript_text)
            if count > 0:
                symptoms_detected[symptom] = count
        
        if symptoms_detected:
            symptoms_df = pd.DataFrame({
                'Gejala': list(symptoms_detected.keys()),
                'Frekuensi': list(symptoms_detected.values())
            }).sort_values('Frekuensi', ascending=False)
            
            fig_symptoms = px.bar(
                symptoms_df,
                x='Gejala',
                y='Frekuensi',
                title="Gejala Klinis yang Terdeteksi",
                color='Frekuensi',
                color_continuous_scale='Viridis'
            )
            st.plotly_chart(fig_symptoms, use_container_width=True)
            
            # Symptoms summary
            st.metric("Total Gejala Terdeteksi", len(symptoms_detected))
        else:
            st.info("Tidak ada gejala klinis yang terdeteksi dalam percakapan ini")
    
    with tab4:
        st.markdown("### 🗣️ Analisis Pola Bicara")
        speech_patterns = speech_data.get("pola_bicara", {})
        if speech_patterns:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                wpm = speech_patterns.get("kata_per_menit", 0)
                st.metric("Kata per Menit", wpm)
                
                if wpm < 50:
                    st.info("⏱️ Kecepatan bicara: Lambat")
                    st.caption("Mungkin mengindikasikan fatigue atau depresi")
                elif wpm < 80:
                    st.success("⏱️ Kecepatan bicara: Normal") 
                else:
                    st.warning("⏱️ Kecepatan bicara: Cepat")
                    st.caption("Mungkin mengindikasikan anxiety")
            
            with col2:
                speed = speech_patterns.get("kecepatan_bicara", "Tidak diketahui")
                st.metric("Kecepatan Bicara", speed)
            
            with col3:
                pause_freq = speech_patterns.get("frekuensi_jeda", "Tidak diketahui")
                st.metric("Frekuensi Jeda", pause_freq)
        else:
            st.info("Analisis pola bicara belum tersedia")

def show_realtime_analysis(live_data):
    """Tampilkan analisis real-time dari FastAPI"""
    st.header("📊 Analisis Real-time System")
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        biodata_count = live_data.get("biodata_count", 0)
        st.metric("Total Partisipan", biodata_count)
    
    with col2:
        chat_sessions_count = live_data.get("chat_sessions_count", 0)
        st.metric("Sesi Percakapan", chat_sessions_count)
    
    with col3:
        analysis_count = live_data.get("analysis_count", 0)
        st.metric("Frame Dianalisis", analysis_count)
    
    with col4:
        last_update = data_manager.last_update.strftime("%H:%M:%S") if data_manager.last_update else "N/A"
        st.metric("Update Terakhir", last_update)
    
    # Recent Biodata
    st.subheader("👥 Data Partisipan Terbaru")
    recent_biodata = live_data.get("recent_biodata", [])
    if recent_biodata:
        biodata_df = pd.DataFrame(recent_biodata)
        
        # Display in nice cards
        for _, patient in biodata_df.iterrows():
            with st.container():
                st.markdown(f"""
                <div class="patient-card">
                    <h3>👤 {patient.get('nama', 'Unknown')}</h3>
                    <p><strong>Usia:</strong> {patient.get('usia', 'N/A')} | <strong>Pekerjaan:</strong> {patient.get('pekerjaan', 'N/A')}</p>
                    <p><strong>Bergabung:</strong> {patient.get('received_at', '')[:10]}</p>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("Belum ada data partisipan yang terkumpul")
    
    # Chat Analysis
    st.subheader("💬 Aktivitas Percakapan Terbaru")
    chat_sessions = live_data.get("chat_sessions", {})
    
    if chat_sessions:
        for session_id, messages in list(chat_sessions.items())[:3]:  # Show first 3 sessions
            with st.expander(f"Session {session_id} ({len(messages)} messages)"):
                for msg in messages[-5:]:  # Last 5 messages
                    timestamp = datetime.fromtimestamp(msg.get('timestamp', 0)).strftime("%H:%M:%S")
                    col1, col2 = st.columns([1, 4])
                    with col1:
                        st.text(f"{timestamp}")
                    with col2:
                        st.text_area(
                            "User:",
                            value=msg.get('user', ''),
                            height=50,
                            key=f"user_{msg.get('timestamp', 0)}",
                            disabled=True
                        )
    else:
        st.info("Belum ada aktivitas percakapan")

def show_psychologist_dashboard():
    """Dashboard Psikolog - Hybrid Version"""
    st.title("👨‍⚕️ Dashboard Psikolog INTEND")
    st.markdown("Monitoring real-time sesi wawancara interaktif")

    # Check server status
    server_online = data_manager.get_server_status()
    
    if not server_online:
        st.warning("""
        ⚠️ **Server Sedang Offline**
        
        Menampilkan data demo. Untuk koneksi real-time:
        1. Pastikan server FastAPI berjalan di `{}`
        2. Periksa koneksi jaringan
        3. Refresh halaman ini
        """.format(SERVER_URL))

    # Get live data (will return None if server offline)
    live_data = data_manager.get_dashboard_data()
    
    # Always transform data (will use mock data if server offline)
    patients_data = transform_to_patient_structure(live_data)
    
    # Sidebar navigation
    st.sidebar.header("🎯 Navigasi Pasien")
    
    if patients_data:
        selected_patient = st.sidebar.selectbox(
            "Pilih Pasien:",
            options=list(patients_data.keys())
        )
        
        patient_data = patients_data[selected_patient]
        sessions = list(patient_data["sessions"].keys())
        
        if sessions:
            selected_session = st.sidebar.selectbox(
                "Pilih Sesi:",
                options=sessions,
                index=0
            )
            
            session_data = patient_data["sessions"][selected_session]
            
            # Display patient profile
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.header(f"👤 Profil: {selected_patient}")
                demografi = patient_data["demografi"]
                
                st.markdown(f"""
                **📊 Demografi:**
                - **Usia:** {demografi['usia']} tahun
                - **Jenis Kelamin:** {demografi['jenis_kelamin']}
                - **Pekerjaan:** {demografi['pekerjaan']}
                - **Bergabung:** {demografi['tanggal_mulai'][:10]}
                """)
            
            with col2:
                st.header("📈 Statistik Sesi")
                st.metric("Emosi Dominan", session_data["emosi_dominan"])
                st.metric("Skor Sentimen", f"{session_data['skor_sentimen']:.2f}")
                st.metric("Durasi", session_data["durasi_sesi"])
            
            st.markdown("---")
            
            # Session Analysis
            st.header(f"📋 Analisis Sesi: {selected_session}")
            
            # Emotion distribution
            col1, col2 = st.columns(2)
            
            with col1:
                emotion_data = session_data["deteksi_wajah"]
                fig_emotion = px.pie(
                    values=list(emotion_data.values()),
                    names=list(emotion_data.keys()),
                    title="Distribusi Ekspresi Wajah",
                    color=list(emotion_data.keys()),
                    color_discrete_map={
                        'senang': '#2ecc71',
                        'sedih': '#3498db',
                        'netral': '#95a5a6',
                        'marah': '#e74c3c'
                    }
                )
                st.plotly_chart(fig_emotion, use_container_width=True)
            
            with col2:
                # Keyword analysis
                st.subheader("🔑 Kata Kunci Dominan")
                text = session_data["analisis_suara"]["kata_kunci"]
                if text and text.strip():
                    words = text.split()
                    word_counts = {}
                    for word in words:
                        normalized = word.strip().lower()
                        if len(normalized) > 2:  # Filter short words
                            word_counts[normalized] = word_counts.get(normalized, 0) + 1
                    
                    if word_counts:
                        top_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:8]
                        
                        # Word tags
                        tags_html = "<div style='display: flex; flex-wrap: wrap; gap: 8px; margin: 10px 0;'>"
                        for word, count in top_words:
                            tags_html += f"""
                            <span style='
                                background: #e74c3c;
                                color: white;
                                padding: 6px 12px;
                                border-radius: 15px;
                                font-size: 14px;
                                font-weight: bold;
                            '>{word} ({count})</span>
                            """
                        tags_html += "</div>"
                        st.markdown(tags_html, unsafe_allow_html=True)
                    else:
                        st.info("Tidak ada kata kunci yang cukup")
                else:
                    st.info("Tidak ada transkrip untuk analisis")
            
            # Speech Analysis
            show_speech_analysis_detail(session_data["analisis_suara"])
            
        else:
            st.info("Belum ada sesi untuk pasien ini")
    else:
        st.info("Belum ada data pasien yang tercatat")

    # Real-time Analysis Section (only if server online)
    if server_online and live_data:
        st.markdown("---")
        show_realtime_analysis(live_data)

def show_home():
    """Dashboard Utama"""
    st.markdown('<h1 class="main-header">INTEND</h1>', unsafe_allow_html=True)
    st.markdown('<h2 class="sub-header">Intelligence Doll untuk Kesehatan Mental Generasi Z</h2>', unsafe_allow_html=True)

    # Server status check
    is_online = data_manager.get_server_status()
    status_text = "🟢 LIVE" if is_online else "🔴 OFFLINE (Demo Mode)"
    status_class = "status-live" if is_online else "status-offline"
    
    st.markdown(f'<div style="text-align: center; margin-bottom: 2rem;">'
                f'<span class="{status_class}">Status Sistem: {status_text}</span>'
                f'</div>', unsafe_allow_html=True)

    # Quick stats dengan data real
    live_data = data_manager.get_dashboard_data()
    
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_patients = live_data.get("biodata_count", 0) if live_data else 1
        st.metric("Total Pasien", total_patients)

    with col2:
        total_sessions = live_data.get("chat_sessions_count", 0) if live_data else 1
        st.metric("Total Sesi", total_sessions)

    with col3:
        frames_analyzed = live_data.get("analysis_count", 0) if live_data else 0
        st.metric("Analisis Data", frames_analyzed)

    with col4:
        accuracy = "98%" if is_online else "Demo"
        st.metric("Status Sistem", accuracy)

    st.markdown("---")

    # Features overview
    st.subheader("🎯 Fitur Utama INTEND")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("""
        <div class="feature-card">
            <h3>🤖 Deteksi Ekspresi Real-time</h3>
            <p>Analisis 6 ekspresi wajah dengan AI terbaru</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3>🎤 Speech-to-Text Cerdas</h3>
            <p>Konversi percakapan dengan akurasi tinggi + analisis sentimen</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="feature-card">
            <h3>📊 Dashboard Real-time</h3>
            <p>Monitoring langsung dari sistem INTEND</p>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown("""
        <div class="feature-card">
            <h3>💬 Chatbot Terapeutik</h3>
            <p>Respons AI empatik berdasarkan kondisi emosional</p>
        </div>
        """, unsafe_allow_html=True)

    # Quick actions
    st.markdown("---")
    st.subheader("🚀 Akses Cepat")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Dashboard Psikolog", use_container_width=True):
            st.session_state.page = "📊 Dashboard Psikolog"
            st.rerun()
    
    with col2:
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.rerun()
    
    with col3:
        export_data = data_manager.get_export_data()
        if export_data:
            st.download_button(
                label="📥 Export Data",
                data=json.dumps(export_data, indent=2),
                file_name=f"intend_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )

def show_about():
    """Halaman Tentang INTEND"""
    st.title("🤖 Tentang INTEND")
    st.markdown("Intelligence Doll untuk Kesehatan Mental Generasi Z")

    st.header("🎯 Arsitektur Sistem INTEND")
    
    # System architecture
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔗 Alur Data Real-time")
        st.write("""
        ```
        User → LattePanda (Input) 
               ↓
        MSI Server (AI Processing)
               ↓  
        Streamlit (Visualization)
        ```
        
        **Komponen:**
        - 🧩 **LattePanda**: STT, Video Capture, TTS
        - 💻 **MSI Server**: Face Detection, Chatbot, Analysis
        - 🌐 **Streamlit**: Real-time Dashboard
        """)
    
    with col2:
        st.subheader("🛠️ Teknologi yang Digunakan")
        st.write("""
        - **Backend**: FastAPI + WebSocket
        - **AI Models**: MediaPipe, SpeechRecognition
        - **Frontend**: Streamlit + Plotly
        - **Communication**: REST API
        - **Hardware**: LattePanda V1, Webcam, Mic
        """)

    st.markdown("---")
    
    st.header("📈 Status Sistem Saat Ini")
    
    # Real-time system status
    live_data = data_manager.get_dashboard_data()
    is_online = data_manager.get_server_status()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        status_color = "🟢" if is_online else "🔴"
        st.metric("Server Status", f"{status_color} {'Online' if is_online else 'Offline'}")
    
    with col2:
        biodata_count = live_data.get("biodata_count", 0) if live_data else 0
        st.metric("Data Pasien", biodata_count)
    
    with col3:
        analysis_count = live_data.get("analysis_count", 0) if live_data else 0
        st.metric("Analisis Data", analysis_count)
    
    with col4:
        last_update = data_manager.last_update.strftime("%H:%M") if data_manager.last_update else "N/A"
        st.metric("Update Terakhir", last_update)

# Initialize session state for page navigation
if 'page' not in st.session_state:
    st.session_state.page = "🏠 Dashboard Utama"

# Sidebar navigation
st.sidebar.title("🧭 Navigasi INTEND")
st.sidebar.markdown("---")

# Server configuration
st.sidebar.subheader("⚙️ Konfigurasi Server")
server_url = st.sidebar.text_input("Server URL", SERVER_URL)
if server_url != SERVER_URL:
    SERVER_URL = server_url
    data_manager = INTENDDataManager(SERVER_URL)

# Server status in sidebar
server_status = data_manager.get_server_status()
status_color = "🟢" if server_status else "🔴"
st.sidebar.markdown(f"**Status Server:** {status_color} {'Online' if server_status else 'Offline'}")

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
    show_psychologist_dashboard()
elif page == "🤖 Tentang INTEND":
    show_about()

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #7f8c8d;'>"
    "INTEND - Intelligence Doll © 2025 | Powered by FastAPI + Streamlit | Universitas Airlangga"
    "</div>",
    unsafe_allow_html=True
)

# Auto-refresh untuk halaman tertentu
if page in ["🏠 Dashboard Utama", "📊 Dashboard Psikolog"]:
    time.sleep(REFRESH_INTERVAL)
    st.rerun()
