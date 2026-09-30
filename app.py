import streamlit as st
import pandas as pd
import requests
import json
from concurrent.futures import ThreadPoolExecutor

# --- 1. CẤU HÌNH GIAO DIỆN VÀ CSS THU GỌN ---
st.set_page_config(page_title="Luyện thi ICAO Level 4", page_icon="✈️", layout="wide")

st.markdown("""
    <style>
    /* TÙY CHỈNH KHU VỰC LÀM BÀI CHÍNH (MAIN) */
    section[data-testid="stMain"] div[role="radiogroup"] label p {
        font-size: 17px !important;
        font-weight: 500;
    }
    section[data-testid="stMain"] .stMarkdown, section[data-testid="stMain"] .stRadio {
        margin-bottom: -10px !important;
    }
    section[data-testid="stMain"] div[data-testid="stMarkdownContainer"] {
        margin-bottom: 5px !important;
    }

    /* TÙY CHỈNH KHU VỰC MENU TRÁI (SIDEBAR) ĐỂ SIÊU GỌN GÀNG */
    section[data-testid="stSidebar"] div[role="radiogroup"] label p {
        font-size: 14px !important;
    }
    section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] div[data-baseweb="select"] {
        font-size: 14px !important;
    }
    section[data-testid="stSidebar"] h1 {
        font-size: 20px !important;
        padding-bottom: 0px !important;
    }
    section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3 {
        font-size: 16px !important;
        padding-bottom: 0px !important;
        margin-bottom: -10px !important;
    }

    /* THU GỌN ĐƯỜNG KẺ CHUNG */
    hr {
        margin-top: 10px !important;
        margin-bottom: 10px !important;
    }
    </style>
""", unsafe_allow_html=True)

# Lấy đường link API từ Secrets (Nếu chưa set trong Secrets thì dùng link cứng dự phòng)
API_URL = st.secrets.get("API_URL", "https://script.google.com/macros/s/AKfycbxeWNQeOcccY3QVjqGiyIROaOOvzCBmpLbIstLgW9IaDR6pzFxXh6j6S99bvno0Yl-T/exec")

if 'executor' not in st.session_state:
    st.session_state.executor = ThreadPoolExecutor(max_workers=2)

# --- 2. QUẢN LÝ TRẠNG THÁI ---
def init_states():
    if 'user_name' not in st.session_state: st.session_state.user_name = ""
    if 'db_loaded' not in st.session_state: st.session_state.db_loaded = False
    if 'icao_answers' not in st.session_state: st.session_state.icao_answers = {}

init_states()

# --- 3. CÁC HÀM TỰ ĐỘNG ĐỒNG BỘ CLOUD (BẤT ĐỒNG BỘ) ---
def fetch_progress_from_db(user):
    if not API_URL: return None
    try:
        res = requests.get(f"{API_URL}?action=get_progress&user={user}&quiz=ICAO_Listening", timeout=5)
        if res.status_code == 200: return res.json()
    except: pass
    return None

def _async_post_request(url, payload):
    try:
        requests.post(url, json=payload, timeout=5)
    except: pass

def save_icao_progress():
    if not API_URL or st.session_state.user_name == "": return
    
    payload = {
        "action": "save_progress", "mode": "icao_listening",
        "user": st.session_state.user_name, "quiz": "ICAO_Listening",
        "mt_answers": json.dumps(st.session_state.icao_answers),
    }
    st.session_state.executor.submit(_async_post_request, API_URL, payload)

def on_answer_change(idx_str):
    selected_val = st.session_state[f"nhap_{idx_str}"]
    st.session_state.icao_answers[idx_str] = selected_val
    save_icao_progress()

# Hàm Callback chuyển đổi bài hát tránh lỗi xung đột Widget
def change_track(step, tracks_list):
    current_idx = tracks_list.index(st.session_state.selected_track_key)
    st.session_state.selected_track_key = tracks_list[current_idx + step]

# --- 4. TẢI DỮ LIỆU ĐỀ THI VÀ AUDIO ---
@st.cache_data(ttl=60)
def load_database():
    sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQo3-ExtlDVOnEaTOC2rJMMzbHbazP2CxWGCNG7nyjKwaj8I9EyAfapCg6EUQxi5POgufMmkSxpRXf-/pub?output=tsv"
    df = pd.read_csv(sheet_url, sep='\t')
    return df.dropna(subset=['Track_Name'])

df = load_database()

@st.cache_data(show_spinner=False)
def load_audio(drive_id):
    url = f"https://drive.google.com/uc?export=download&id={drive_id}"
    response = requests.get(url)
    return response.content

