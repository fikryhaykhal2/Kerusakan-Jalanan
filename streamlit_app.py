import streamlit as st
import pandas as pd

# 1. Konfigurasi Halaman
st.set_page_config(
    page_title="Monitoring Jalan Rusak",
    page_icon="🚧",
    layout="wide"
)

# 2. Custom CSS untuk Tema Gelap & Box Metrik
st.markdown("""
    <style>
    /* Mengubah latar belakang utama */
    .main {
        background-color: #0e1117;
    }
    /* Mengubah Box Metrik menjadi Gelap */
    div[data-testid="stMetric"] {
        background-color: #1f2937; 
        border: 1px solid #374151;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    /* Warna teks Label Metrik */
    div[data-testid="stMetricLabel"] {
        color: #9ca3af !important;
        font-weight: bold;
    }
    /* Warna teks Nilai Metrik */
    div[data-testid="stMetricValue"] {
        color: #ffffff !important;
    }
    /* Menghilangkan border pada dataframe agar lebih bersih */
    .stDataFrame {
        border: none;
    }
    h1, h2, h3 {
        color: #ffffff;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Sidebar
with st.sidebar:
    st.title("⚙️ Kontrol Panel")
    st.info("Sistem Monitoring Terpadu")
    if st.button("🔄 Segarkan Data"):
        st.cache_data.clear()
        st.rerun()

# 4. Fungsi Load Data dari Google Sheets
@st.cache_data
def load_data():
    sheet_url = "https://docs.google.com/spreadsheets/d/115rzE-b9GzzM4onP2mbWN6rDohkHqPJo1Ptn1bkm-Z0/export?format=csv"
    data = pd.read_csv(sheet_url)
    data.columns = [c.lower() for c in data.columns]
    return data

try:
    df = load_data()

    # --- Header Section ---
    st.title("🚧 Dashboard Pelaporan Jalan Rusak")
    st.write("Data laporan masyarakat yang masuk melalui sistem Telegram Bot.")
    
    # --- Row 1: Metrik Utama (Box Gelap) ---
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Laporan", f"{len(df)} 📋")
    with col2:
        # Contoh filter sederhana untuk laporan hari ini (jika ada data terkait)
        st.metric("Laporan Baru", "5 🆕", delta="+2 hari ini")
    with col3:
        # Menampilkan jenis kerusakan yang paling sering dilaporkan
        top_issue = df['jenis_kerusakan'].mode()[0] if 'jenis_kerusakan' in df.columns else "N/A"
        st.metric("Isu Terdominan", top_issue)
    with col4:
        st.metric("Status Server", "Aktif ✅")

    st.markdown("---")

    # --- Row 2: Tabel Detail Laporan ---
    st.subheader("📋 Daftar Riwayat Laporan Lengkap")
    
    # Menambahkan fitur pencarian/filter di atas tabel
    search_query = st.text_input("🔍 Cari berdasarkan lokasi atau jenis kerusakan:", "")
    
    if search_query:
        # Filter dataframe berdasarkan input pencarian
        filtered_df = df[df.astype(str).apply(lambda x: x.str.contains(search_query, case=False)).any(axis=1)]
    else:
        filtered_df = df

    # Menampilkan tabel dengan lebar penuh
    st.dataframe(
        filtered_df, 
        use_container_width=True,
        hide_index=True # Menyembunyikan kolom index agar lebih rapi
    )

    # Informasi tambahan di footer
    st.caption(f"Menampilkan {len(filtered_df)} dari total {len(df)} laporan.")

except Exception as e:
    st.error(f"Gagal memuat dashboard: {e}")
