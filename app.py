# -*- coding: utf-8 -*-
"""
INTEND Dashboard Streamlit - Terhubung ke Server Lokal
Website untuk monitoring dan analisis data pasien secara real-time
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
import json
import time
import warnings
warnings.filterwarnings('ignore')

# Konfigurasi
SERVER_URL = "http://localhost:5000"  # Ganti dengan IP laptop MSI jika perlu
REFRESH_INTERVAL = 5  # seconds

# Custom CSS untuk styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #2c3e50;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: bold;
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
        margin: 0.5rem 0;
    }
    .feature-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin: 0.5rem;
        border: 1px solid #e0e0e0;
    }
    .speech-transcript {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #e74c3c;
        margin: 0.5rem 0;
        font-family: monospace;
    }
    .emotion-happy { color: #2ecc71; font-weight: bold; }
    .emotion-sad { color: #3498db; font-weight: bold; }
    .emotion-angry { color: #e74c3c; font-weight: bold; }
    .emotion-neutral { color: #95a5a6; font-weight: bold; }
    .emotion-calm { color: #9b59b6; font-weight: bold; }
    
    /* Loading spinner */
    .loading-spinner {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 2rem;
    }
</style>
""", unsafe_allow_html=True)

class INTENDDashboard:
    def __init__(self, server_url):
        self.server_url = server_url
        self.connection_status = False
        self.last_update = None
        
    def check_connection(self):
        """Cek koneksi ke server"""
        try:
            response = requests.get(f"{self.server_url}/api/health", timeout=5)
            if response.status_code == 200:
                self.connection_status = True
                return True
            else:
                self.connection_status = False
                return False
        except:
            self.connection_status = False
            return False
    
    def get_patients(self):
        """Ambil data pasien dari server"""
        try:
            response = requests.get(f"{self.server_url}/api/data/patients", timeout=10)
            if response.status_code == 200:
                return response.json().get('patients', [])
            else:
                st.error(f"Error fetching patients: {response.text}")
                return []
        except Exception as e:
            st.error(f"Connection error: {str(e)}")
            return []
    
    def get_patient_sessions(self, patient_id):
        """Ambil sesi untuk pasien tertentu"""
        try:
            response = requests.get(f"{self.server_url}/api/data/sessions/{patient_id}", timeout=10)
            if response.status_code == 200:
                return response.json().get('sessions', [])
            else:
                return []
        except Exception as e:
            st.error(f"Error fetching sessions: {str(e)}")
            return []
    
    def get_session_data(self, session_id):
        """Ambil data lengkap sesi"""
        try:
            response = requests.get(f"{self.server_url}/api/data/session/{session_id}", timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                return None
        except Exception as e:
            st.error(f"Error fetching session data: {str(e)}")
            return None
    
    def get_realtime_analytics(self, session_id):
        """Ambil data real-time untuk sesi aktif"""
        try:
            response = requests.get(f"{self.server_url}/api/analytics/realtime/{session_id}", timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                return None
        except Exception as e:
            return None
    
    def get_session_files(self, session_id):
        """Ambil daftar file untuk sesi"""
        try:
            response = requests.get(f"{self.server_url}/api/files/session/{session_id}", timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                return {}
        except Exception as e:
            st.error(f"Error fetching session files: {str(e)}")
            return {}

# Initialize dashboard
dashboard = INTENDDashboard(SERVER_URL)

def emotion_color(emotion):
    """Return color class for emotion"""
    color_map = {
        'happy': 'emotion-happy',
        'sad': 'emotion-sad', 
        'angry': 'emotion-angry',
        'neutral': 'emotion-neutral',
        'calm': 'emotion-calm'
    }
    return color_map.get(emotion, 'emotion-neutral')

def show_loading_spinner():
    """Show loading spinner"""
    st.markdown("""
    <div class="loading-spinner">
        <div style="text-align: center;">
            <div>🔄 Loading data from INTEND Server...</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def show_connection_status():
    """Show server connection status"""
    if dashboard.check_connection():
        st.sidebar.success("✅ Terhubung ke INTEND Server")
        health_response = requests.get(f"{SERVER_URL}/api/health", timeout=5)
        if health_response.status_code == 200:
            health_data = health_response.json()
            st.sidebar.metric("Active Sessions", health_data.get('active_sessions', 0))
            st.sidebar.metric("Storage Usage", f"{health_data.get('storage_usage', 0)} MB")
    else:
        st.sidebar.error("❌ Tidak dapat terhubung ke server")
        st.sidebar.info("Pastikan server berjalan di http://localhost:5000")

def show_home():
    """Dashboard Utama"""
    st.markdown('<h1 class="main-header">INTEND</h1>', unsafe_allow_html=True)
    st.markdown('<h2 class="sub-header">Intelligence Doll untuk Kesehatan Mental Generasi Z</h2>', unsafe_allow_html=True)
    
    # Quick stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        patients = dashboard.get_patients()
        st.metric("Total Pasien", len(patients))
    
    with col2:
        total_sessions = 0
        for patient in patients:
            sessions = dashboard.get_patient_sessions(patient.get('patient_id'))
            total_sessions += len(sessions)
        st.metric("Total Sesi", total_sessions)
    
    with col3:
        # Active sessions dari health endpoint
        try:
            health_response = requests.get(f"{SERVER_URL}/api/health", timeout=5)
            if health_response.status_code == 200:
                active_sessions = health_response.json().get('active_sessions', 0)
                st.metric("Sesi Aktif", active_sessions)
            else:
                st.metric("Sesi Aktif", 0)
        except:
            st.metric("Sesi Aktif", 0)
    
    with col4:
        st.metric("Server Status", "Online" if dashboard.connection_status else "Offline")
    
    st.markdown("---")
    
    # Features overview
    st.subheader("🎯 Fitur Utama INTEND")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h3>🤖 Deteksi Ekspresi Wajah</h3>
            <p>Analisis real-time 6 fitur geometris wajah dengan MediaPipe</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3>🎤 Analisis Suara</h3>
            <p>Speech-to-text + analisis sentimen dan gejala klinis</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <h3>📊 Dashboard Real-time</h3>
            <p>Monitoring data emosional pasien secara live</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="feature-card">
            <h3>💬 Interaksi Empatik</h3>
            <p>Respons AI yang personal berdasarkan kondisi emosional</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Recent activity
    st.subheader("📈 Aktivitas Terkini")
    
    if patients:
        # Show recent sessions
        recent_sessions = []
        for patient in patients[:3]:  # Limit to 3 patients
            sessions = dashboard.get_patient_sessions(patient.get('patient_id'))
            for session in sessions[:2]:  # Limit to 2 sessions per patient
                recent_sessions.append({
                    'patient': patient.get('nama', 'Unknown'),
                    'session_id': session.get('session_id'),
                    'date': session.get('start_time', '')[:10],
                    'duration': f"{session.get('duration_seconds', 0) // 60}m",
                    'dominant_emotion': session.get('dominant_emotion', 'unknown')
                })
        
        if recent_sessions:
            df_sessions = pd.DataFrame(recent_sessions)
            st.dataframe(df_sessions, use_container_width=True)
        else:
            st.info("Belum ada sesi yang tercatat")
    else:
        st.info("Belum ada pasien terdaftar")

def show_speech_analysis_detail(speech_data):
    """Tampilkan analisis detail speech recognition"""
    st.subheader("🎤 Analisis Percakapan Detail")
    
    # Tab untuk berbagai analisis
    tab1, tab2, tab3, tab4 = st.tabs(["📝 Transkrip", "🔍 Analisis Sentimen", "🩺 Gejala Klinis", "🗣️ Pola Bicara"])
    
    with tab1:
        # Transkrip lengkap
        st.markdown("### 📝 Transkrip Percakapan")
        transcript = speech_data.get("transcript", "")
        if transcript:
            st.markdown(f'<div class="speech-transcript">{transcript}</div>', unsafe_allow_html=True)
        else:
            st.info("Tidak ada transkrip yang tersedia")
    
    with tab2:
        # Analisis sentimen
        st.markdown("### 🔍 Analisis Sentimen")
        sentiment = speech_data.get("sentiment_analysis", {})
        if sentiment:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                score = sentiment.get("sentiment_score", 0)
                st.metric("Skor Sentimen", f"{score:.3f}")
                
                # Progress bar sentiment
                sentiment_progress = (score + 1) / 2  # Convert -1 to 1 range to 0 to 1
                st.progress(sentiment_progress)
                
                category = sentiment.get("sentiment_category", "Tidak diketahui")
                st.write(f"**Kategori:** {category}")
            
            with col2:
                positive = sentiment.get("positive_words", 0)
                st.metric("Kata Positif", positive)
            
            with col3:
                negative = sentiment.get("negative_words", 0)
                st.metric("Kata Negatif", negative)
            
            with col4:
                total_words = sentiment.get("word_count", 0)
                st.metric("Total Kata", total_words)
            
            # Sentiment chart
            sentiment_counts = [positive, negative, total_words - positive - negative]
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
        symptoms = sentiment.get("detected_symptoms", {})
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
        total_words = sentiment.get("word_count", 0)
        
        if total_words > 0:
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Total Kata", total_words)
                
                # Word count indicator
                if total_words < 50:
                    st.warning("⏱️ Pasien sedikit bicara")
                elif total_words < 200:
                    st.success("⏱️ Pola bicara normal")
                else:
                    st.info("⏱️ Pasien banyak bicara")
            
            with col2:
                speaking_rate = total_words / 10  # Assuming 10 minutes session
                st.metric("Perkiraan Kata/menit", f"{speaking_rate:.1f}")
            
            # Speech pattern insights
            st.markdown("#### 💡 Insight Pola Bicara")
            if total_words < 30:
                st.info("Pasien mungkin mengalami kesulitan mengekspresikan perasaan")
            elif sentiment.get("negative_words", 0) > sentiment.get("positive_words", 0) * 2:
                st.warning("Percakapan didominasi oleh kata-kata negatif")
        else:
            st.info("Analisis pola bicara belum tersedia")

def show_dashboard():
    """Dashboard Psikolog - Monitoring Pasien"""
    st.title("👨‍⚕️ Dashboard Psikolog INTEND")
    st.markdown("Monitoring dan analisis data pasien secara real-time")
    
    # Dapatkan data pasien dari server
    patients = dashboard.get_patients()
    
    if not patients:
        st.warning("Tidak ada data pasien yang ditemukan. Pastikan server lokal berjalan dan ada pasien terdaftar.")
        return
    
    # Buat mapping untuk dropdown
    patient_options = {f"{p.get('nama', 'Unknown')} (ID: {p.get('patient_id', 'N/A')})": p for p in patients}
    
    # Sidebar navigation
    st.sidebar.header("🎯 Navigasi Pasien")
    selected_patient_label = st.sidebar.selectbox(
        "Pilih Pasien:",
        options=list(patient_options.keys())
    )
    
    if not selected_patient_label:
        st.info("Pilih pasien dari sidebar.")
        return
    
    selected_patient = patient_options[selected_patient_label]
    patient_id = selected_patient.get('patient_id')
    
    # Dapatkan sesi pasien
    sessions = dashboard.get_patient_sessions(patient_id)
    
    # Tampilkan info pasien
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Nama Pasien", selected_patient.get('nama', 'Unknown'))
    with col2:
        st.metric("Usia", selected_patient.get('usia', 'N/A'))
    with col3:
        st.metric("Total Sesi", len(sessions))
    
    st.markdown("---")
    
    if not sessions:
        st.info("Belum ada sesi untuk pasien ini.")
        return
    
    # Pilih sesi
    session_options = {s.get('session_id'): s for s in sessions}
    selected_session_id = st.sidebar.selectbox(
        "Pilih Sesi:",
        options=list(session_options.keys())
    )
    
    # Session analysis
    if selected_session_id:
        # Dapatkan data sesi dari server
        with st.spinner("Memuat data sesi..."):
            server_session_data = dashboard.get_session_data(selected_session_id)
        
        if server_session_data:
            selected_session = session_options[selected_session_id]
            
            st.header(f"📊 Analisis Sesi: {selected_session_id}")
            st.write(f"**Waktu Sesi:** {selected_session.get('start_time', 'N/A')}")
            st.write(f"**Durasi:** {selected_session.get('duration_seconds', 0) // 60} menit")
            
            # Key metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                dominant_emotion = selected_session.get('dominant_emotion', 'unknown')
                st.metric("Emosi Dominan", dominant_emotion)
            
            with col2:
                avg_sentiment = selected_session.get('average_sentiment', 0)
                st.metric("Rata-rata Sentimen", f"{avg_sentiment:.3f}")
            
            with col3:
                total_face = selected_session.get('total_face_data', 0)
                st.metric("Data Ekspresi", total_face)
            
            with col4:
                total_speech = selected_session.get('total_speech_data', 0)
                st.metric("Data Percakapan", total_speech)
            
            # Visualization row
            col1, col2 = st.columns(2)
            
            with col1:
                # Emotion distribution chart
                st.subheader("📈 Distribusi Ekspresi Wajah")
                emotion_dist = selected_session.get('emotion_distribution', {})
                if emotion_dist:
                    fig_emotion = px.pie(
                        values=list(emotion_dist.values()),
                        names=list(emotion_dist.keys()),
                        title="Persentase Ekspresi Wajah",
                        color=list(emotion_dist.keys()),
                        color_discrete_map={
                            'happy': '#2ecc71',
                            'sad': '#3498db',
                            'angry': '#e74c3c',
                            'neutral': '#95a5a6',
                            'calm': '#9b59b6'
                        }
                    )
                    st.plotly_chart(fig_emotion, use_container_width=True)
                else:
                    st.info("Tidak ada data distribusi emosi")
            
            with col2:
                # Key insights
                st.subheader("💡 Insights Klinis")
                insights = selected_session.get('key_insights', [])
                if insights:
                    for insight in insights:
                        st.info(f"• {insight}")
                else:
                    st.info("Tidak ada insights yang tersedia untuk sesi ini")
            
            # Speech analysis section
            speech_data_list = server_session_data.get('speech_data', [])
            if speech_data_list:
                st.markdown("---")
                st.subheader("🎤 Analisis Percakapan")
                
                # Tampilkan transcript terbaru
                latest_speech = speech_data_list[-1] if speech_data_list else {}
                show_speech_analysis_detail(latest_speech)
            
            # File access section
            st.markdown("---")
            st.subheader("📁 Akses File Data Mentah")
            
            with st.spinner("Memuat daftar file..."):
                session_files = dashboard.get_session_files(selected_session_id)
            
            if session_files:
                col1, col2, col3 = st.columns(3)
                
                # Face data files
                with col1:
                    st.write("**Data Ekspresi Wajah:**")
                    face_files = session_files.get('face', [])
                    for file in face_files[:3]:  # Show first 3 files
                        st.write(f"• {file['filename']}")
                
                # Speech data files  
                with col2:
                    st.write("**Data Percakapan:**")
                    speech_files = session_files.get('speech', [])
                    for file in speech_files[:3]:
                        st.write(f"• {file['filename']}")
                
                # Session summary
                with col3:
                    st.write("**Summary Sesi:**")
                    summary_files = session_files.get('session_summary', [])
                    for file in summary_files:
                        st.write(f"• {file['filename']}")
                
                # Download buttons
                st.markdown("---")
                st.subheader("📥 Download Data")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("📊 Download Summary JSON", key="download_summary"):
                        if summary_files:
                            file_url = f"{SERVER_URL}{summary_files[0]['download_url']}"
                            st.markdown(f'[Download Summary]({file_url})', unsafe_allow_html=True)
                
                with col2:
                    if st.button("🎭 Download Data Ekspresi", key="download_face"):
                        if face_files:
                            # Create a combined download link or individual
                            st.info("Gunakan link di atas untuk download file individual")
                
                with col3:
                    if st.button("🗣️ Download Data Percakapan", key="download_speech"):
                        if speech_files:
                            st.info("Gunakan link di atas untuk download file individual")
            
            else:
                st.info("Tidak ada file data yang tersedia untuk sesi ini")
        
        else:
            st.error("Gagal memuat data sesi dari server")

def show_realtime_monitoring():
    """Real-time Monitoring untuk Sesi Aktif"""
    st.title("🔴 Monitoring Real-time INTEND")
    st.markdown("Monitor sesi terapi yang sedang berlangsung secara live")
    
    # Cek sesi aktif
    try:
        health_response = requests.get(f"{SERVER_URL}/api/health", timeout=5)
        if health_response.status_code == 200:
            active_sessions_count = health_response.json().get('active_sessions', 0)
            
            if active_sessions_count == 0:
                st.info("Tidak ada sesi aktif yang berjalan.")
                st.write("Pastikan INTEND Doll sedang digunakan untuk sesi terapi.")
                return
            
            st.success(f"🎯 {active_sessions_count} sesi aktif terdeteksi")
            
            # Untuk simplicity, monitor session pertama yang aktif
            # Dalam implementasi real, kita perlu mendapatkan list session aktif
            patients = dashboard.get_patients()
            if patients:
                # Cari sesi aktif untuk pasien pertama
                patient_id = patients[0].get('patient_id')
                sessions = dashboard.get_patient_sessions(patient_id)
                
                if sessions:
                    latest_session = sessions[0]  # Asumsi session terbaru adalah yang aktif
                    session_id = latest_session.get('session_id')
                    
                    # Real-time monitoring
                    st.subheader(f"📊 Live Monitoring - Sesi: {session_id}")
                    
                    # Auto-refresh
                    refresh = st.checkbox("🔄 Auto-refresh setiap 5 detik", value=True)
                    
                    if refresh:
                        st.write("**Data akan diperbarui otomatis...**")
                        
                        # Placeholder untuk real-time data
                        placeholder = st.empty()
                        
                        # Simulasi real-time updates
                        for i in range(10):  # Refresh 10 kali
                            if refresh:
                                with placeholder.container():
                                    # Get real-time analytics
                                    realtime_data = dashboard.get_realtime_analytics(session_id)
                                    
                                    if realtime_data:
                                        col1, col2, col3, col4 = st.columns(4)
                                        
                                        with col1:
                                            emotion = realtime_data.get('latest_emotion', 'unknown')
                                            st.metric("Emosi Terkini", emotion)
                                        
                                        with col2:
                                            sentiment = realtime_data.get('latest_sentiment', 0)
                                            st.metric("Sentimen", f"{sentiment:.3f}")
                                        
                                        with col3:
                                            face_data = realtime_data.get('total_face_data', 0)
                                            st.metric("Data Wajah", face_data)
                                        
                                        with col4:
                                            speech_data = realtime_data.get('total_speech_data', 0)
                                            st.metric("Data Percakapan", speech_data)
                                        
                                        # Emotion timeline
                                        st.subheader("📈 Timeline Emosi")
                                        emotion_timeline = realtime_data.get('emotion_timeline', [])
                                        if emotion_timeline:
                                            timeline_df = pd.DataFrame({
                                                'Waktu': range(len(emotion_timeline)),
                                                'Emosi': emotion_timeline
                                            })
                                            fig_timeline = px.line(timeline_df, x='Waktu', y='Emosi', 
                                                                 title='Perubahan Emosi 10 Detik Terakhir')
                                            st.plotly_chart(fig_timeline, use_container_width=True)
                                    
                                    time.sleep(5)  # Refresh every 5 seconds
                            else:
                                break
                    else:
                        st.info("Aktifkan auto-refresh untuk monitoring real-time")
            
        else:
            st.error("Tidak dapat terhubung ke server")
    
    except Exception as e:
        st.error(f"Error monitoring real-time: {str(e)}")

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
    
    # Architecture diagram
    st.subheader("🏗️ Arsitektur Sistem")
    st.image("https://via.placeholder.com/800x400/3498db/ffffff?text=INTEND+System+Architecture", 
             caption="Arsitektur Client-Server INTEND")
    
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

def main():
    """Main function"""
    # Sidebar navigation
    st.sidebar.title("🧭 Navigasi INTEND")
    
    # Show connection status
    show_connection_status()
    
    # Main page selection
    page = st.sidebar.radio(
        "Pilih Halaman:", 
        [
            "🏠 Dashboard Utama",
            "📊 Dashboard Psikolog", 
            "🔴 Monitoring Real-time",
            "🤖 Tentang INTEND"
        ]
    )
    
    # Page routing
    if page == "🏠 Dashboard Utama":
        show_home()
    elif page == "📊 Dashboard Psikolog":
        show_dashboard()
    elif page == "🔴 Monitoring Real-time":
        show_realtime_monitoring()
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

if __name__ == "__main__":
    main()
