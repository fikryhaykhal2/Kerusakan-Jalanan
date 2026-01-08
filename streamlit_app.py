import streamlit as st
import pandas as pd
import numpy as np

# 1. Konfigurasi Utama
# GANTI URL INI sesuai URL Ngrok terbaru Anda
NGROK_URL = "hhttps://4d9ba8690bb9.ngrok-free.app" 

st.set_page_config(
    page_title="Monitoring Jalan Rusak Final",
    page_icon="🚧",
    layout="wide"
)

# 2. Custom CSS (Gaya Gelap)
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stMetric"] {
        background-color: #1f2937; 
        border: 1px solid #374151;
        padding: 20px;
        border-radius: 12px;
    }
    h1, h2, h3 { color: #ffffff; }
    </style>
    """, unsafe_allow_html=True)

# 3. Sidebar
with st.sidebar:
    st.title("⚙️ Kontrol Panel")
    st.markdown(f"**Model:** `Fine-tuned CLIP` ✅")
    st.markdown(f"**Server:** `{NGROK_URL}`")
    if st.button("🔄 Segarkan Data"):
        st.cache_data.clear()
        st.rerun()

# 4. Fungsi Load Data (Disesuaikan dengan format app.py final)
@st.cache_data(ttl=60)
def load_data():
    sheet_url = "https://docs.google.com/spreadsheets/d/115rzE-b9GzzM4onP2mbWN6rDohkHqPJo1Ptn1bkm-Z0/export?format=csv"
    data = pd.read_csv(sheet_url)
    
    # Standarisasi kolom ke huruf kecil
    data.columns = [str(c).strip().lower() for c in data.columns]
    
    # --- Penyesuaian Tanggal ---
    if 'tanggal' in data.columns:
        data['tanggal'] = pd.to_datetime(data['tanggal'], errors='coerce')
    
    # --- Penyesuaian Confidence (Sistem Anti-Error) ---
    if 'confidence' in data.columns:
        # Konversi koma ke titik dan pastikan numerik
        data['confidence'] = data['confidence'].astype(str).str.replace(',', '.')
        data['confidence'] = pd.to_numeric(data['confidence'], errors='coerce').fillna(0)
        
        # Normalisasi angka jika terbaca sebagai ribuan (misal 8021 -> 0.8021)
        data['confidence'] = data['confidence'].apply(
            lambda x: x / 10000 if x > 100 else (x / 100 if x > 1 else x)
        )
    
    # --- Penyesuaian Link Foto ---
    if 'link foto' in data.columns:
        base_url = NGROK_URL.strip().rstrip('/')
        data['pratinjau'] = data['link foto'].apply(
            lambda x: f"{base_url}/static/images/{str(x).strip()}" 
            if str(x).strip().lower() not in ['nan', 'none', ''] else None
        )
        
    return data

# 5. Dashboard Utama
try:
    df = load_data()

    st.title("🚧 Dashboard Monitoring Jalan Rusak")
    
    # Metrik
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Laporan", f"{len(df)} 📋")
    with col2:
        # Menghitung deteksi kelas Unseen secara dinamis
        unseen_list = ["Jalanan Berlumpur", "Bukan Jalanan"]
        u_count = len(df[df['jenis kerusakan'].isin(unseen_list)]) if 'jenis kerusakan' in df.columns else 0
        st.metric("Deteksi Unseen ✨", u_count)
    with col3:
        avg_conf = df['confidence'].mean() if 'confidence' in df.columns else 0
        st.metric("Rerata Akurasi", f"{avg_conf:.2%}")

    st.markdown("---")

    # Tabel Riwayat
    st.subheader("📋 Riwayat Deteksi Model Final")
    
    st.data_editor(
        df,
        column_config={
            "pratinjau": st.column_config.ImageColumn("Foto Kejadian", width="medium"),
            "confidence": st.column_config.NumberColumn("Confidence", format="%.2f%%"),
            "tanggal": st.column_config.DatetimeColumn("Waktu Laporan"),
            "link foto": None # Sembunyikan kolom teks asli
        },
        use_container_width=True,
        hide_index=True,
        disabled=True
    )

except Exception as e:
    st.error(f"Gagal memuat dashboard. Periksa koneksi Server atau Google Sheets. Error: {e}")
