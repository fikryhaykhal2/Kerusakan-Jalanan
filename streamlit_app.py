import streamlit as st
import pandas as pd

# Judul Dashboard
st.set_page_config(page_title="Monitoring Jalan Rusak", layout="wide")
st.title("🚧 Dashboard Pelaporan Jalan Rusak")
st.write("Data real-time dari laporan masyarakat melalui Telegram Bot.")

# Link Google Sheets Anda (Pastikan sudah di-share: Anyone with the link can view)
# Ganti part '/edit#gid=0' menjadi '/export?format=csv'
sheet_url = "https://docs.google.com/spreadsheets/d/115rzE-b9GzzM4onP2mbWN6rDohkHqPJo1Ptn1bkm-Z0/export?format=csv"

try:
    # Membaca Data
    df = pd.read_csv(sheet_url)
    
    # Menampilkan Statistik Sederhana
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Laporan", len(df))
    with col2:
        # Menghitung laporan hari ini jika ada kolom Timestamp
        st.metric("Laporan Baru", len(df)) 

    st.divider()

    # Menampilkan Tabel Data
    st.subheader("📋 Daftar Laporan Kerusakan")
    st.dataframe(df, use_container_width=True)

    # Fitur Peta (Jika ada kolom Lat & Lon)
    if 'latitude' in df.columns and 'longitude' in df.columns:
        st.subheader("📍 Peta Lokasi Kerusakan")
        st.map(df)

except Exception as e:
    st.error(f"Gagal memuat data: {e}")

    st.info("Pastikan Google Sheets Anda sudah diatur ke 'Anyone with the link can view'")
