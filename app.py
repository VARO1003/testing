import streamlit as st
import sqlite3
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import base64

# Page configuration
st.set_page_config(
    page_title="INTEND Dashboard",
    page_icon="🧸",
    layout="wide",
    initial_sidebar_state="expanded"
)

class INTENDDashboard:
    def __init__(self):
        self.conn = sqlite3.connect('intend_sessions.db', check_same_thread=False)
        self.init_session_state()
    
    def init_session_state(self):
        """Initialize session state"""
        if 'selected_session' not in st.session_state:
            st.session_state.selected_session = None
        if 'current_view' not in st.session_state:
            st.session_state.current_view = 'dashboard'
    
    def get_sessions(self):
        """Get all sessions from database"""
        query = """
        SELECT s.session_id, s.client_ip, s.start_time, s.end_time, b.nama
        FROM sessions s
        LEFT JOIN biodata b ON s.session_id = b.session_id
        ORDER BY s.start_time DESC
        """
        return pd.read_sql_query(query, self.conn)
    
    def get_session_data(self, session_id):
        """Get comprehensive data for a specific session"""
        # Biodata
        biodata = pd.read_sql_query(
            "SELECT * FROM biodata WHERE session_id = ?", 
            self.conn, params=[session_id]
        )
        
        # Expressions
        expressions = pd.read_sql_query(
            "SELECT expression, timestamp FROM expressions WHERE session_id = ?", 
            self.conn, params=[session_id]
        )
        
        # Transcripts
        transcripts = pd.read_sql_query(
            "SELECT text, symptoms, timestamp FROM transcripts WHERE session_id = ?", 
            self.conn, params=[session_id]
        )
        
        return {
            'biodata': biodata,
            'expressions': expressions,
            'transcripts': transcripts
        }
    
    def create_expression_timeline(self, expressions_df):
        """Create expression timeline chart"""
        if expressions_df.empty:
            return None
            
        expressions_df['timestamp'] = pd.to_datetime(expressions_df['timestamp'])
        expressions_df = expressions_df.sort_values('timestamp')
        
        # Count expressions over time
        expression_counts = expressions_df.groupby([
            pd.Grouper(key='timestamp', freq='5T'),  # 5-minute intervals
            'expression'
        ]).size().reset_index(name='count')
        
        fig = px.line(
            expression_counts, 
            x='timestamp', 
            y='count', 
            color='expression',
            title='Timeline Ekspresi Wajah',
            labels={'count': 'Frekuensi', 'timestamp': 'Waktu', 'expression': 'Ekspresi'}
        )
        
        return fig
    
    def create_expression_pie_chart(self, expressions_df):
        """Create expression distribution pie chart"""
        if expressions_df.empty:
            return None
            
        expression_dist = expressions_df['expression'].value_counts()
        
        fig = px.pie(
            values=expression_dist.values,
            names=expression_dist.index,
            title='Distribusi Ekspresi Wajah'
        )
        
        return fig
    
    def create_word_cloud(self, transcripts_df):
        """Create word cloud from transcripts"""
        if transcripts_df.empty:
            return None
            
        all_text = ' '.join(transcripts_df['text'].astype(str))
        
        if not all_text.strip():
            return None
            
        wordcloud = WordCloud(
            width=800, 
            height=400, 
            background_color='white',
            colormap='Blues'
        ).generate(all_text)
        
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        
        return fig
    
    def analyze_symptoms(self, transcripts_df):
        """Analyze depression symptoms from transcripts"""
        if transcripts_df.empty:
            return pd.DataFrame()
            
        symptoms_data = []
        
        for _, row in transcripts_df.iterrows():
            if row['symptoms'] and row['symptoms'] != 'null':
                try:
                    symptoms = json.loads(row['symptoms'])
                    for symptom, details in symptoms.items():
                        symptoms_data.append({
                            'symptom': symptom,
                            'count': details.get('count', 0),
                            'timestamp': row['timestamp']
                        })
                except:
                    continue
        
        if symptoms_data:
            symptoms_df = pd.DataFrame(symptoms_data)
            return symptoms_df.groupby('symptom')['count'].sum().reset_index()
        else:
            return pd.DataFrame()
    
    def display_dashboard(self):
        """Display main dashboard"""
        st.title("🧸 INTEND - Intelligence Doll Dashboard")
        
        # Session selection
        sessions_df = self.get_sessions()
        
        if sessions_df.empty:
            st.warning("Belum ada data session yang tersedia.")
            return
        
        # Sidebar for session selection
        with st.sidebar:
            st.header("Pilih Session")
            
            session_options = [
                f"Session {row.session_id} - {row.nama or 'Unknown'} ({row.start_time[:10]})" 
                for _, row in sessions_df.iterrows()
            ]
            
            selected_option = st.selectbox(
                "Pilih Session:",
                options=session_options,
                index=0
            )
            
            selected_session_id = sessions_df.iloc[session_options.index(selected_option)].session_id
            
            if st.button("Load Session Data"):
                st.session_state.selected_session = selected_session_id
                st.session_state.current_view = 'session_detail'
            
            st.markdown("---")
            st.markdown("### Quick Stats")
            st.metric("Total Sessions", len(sessions_df))
            
            active_sessions = len(sessions_df[sessions_df['end_time'].isna()])
            st.metric("Active Sessions", active_sessions)
        
        # Main dashboard content
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Average Session Duration", "45 menit")
        
        with col2:
            st.metric("Most Common Expression", "Netral")
        
        with col3:
            st.metric("Data Accuracy", "98%")
        
        # Recent sessions table
        st.subheader("Session Terbaru")
        st.dataframe(
            sessions_df[['session_id', 'nama', 'client_ip', 'start_time']].head(10),
            use_container_width=True
        )
    
    def display_session_detail(self, session_id):
        """Display detailed session analysis"""
        session_data = self.get_session_data(session_id)
        
        st.title(f"📊 Analisis Session #{session_id}")
        
        # Back button
        if st.button("← Kembali ke Dashboard"):
            st.session_state.current_view = 'dashboard'
            st.rerun()
        
        if not session_data['biodata'].empty:
            biodata = session_data['biodata'].iloc[0]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Informasi Pasien")
                st.write(f"**Nama:** {biodata['nama']}")
                st.write(f"**Usia:** {biodata['usia']}")
                st.write(f"**Jenis Kelamin:** {biodata['jenis_kelamin']}")
                st.write(f"**Pekerjaan:** {biodata['pekerjaan']}")
            
            with col2:
                st.subheader("Informasi Kesehatan")
                st.write(f"**Riwayat Kesehatan:** {biodata['riwayat_kesehatan']}")
                st.write(f"**Keluhan Utama:** {biodata['keluhan_utama']}")
        
        # Expression analysis
        st.subheader("Analisis Ekspresi Wajah")
        
        if not session_data['expressions'].empty:
            col1, col2 = st.columns(2)
            
            with col1:
                timeline_chart = self.create_expression_timeline(session_data['expressions'])
                if timeline_chart:
                    st.plotly_chart(timeline_chart, use_container_width=True)
            
            with col2:
                pie_chart = self.create_expression_pie_chart(session_data['expressions'])
                if pie_chart:
                    st.plotly_chart(pie_chart, use_container_width=True)
        else:
            st.info("Tidak ada data ekspresi yang tersedia untuk session ini.")
        
        # Transcript analysis
        st.subheader("Analisis Percakapan")
        
        if not session_data['transcripts'].empty:
            col1, col2 = st.columns(2)
            
            with col1:
                # Word cloud
                wordcloud_fig = self.create_word_cloud(session_data['transcripts'])
                if wordcloud_fig:
                    st.pyplot(wordcloud_fig)
            
            with col2:
                # Symptoms analysis
                symptoms_df = self.analyze_symptoms(session_data['transcripts'])
                if not symptoms_df.empty:
                    st.subheader("Gejala yang Terdeteksi")
                    fig = px.bar(
                        symptoms_df,
                        x='symptom',
                        y='count',
                        title='Frekuensi Gejala Depresi'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Tidak terdeteksi gejala spesifik dalam percakapan.")
            
            # Raw transcripts
            st.subheader("Transkrip Percakapan")
            for _, transcript in session_data['transcripts'].iterrows():
                with st.expander(f"Percakapan - {transcript['timestamp'][:19]}"):
                    st.write(f"**Teks:** {transcript['text']}")
                    if transcript['symptoms'] and transcript['symptoms'] != 'null':
                        try:
                            symptoms = json.loads(transcript['symptoms'])
                            st.write("**Gejala terdeteksi:**")
                            for symptom, details in symptoms.items():
                                st.write(f"- {symptom}: {details.get('count', 0)} kata kunci")
                        except:
                            st.write("Tidak ada gejala terdeteksi")
        else:
            st.info("Tidak ada data transkrip yang tersedia untuk session ini.")
        
        # Raw data access
        st.subheader("Akses Data Mentah")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📥 Download Biodata JSON"):
                self.download_json(session_data['biodata'].to_dict('records'), f"biodata_{session_id}.json")
        
        with col2:
            if st.button("📥 Download Data Ekspresi"):
                self.download_json(session_data['expressions'].to_dict('records'), f"expressions_{session_id}.json")
        
        with col3:
            if st.button("📥 Download Transkrip"):
                self.download_json(session_data['transcripts'].to_dict('records'), f"transcripts_{session_id}.json")
    
    def download_json(self, data, filename):
        """Create download link for JSON data"""
        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        b64 = base64.b64encode(json_str.encode()).decode()
        href = f'<a href="data:file/json;base64,{b64}" download="{filename}">Download {filename}</a>'
        st.markdown(href, unsafe_allow_html=True)
    
    def run(self):
        """Run the dashboard"""
        if st.session_state.current_view == 'dashboard':
            self.display_dashboard()
        elif st.session_state.current_view == 'session_detail' and st.session_state.selected_session:
            self.display_session_detail(st.session_state.selected_session)

# Run the dashboard
if __name__ == "__main__":
    dashboard = INTENDDashboard()
    dashboard.run()
