import streamlit as st
import pandas as pd

st.set_page_config(page_title="Luyện thi ICAO Level 4", page_icon="✈️️", layout="centered")
st.title("🎧 Phần mềm Luyện nghe Tiếng Anh Hàng không")
st.caption("Dạng bài tập: Nghe và trả lời tự luận")

# Hàm lấy dữ liệu trực tiếp từ Google Sheets, cập nhật mỗi 60 giây
@st.cache_data(ttl=60)
def load_database():
    # THAY ĐƯỜNG LINK DƯỚI ĐÂY BẰNG LINK BẠN ĐÃ COPY Ở GIAI ĐOẠN 1
    sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQo3-ExtlDVOnEaTOC2rJMMzbHbazP2CxWGCNG7nyjKwaj8I9EyAfapCg6EUQxi5POgufMmkSxpRXf-/pub?output=tsv"
    return pd.read_csv(sheet_url)

df = load_database()

st.sidebar.header("📚 Danh sách bài")
unique_tracks = df['Track_Name'].unique().tolist()
selected_track = st.sidebar.selectbox("Chọn Track để nghe:", unique_tracks)

track_data = df[df['Track_Name'] == selected_track]

st.markdown("---")
st.subheader(f"Đang phát: {selected_track}")

# Phát Audio từ Drive (lấy Drive ID từ dòng đầu tiên của Track)
drive_id = track_data.iloc[0]['Drive_ID']
direct_audio_url = f"https://drive.google.com/uc?export=download&id={drive_id}"
st.audio(direct_audio_url, format="audio/mp3")

st.markdown("### 📝 Câu hỏi bài tập")

for index, row in track_data.iterrows():
    with st.container():
        st.write(f"**{row['Question']}**")
        st.text_area(f"Nhập câu trả lời (nháp):", height=80, key=f"nhap_{index}")
        
        with st.expander(f"👁️ Xem đáp án câu này"):
            st.info(f"**Đáp án:** {row['Answer']}")
        st.markdown("<br>", unsafe_allow_html=True)