# --- 5. MÀN HÌNH KHAI BÁO TÊN BAN ĐẦU ---
if st.session_state.user_name == "":
    st.title("✈️ Phần mềm Luyện Nghe ICAO Level 4")
    st.subheader("Hệ thống tự động đồng bộ tiến độ học")
    
    with st.form("identity_form"):
        name_input = st.text_input("Nhập Tên định danh của bạn (VD: TrungATC):")
        submit_identity = st.form_submit_button("Bắt đầu ôn tập 🚀")
        if submit_identity:
            if name_input.strip() == "":
                st.warning("Vui lòng điền tên định danh cá nhân!")
            else:
                st.session_state.user_name = name_input.strip()
                st.session_state.db_loaded = False
                st.rerun()
    
    st.markdown("<br><hr><p style='text-align: center; color: gray; font-style: italic;'>💡 Tiến độ làm bài của bạn sẽ được lưu trữ đám mây, tự động khôi phục trên mọi thiết bị.</p>", unsafe_allow_html=True)
    st.stop()

# --- TẢI TIẾN ĐỘ TỪ CLOUD CHO NGƯỜI DÙNG HIỆN TẠI ---
if not df.empty and not st.session_state.db_loaded:
    with st.spinner("🔄 Đang đồng bộ tiến độ ôn tập từ Cloud..."):
        progress = fetch_progress_from_db(st.session_state.user_name)
        
        if progress and progress.get("status") == "found":
            mt_ans_str = progress.get("mt_answers", "{}")
            if mt_ans_str:
                st.session_state.icao_answers = json.loads(mt_ans_str)
        else:
            st.session_state.icao_answers = {}
            
        st.session_state.db_loaded = True
        st.rerun()

# --- 6. GIAO DIỆN MENU BÊN TRÁI ---
with st.sidebar:
    st.success(f"👤 Học viên: **{st.session_state.user_name}**")
    if st.button("🚪 Đổi tài khoản / Đăng xuất"):
        st.session_state.user_name = ""
        st.session_state.db_loaded = False
        st.rerun()
        
    st.divider()
    st.title("🎧 Chọn Bài Nghe")
    unique_tracks = df['Track_Name'].unique().tolist()
    
    if "selected_track_key" not in st.session_state:
        st.session_state.selected_track_key = unique_tracks[0]
    
    completed_count = len([x for x in st.session_state.icao_answers.values() if str(x).strip() != ""])
    st.info(f"📊 Tiến độ tổng: **{completed_count}/{len(df)}** câu")

    selected_track = st.selectbox(
        "📌 Danh sách Track:", 
        unique_tracks,
        key="selected_track_key"
    )
    
    if st.button("🗑️ Xóa tiến độ bài này"):
        track_indices = df[df['Track_Name'] == selected_track].index.tolist()
        for idx in track_indices:
            idx_str = str(idx)
            if idx_str in st.session_state.icao_answers:
                del st.session_state.icao_answers[idx_str]
        save_icao_progress()
        st.rerun()
        
    st.write("---")
    st.markdown("<p style='text-align: center; color: #888; font-style: italic; font-size: 14px;'>Hệ thống lưu tự động khi bạn gõ xong đáp án</p>", unsafe_allow_html=True)


# --- 7. KHU VỰC HIỂN THỊ CHÍNH ---
st.title("✈️ Luyện nghe Tiếng Anh Hàng không")

if df.empty:
    st.warning("⚠️ Cơ sở dữ liệu đang trống hoặc link tải file bị lỗi.")
else:
    track_data = df[df['Track_Name'] == selected_track]
    
    st.markdown("---")
    st.subheader(f"Đang phát: {selected_track}")
    
    drive_id = track_data.iloc[0]['Drive_ID']
    if pd.isna(drive_id) or str(drive_id).strip() == "":
        st.error("⚠️️ Bài này chưa có ID Audio.")
    else:
        with st.spinner('Đang tải Audio từ Cloud...'):
            audio_bytes = load_audio(drive_id)
            st.audio(audio_bytes, format="audio/mp3")

    st.markdown("### 📝 Câu hỏi bài tập")

    for index, row in track_data.iterrows():
        idx_str = str(index)
        
        with st.container():
            st.write(f"**{row['Question']}**")
            
            prev_val = st.session_state.icao_answers.get(idx_str, "")
            
            st.text_area(
                "Nhập câu trả lời (nháp):", 
                value=prev_val, 
                height=80, 
                key=f"nhap_{idx_str}",
                on_change=on_answer_change,
                args=(idx_str,)
            )
            
            with st.expander(f"👁️ Xem đáp án chuẩn"):
                st.info(f"**Đáp án:** {row['Answer']}")
            st.markdown("<br>", unsafe_allow_html=True)

    # --- KHU VỰC NÚT ĐIỀU HƯỚNG BÀI NGHE (DÙNG CALLBACK) ---
    st.write("---")
    col1, col2, col3 = st.columns([1, 4, 1])
    
    current_track_idx = unique_tracks.index(selected_track)
    
    if current_track_idx > 0:
        # Sử dụng on_click để chuyển bài mượt mà
        col1.button("⬅ Bài trước", on_click=change_track, args=(-1, unique_tracks))

    if current_track_idx < len(unique_tracks) - 1:
        col3.button("Bài tiếp theo ➡️", on_click=change_track, args=(1, unique_tracks))
