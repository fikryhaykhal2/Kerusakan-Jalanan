import streamlit as st
import pandas as pd
import numpy as np

# 1. Konfigurasi Utama & Ngrok
NGROK_URL = "https://ae9d063e3834.ngrok-free.app" 

st.set_page_config(
    page_title="Monitoring Jalan Rusak v2",
    page_icon="🚧",
    layout="wide"
)

# 2. Custom CSS
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stMetric"] {
        background-color: #1f2937; 
        border: 1px solid #374151;
        padding: 20px;
        border-radius: 12px;
    }
    div[data-testid="stMetricLabel"] { color: #9ca3af !important; font-weight: bold; }
    div[data-testid="stMetricValue"] { color: #ffffff !important; }
    h1, h2, h3 { color: #ffffff; }
    </style>
    """, unsafe_allow_html=True)

# 3. Sidebar
with st.sidebar:
    st.title("⚙️ Kontrol Panel")
    st.info("Sistem Monitoring Open-Vocabulary")
    st.markdown(f"**Server Model:** `{NGROK_URL}`")
    st.warning("⚠️ Buka URL Ngrok di atas dan klik 'Visit Site' jika gambar tidak muncul.")
    if st.button("🔄 Segarkan Data"):
        st.cache_data.clear()
        st.rerun()

# 4. Fungsi Load Data
@st.cache_data(ttl=60)
def load_data():
    sheet_url = "https://docs.google.com/spreadsheets/d/115rzE-b9GzzM4onP2mbWN6rDohkHqPJo1Ptn1bkm-Z0/export?format=csv"
    data = pd.read_csv(sheet_url)
    
    # BERSIHKAN NAMA KOLOM (Sangat Penting untuk Header)
    data.columns = [str(c).strip().lower() for c in data.columns]
    
    # --- PROSES KOLOM TANGGAL ---
    if 'tanggal' in data.columns:
        data['tanggal'] = pd.to_datetime(data['tanggal'], errors='coerce')
    
    # --- PROSES KOLOM CONFIDENCE ---
    if 'confidence' in data.columns:
        data['confidence'] = data['confidence'].astype(str).str.replace(',', '.')
        data['confidence'] = pd.to_numeric(data['confidence'], errors='coerce').fillna(0)
        data['confidence'] = data['confidence'].apply(lambda x: x/10000 if x > 100 else (x/100 if x > 1 else x))
    
    # --- PROSES KOLOM GAMBAR (PRATINJAU) ---
    if 'link foto' in data.columns:
        base_url = NGROK_URL.strip().rstrip('/')
        data['pratinjau'] = data['link foto'].apply(
            lambda x: f"{base_url}/static/images/{str(x).strip()}" 
            if str(x).strip().lower() not in ['nan', 'none', ''] else None
        )
        
    return data

try:
    df = load_data()

    # --- Header Dashboard ---
    st.title("🚧 Dashboard Pelaporan Jalan Rusak")
    st.write(f"Sistem Deteksi Real-time")
    
    # --- Row 1: Metrik Utama ---
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Laporan", f"{len(df)} 📋")
    with col2:
        # Gunakan nama kolom yang sudah di-lowercase ('jenis kerusakan')
        unseen_count = 0
        if 'jenis kerusakan' in df.columns:
            unseen_count = len(df[df['jenis kerusakan'].isin(['Jalanan Berlumpur', 'Bukan Jalanan'])])
        st.metric("Deteksi Unseen", f"{unseen_count} ✨")
    with col3:
        top_issue = df['jenis kerusakan'].mode()[0] if not df.empty and 'jenis kerusakan' in df.columns else "N/A"
        st.metric("Isu Terdominan", top_issue)
    with col4:
        st.metric("Status Server", "Aktif ✅")

    st.markdown("---")

    # --- Row 2: Tabel dengan Header Terjamin Muncul ---
    st.subheader("📋 Daftar Riwayat Laporan Lengkap")
    
    # Konfigurasi Kolom yang SINKRON dengan nama kolom data
    st.data_editor(
        df,
        column_config={
            "pratinjau": st.column_config.ImageColumn("Foto Kejadian", width="medium"),
            "jenis kerusakan": st.column_config.TextColumn("Jenis Kerusakan"),
            "confidence": st.column_config.NumberColumn("Confidence", format="%.2f%%"),
            "tanggal": st.column_config.DatetimeColumn("Waktu Laporan"),
            "link foto": None # Kolom ini disembunyikan
        },
        use_container_width=True,
        hide_index=True,
        disabled=True
    )

except Exception as e:
    st.error(f"Gagal memuat dashboard. Error: {e}")
