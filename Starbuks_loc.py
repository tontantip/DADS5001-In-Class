import streamlit as st
import pandas as pd
import numpy as np

st.title("☕ Starbucks Locations in Thailand")

DATA_URL = "https://raw.githubusercontent.com/tontantip/Archive/refs/heads/main/starbuks_data.csv"

@st.cache_data
def load_data(nrows=None):
    data = pd.read_csv(DATA_URL, nrows=nrows)
    data.columns = data.columns.str.lower()
    return data

# โหลดข้อมูล
data_load_state = st.text('Loading data...')
data = load_data()
data_load_state.text('Done! (using st.cache_data)')

# ตรวจสอบคอลัมน์ที่เกี่ยวข้อง
st.subheader('Raw data')
st.write(data)
st.subheader('Number of pickups by hour')
city_counts = data['city'].value_counts().head(20) # เลือกแสดง 20 เมืองแรกที่มากที่สุด

st.subheader('Top 20 Starbucks Locations by City')

st.bar_chart(city_counts)

# กรองเฉพาะประเทศไทย
thailand_data = data[data['country'] == 'TH'].copy()

if thailand_data.empty:
    st.error("⚠️ ไม่พบข้อมูลสาขาในประเทศไทย (country = 'TH')")
else:
    st.success(f"✅ พบ {len(thailand_data)} สาขาในประเทศไทย")

    # ตรวจสอบว่ามี latitude และ longitude หรือไม่
    if 'latitude' in thailand_data.columns and 'longitude' in thailand_data.columns:
        map_data = thailand_data[['latitude', 'longitude']].dropna()
        
        st.subheader(f'📍 แผนที่สาขา Starbucks ทั้งหมดในประเทศไทย ({len(map_data)} จุด)')
        st.map(map_data, zoom=5)  # zoom=5 เพื่อโฟกัสประเทศไทย

        # แสดงตารางข้อมูล
        if st.checkbox('แสดงข้อมูลดิบของสาขาในประเทศไทย'):
            st.subheader('ข้อมูลสาขาในประเทศไทย')
            display_cols = ['brand', 'store name', 'city', 'state/province', 'latitude', 'longitude']
            available_cols = [col for col in display_cols if col in thailand_data.columns]
            st.dataframe(thailand_data[available_cols].reset_index(drop=True))

        # สรุปจำนวนสาขาต่อจังหวัด
        if 'state/province' in thailand_data.columns:
            province_counts = thailand_data['state/province'].value_counts().head(10)
            st.subheader('🏆 Top 10 จังหวัดที่มีสาขามากที่สุด')
            st.bar_chart(province_counts)

    else:
        st.warning("ไม่พบคอลัมน์ latitude/longitude สำหรับแสดงแผนที่")
        st.write("คอลัมน์ที่มี:", list(thailand_data.columns))



