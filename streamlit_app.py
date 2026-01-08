import streamlit as st
import pandas as pd

# 1. Konfigurasi Utama & Ngrok
# GANTI URL INI setiap kali Anda menjalankan ulang Ngrok
NGROK_URL = "https://your-ngrok-url.ngrok-free.app" 

st.set_page_config(
    page_title="Monitoring Jalan Rusak v2",
    page_icon="🚧",
    layout="wide"
)

# 2. Custom CSS (Tetap menggunakan gaya gelap Anda)
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
    
    # Pastikan kolom 'link foto' adalah string agar bisa ditambah dengan URL
    if 'link foto' in data.columns:
        # .astype(str) mencegah error 'int' + 'str'
        data['pratinjau'] = data['link foto'].astype(str).apply(
            lambda x: f"{NGROK_URL}/static/images/{x}" if x != 'nan' and not x.startswith('=') else None
        )
    return data data

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
        # Menghitung deteksi Open-Vocabulary (Unseen)
        unseen_count = len(df[df['jenis kerusakan'].isin(['Jalanan Berlumpur', 'Bukan Jalanan'])])
        st.metric("Deteksi Unseen", f"{unseen_count} ✨", help="Jumlah kelas di luar dataset latih")
    with col3:
        top_issue = df['jenis kerusakan'].mode()[0] if not df.empty else "N/A"
        st.metric("Isu Terdominan", top_issue)
    with col4:
        avg_conf = f"{df['confidence'].mean():.2%}" if 'confidence' in df.columns else "0%"
        st.metric("Rerata Confidence", avg_conf)

    st.markdown("---")

    # --- Row 2: Tabel Interaktif dengan Gambar ---
    st.subheader("📋 Daftar Riwayat Laporan Lengkap")
    
    search_query = st.text_input("🔍 Cari berdasarkan lokasi, deskripsi, atau jenis kerusakan:", "")
    
    if search_query:
        filtered_df = df[df.astype(str).apply(lambda x: x.str.contains(search_query, case=False)).any(axis=1)]
    else:
        filtered_df = df

    # Menampilkan Tabel dengan Kolom Gambar
    st.dataframe(
        filtered_df,
        column_config={
            "pratinjau": st.column_config.ImageColumn("Foto Kejadian", help="Gambar dari folder lokal server"),
            "confidence": st.column_config.NumberColumn("Confidence", format="%.4f"),
            "tanggal": st.column_config.DatetimeColumn("Waktu"),
            "link foto": None # Sembunyikan kolom nama file mentah agar rapi
        },
        use_container_width=True,
        hide_index=True
    )

    # --- Row 3: Grafik ---
    st.subheader("📊 Statistik Jenis Kerusakan")
    if not filtered_df.empty:
        chart_data = filtered_df['jenis kerusakan'].value_counts()
        st.bar_chart(chart_data)

except Exception as e:
    st.error(f"Gagal memuat dashboard. Pastikan kolom di Google Sheets sudah sesuai. Error: {e}")

