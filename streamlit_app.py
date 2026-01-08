import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Konfigurasi Halaman & Tema
st.set_page_config(
    page_title="Pusat Monitoring Jalan Rusak",
    page_icon="🚧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS untuk tampilan lebih bersih
st.markdown("""
    <style>
    .main {
        background-color: #f5f7f9;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Sidebar untuk Filter & Navigasi
with st.sidebar:
    st.image("https://www.gstatic.com/images/branding/product/2x/maps_96in128dp.png", width=80)
    st.title("Navigasi")
    st.info("Gunakan menu ini untuk memfilter data laporan.")
    
    # Tombol Refresh Data
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()

# 3. Fungsi Load Data
@st.cache_data
def load_data():
    sheet_url = "https://docs.google.com/spreadsheets/d/115rzE-b9GzzM4onP2mbWN6rDohkHqPJo1Ptn1bkm-Z0/export?format=csv"
    data = pd.read_csv(sheet_url)
    # Pastikan nama kolom kecil semua untuk kemudahan akses
    data.columns = [c.lower() for c in data.columns]
    return data

try:
    df = load_data()

    # 4. Header Section
    st.title("🚧 Dashboard Monitoring Kerusakan Jalan")
    st.caption("Sistem Informasi Geografis Pelaporan Real-time via Telegram Bot")
    
    # 5. KPI Metrics (Bagian Atas)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Laporan", len(df), delta_color="normal")
    with col2:
        # Contoh filter kategori (jika ada kolom 'status' atau 'jenis_kerusakan')
        total_pothole = len(df[df['jenis_kerusakan'] == 'Jalan Berlubang']) if 'jenis_kerusakan' in df.columns else 0
        st.metric("Jalan Berlubang", total_pothole)
    with col3:
        st.metric("Wilayah Terdampak", df['latitude'].nunique() if 'latitude' in df.columns else 0)
    with col4:
        st.metric("Status Selesai", "0%", delta="-100%")

    st.markdown("---")

    # 6. Visualisasi Utama (Peta & Grafik)
    main_col1, main_col2 = st.columns([2, 1])

    with main_col1:
        st.subheader("📍 Sebaran Lokasi Laporan")
        if 'latitude' in df.columns and 'longitude' in df.columns:
            st.map(df)
        else:
            st.warning("Data koordinat (Lat/Lon) tidak ditemukan.")

    with main_col2:
        st.subheader("📊 Statistik Kerusakan")
        if 'jenis_kerusakan' in df.columns:
            fig = px.pie(df, names='jenis_kerusakan', hole=0.4, 
                         color_discrete_sequence=px.colors.qualitative.Pastel)
            fig.update_layout(margin=dict(t=0, b=0, l=0, r=0))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Tambahkan kolom 'jenis_kerusakan' untuk melihat grafik.")

    # 7. Detail Data Laporan (Tabel)
    with st.expander("🔍 Lihat Detail Seluruh Data Laporan", expanded=False):
        # Filter Pencarian
        search = st.text_input("Cari data laporan (ID, Lokasi, atau Keterangan):")
        if search:
            df_display = df[df.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)]
        else:
            df_display = df
            
        st.dataframe(
            df_display, 
            use_container_width=True,
            column_config={
                "foto": st.column_config.ImageColumn("Preview Foto"),
                "latitude": None, # Sembunyikan kolom koordinat agar tabel bersih
                "longitude": None
            }
        )

except Exception as e:
    st.error(f"❌ Terjadi kesalahan sistem: {e}")
    st.markdown("---")
    st.subheader("Panduan Perbaikan:")
    st.write("1. Pastikan Google Sheets memiliki kolom: `latitude`, `longitude`, dan `jenis_kerusakan`.")
    st.write("2. Periksa apakah link CSV sudah benar.")
