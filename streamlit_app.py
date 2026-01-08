import streamlit as st
import pandas as pd
import numpy as np

# 1. Konfigurasi Utama & Ngrok
# Pastikan URL ini TIDAK diakhiri dengan garis miring (/)
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
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
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
    
    # Tips jika gambar tidak muncul
    st.warning("⚠️ Jika gambar tidak muncul, buka URL Server Model di tab baru dan klik 'Visit Site'.")
    
    if st.button("🔄 Segarkan Data"):
        st.cache_data.clear()
        st.rerun()

# 4. Fungsi Load Data
@st.cache_data(ttl=60)
def load_data():
    sheet_url = "https://docs.google.com/spreadsheets/d/115rzE-b9GzzM4onP2mbWN6rDohkHqPJo1Ptn1bkm-Z0/export?format=csv"
    data = pd.read_csv(sheet_url)
    
    # Standarisasi nama kolom
    data.columns = [c.lower().strip() for c in data.columns]
    
    # --- PERBAIKAN CONFIDENCE ---
    if 'confidence' in data.columns:
        data['confidence'] = data['confidence'].astype(str).str.replace(',', '.')
        data['confidence'] = data['confidence'].str.replace(r'[^-0-9.]', '', regex=True)
        data['confidence'] = pd.to_numeric(data['confidence'], errors='coerce').fillna(0)
        
        def fix_value(x):
            if x > 1000: return x / 10000
            if x > 100: return x / 1000
            if x > 1: return x / 100
            return x
        data['confidence'] = data['confidence'].apply(fix_value)
    
    # --- PERBAIKAN URL FOTO (SISTEM STABIL) ---
    if 'link foto' in data.columns:
        base_url = NGROK_URL.strip().rstrip('/')
        
        def build_url(filename):
            name = str(filename).strip()
            if name.lower() in ['nan', 'none', ''] or name.startswith('='):
                return None
            return f"{base_url}/static/images/{name}"
            
        data['pratinjau'] = data['link foto'].apply(build_url)
        
    return data

try:
    df = load_data()

    # --- Row 1: Metrik Utama ---
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Laporan", f"{len(df)} 📋")
    with col2:
        if 'jenis kerusakan' in df.columns:
            unseen_count = len(df[df['jenis kerusakan'].isin(['Jalanan Berlumpur', 'Bukan Jalanan'])])
            st.metric("Deteksi Unseen", f"{unseen_count} ✨")
    with col3:
        top_issue = df['jenis kerusakan'].mode()[0] if not df.empty and 'jenis kerusakan' in df.columns else "N/A"
        st.metric("Isu Terdominan", top_issue)
    with col4:
        if 'confidence' in df.columns:
            st.metric("Rerata Confidence", f"{df['confidence'].mean():.2%}")

    st.markdown("---")

    # --- Row 2: Tabel Interaktif (Menggunakan Data Editor untuk Gambar lebih Stabil) ---
    st.subheader("📋 Daftar Riwayat Laporan Lengkap")
    search_query = st.text_input("🔍 Cari berdasarkan lokasi atau jenis kerusakan:", "")
    
    filtered_df = df
    if search_query:
        filtered_df = df[df.astype(str).apply(lambda x: x.str.contains(search_query, case=False)).any(axis=1)]

    # Menggunakan st.data_editor karena seringkali lebih baik dalam merender ImageColumn
    st.data_editor(
        filtered_df,
        column_config={
            "pratinjau": st.column_config.ImageColumn(
                "Foto Kejadian", 
                help="Pratinjau foto dari lokasi",
                width="medium"
            ),
            "confidence": st.column_config.NumberColumn("Confidence", format="%.2f%%"),
            "tanggal": st.column_config.DatetimeColumn("Waktu"),
            "link foto": None # Sembunyikan nama file mentah
        },
        use_container_width=True,
        hide_index=True,
        disabled=True # Agar user tidak bisa mengedit data
    )

    # --- Row 3: Grafik ---
    if not filtered_df.empty and 'jenis kerusakan' in filtered_df.columns:
        st.subheader("📊 Statistik Jenis Kerusakan")
        st.bar_chart(filtered_df['jenis kerusakan'].value_counts())

except Exception as e:
    st.error(f"Gagal memuat dashboard. Error: {e}")
