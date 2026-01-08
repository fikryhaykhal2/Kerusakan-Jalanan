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
    
    # --- PERBAIKAN CONFIDENCE (SISTEM ANTI-NONE) ---
    if 'confidence' in data.columns:
        # a. Ubah ke string dan ganti koma ke titik (antisipasi standar Indo)
        data['confidence'] = data['confidence'].astype(str).str.replace(',', '.')
        
        # b. Bersihkan karakter selain angka dan titik (seperti simbol %)
        data['confidence'] = data['confidence'].str.replace(r'[^-0-9.]', '', regex=True)
        
        # c. Paksa jadi angka, jika gagal ganti jadi 0 (agar tidak None)
        data['confidence'] = pd.to_numeric(data['confidence'], errors='coerce').fillna(0)
        
        # d. Logika normalisasi angka besar
        def fix_value(x):
            if x > 1000: return x / 10000 # Contoh: 8021 -> 0.8021
            if x > 100: return x / 1000   # Contoh: 802 -> 0.802
            if x > 1: return x / 100      # Contoh: 80 -> 0.80
            return x
        
        data['confidence'] = data['confidence'].apply(fix_value)
    
    # Pembuatan URL Foto
    if 'link foto' in data.columns:
        data['pratinjau'] = data['link foto'].astype(str).apply(
            lambda x: f"{NGROK_URL}/static/images/{x}" if x not in ['nan', 'None', ''] and not x.startswith('=') else None
        )
    return data

try:
    df = load_data()

    # --- Header Section ---
    st.title("🚧 Dashboard Pelaporan Jalan Rusak")
    st.write(f"Analisis Citra Jalan Terintegrasi (Device: CLIP-ViT-B/32)")
    
    # --- Row 1: Metrik Utama ---
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Laporan", f"{len(df)} 📋")
    
    with col2:
        if 'jenis kerusakan' in df.columns:
            unseen_count = len(df[df['jenis kerusakan'].isin(['Jalanan Berlumpur', 'Bukan Jalanan'])])
            st.metric("Deteksi Unseen", f"{unseen_count} ✨")
        else:
            st.metric("Deteksi Unseen", "0")

    with col3:
        top_issue = df['jenis kerusakan'].mode()[0] if not df.empty and 'jenis kerusakan' in df.columns else "N/A"
        st.metric("Isu Terdominan", top_issue)

    with col4:
        if 'confidence' in df.columns:
            conf_avg = df['confidence'].mean()
            st.metric("Rerata Confidence", f"{conf_avg:.2%}") 
        else:
            st.metric("Status Server", "Aktif ✅")

    st.markdown("---")

    # --- Row 2: Tabel Interaktif dengan Gambar ---
    st.subheader("📋 Daftar Riwayat Laporan Lengkap")
    
    search_query = st.text_input("🔍 Cari berdasarkan lokasi atau jenis kerusakan:", "")
    
    if search_query:
        filtered_df = df[df.astype(str).apply(lambda x: x.str.contains(search_query, case=False)).any(axis=1)]
    else:
        filtered_df = df

    # Menampilkan Tabel
    st.dataframe(
        filtered_df,
        column_config={
            "pratinjau": st.column_config.ImageColumn("Foto Kejadian"),
            "confidence": st.column_config.NumberColumn(
                "Confidence", 
                format="%.2f%%", 
                help="Tingkat keyakinan model"
            ),
            "tanggal": st.column_config.DatetimeColumn("Waktu"),
            "link foto": None 
        },
        use_container_width=True,
        hide_index=True
    )

    # --- Row 3: Grafik ---
    if not filtered_df.empty and 'jenis kerusakan' in filtered_df.columns:
        st.subheader("📊 Statistik Jenis Kerusakan")
        chart_data = filtered_df['jenis kerusakan'].value_counts()
        st.bar_chart(chart_data)

except Exception as e:
    st.error(f"Gagal memuat dashboard. Error: {e}")
