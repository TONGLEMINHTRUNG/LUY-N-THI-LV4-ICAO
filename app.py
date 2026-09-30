import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Luyện thi ICAO Level 4", page_icon="✈", layout="centered")
st.title("🎧 Phần mềm Luyện nghe Tiếng Anh Hàng không")
st.caption("Dạng bài tập: Nghe và trả lời tự luận")

# 1. Hàm lấy dữ liệu trực tiếp từ Google Sheets, cập nhật mỗi 60 giây
@st.cache_data(ttl=60)
def load_database():
    sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQo3-ExtlDVOnEaTOC2rJMMzbHbazP2CxWGCNG7nyjKwaj8I9EyAfapCg6EUQxi5POgufMmkSxpRXf-/pub?output=csv"
    df = pd.read_csv(sheet_url)
    # Tự động loại bỏ các dòng trống nếu có để tránh lỗi hiển thị
    return df.dropna(subset=['Track_Name'])

df = load_database()

# 2. Hàm tải ngầm file âm thanh từ Drive về để chống lỗi chặn Web
@st.cache_data(show_spinner=False)
def load_audio(drive_id):
    url = f"https://drive.google.com/uc?export=download&id={drive_id}"
    response = requests.get(url)
    return response.content

# 3. Khu vực thanh điều hướng (Sidebar)
st.sidebar.header("📚 Danh sách bài")
unique_tracks = df['Track_Name'].unique().tolist()
selected_track = st.sidebar.selectbox("Chọn Track để nghe:", unique_tracks)

track_data = df[df['Track_Name'] == selected_track]

st.markdown("---")
st.subheader(f"Đang phát: {selected_track}")

# 4. Phát Audio
drive_id = track_data.iloc[0]['Drive_ID']
if pd.isna(drive_id) or str(drive_id).strip() == "":
    st.error("⚠️ Bài này chưa có ID Audio.")
else:
    # Chèn dữ liệu đã tải ngầm vào trình phát
    audio_bytes = load_audio(drive_id)
    st.audio(audio_bytes, format="audio/mp3")

st.markdown("### 📝 Câu hỏi bài tập")

# 5. Hiển thị danh sách câu hỏi
for index, row in track_data.iterrows():
    with st.container():
        st.write(f"**{row['Question']}**")
        st.text_area(f"Nhập câu trả lời (nháp):", height=80, key=f"nhap_{index}")
        
        with st.expander(f"👁️ Xem đáp án câu này"):
            st.info(f"**Đáp án:** {row['Answer']}")
        st.markdown("<br>", unsafe_allow_html=True)
