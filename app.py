import streamlit as st
import pandas as pd
import requests
import json
import re

# --- 1. CẤU HÌNH GIAO DIỆN VÀ CSS THU GỌN ---
st.set_page_config(page_title="Luyện thi ICAO Level 4", page_icon="✈️", layout="wide")

st.markdown("""
    <style>
    section[data-testid="stMain"] div[data-testid="stMarkdownContainer"] { margin-bottom: 5px !important; }
    section[data-testid="stSidebar"] div[role="radiogroup"] label p { font-size: 14px !important; }
    section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] div[data-baseweb="select"] { font-size: 14px !important; }
    section[data-testid="stSidebar"] h1 { font-size: 20px !important; padding-bottom: 0px !important; }
    section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3 { font-size: 16px !important; padding-bottom: 0px !important; margin-bottom: -10px !important; }
    hr { margin-top: 10px !important; margin-bottom: 10px !important; }
    </style>
""", unsafe_allow_html=True)

# Lấy đường link API (Google Apps Script)
API_URL = st.secrets.get("API_URL", "https://script.google.com/macros/s/AKfycbxeWNQeOcccY3QVjqGiyIROaOOvzCBmpLbIstLgW9IaDR6pzFxXh6j6S99bvno0Yl-T/exec")

# --- DỮ LIỆU TRANSCRIPT (TỪ PDF) ---
TRANSCRIPT_TEXT = """
Track 01
PILOT: Ground, SF398, request departure information.
ATC: SF398, runway in use 29, wind 350 degrees 23knots, gusting 30, temperature 12, dew point 10, runway is wet, braking action good, QNH 1023.
PILOT: 350 degrees 23 knots, QNH 1023, runway 29, SF398.

Track 02
ATC: SF196, here is your clearance.
PILOT: Ready to copy, SF196.
ATC: Rexbury ATC clears SF196 to Winton via flight planned route, November 2 departure, left turn out after departure, climb to and maintain FL 250, request level change en- route, contact 120.26 when airborne, and squawk 2514.
PILOT: SF196, cleared to Winton, flight planned route, N2 departure, turn left after departure FL250, request level change en-route, 120.26 when airborne, and squawk 2514.
ATC: That is correct SF196.

Track 03
PILOT: SF153, stand Bravo 5, request start-up for Athens.
ATC: SF153, start-up at 35.
PILOT: Roger, start-up at 35, SF153.

Track 04
PILOT: Rexbury Ground, Sunair 670, good morning, request start-up.
ATC: Sunair 670, expect departure 50, I'll call you back for start.
PILOT: Could we start-up quickly please. We've got livestock in the hold.
ATC: Standby one.
ATC: Sunair 670, start-up approved.
PILOT: Starting up.

Track 05
PILOT: Rexbury Ground, Sunair 539, good morning, ready to start.
ATC: Good morning Sunair 539, there's a 55-minute delay this morning due to a computer failure, your slot time is 09.45.
PILOT: 09.45, roger, Sunair 539.

Track 06
PILOT: Rexbury Ground, Sunair 692, good morning, request start-up.
ATC: Good morning Sunair 692, slot time 35, start-up 10 minutes before.
PILOT: Slot time 35, start-up 10 minutes before, Sunair 692.
PILOT: (at 25) Sunair 692, we wish to delay our start-up due to passenger baggage identification process. We have one passenger missing.
ATC: Roger, Sunair 692.

Track 07
PILOT: FBG, request push-back, stand C8.
ATC: FBG, expect 2 minutes delay, due 747 taxiing behind.
PILOT: Holding position, FBG.

Track 08
PILOT: Sunair 559, request push-back.
ATC: Sunair 559, there's a 747 to pass behind and park behind, after him, push-back approved.
PILOT: After the 747, pushing back.

Track 09
PILOT: Sunair 310, we're having problems with the tow - bar. We're waiting for another one.
ATC: Roger, Sunair 310, call me back when ready.

Track 10
PILOT: Sunair 892, we're going to be delayed for a while. The tug seems to have broken down.
ATC: Roger Sunair 892, call me back for taxi when you've got it sorted out.

Track 11
PILOT: SF133, request taxi.
ATC: SF133, taxi via taxiway C to holding point 29L.
PILOT: Taxiway C to holding point 29L, SF133.
ATC: SF133, give way to the 747 passing left to right.
PILOT: Traffic in sight, SF133.

Track 12
PILOT: Sunair 978, request taxi.
ATC: Sunair 978, taxiway D4, cross runway 32, backtrack to threshold runway 11, call me back reaching 32.
PILOT: Taxiway D4, backtrack 11, call you back reaching 32, Sunair 978.
PILOT: Sunair 978, reaching intersection with runway 32.
ATC: Sunair 978, cross runway 32.
PILOT: Crossing runway 32.

Track 13
PILOT: Sunair 978, a large dog has just crossed the taxiway ahead of us.
ATC: Sunair 978, which direction was it going?
PILOT: It crossed from right to left.
ATC: Thank you Sunair 978, we'll try to get someone to catch it.

Track 14
ATC: Sunair 497, you've gone too far. You missed taxiway D4. Wait there for the 'follow me' car.
PILOT: Sunair 497, wilco.

Track 15
PILOT: Sunair 329, holding point 32.
ATC: Sunair 329, line up and wait. (pause)
PILOT: Sunair 329, we have a problem, the nose wheel steering seems to be jammed.
ATC: Do you require a tug?
PILOT: Affirm. Request tug to tow us back to the apron.

Track 16
PILOT: Sunair 473, holding point 18 Left.
ATC: Suggest you hold there for a few minutes, the thunderstorm is rapidly approaching the far end of the runway.
PILOT: Wilco, Sunair 473.

Track 17
PILOT: Sunair 968, reaching holding point 29, request return to stand, the brakes are overheating.
ATC: Roger, Sunair 968, turn in the holding bay, take the first convenient left turn, onto taxiway Juliet.
PILOT: Left turn onto taxiway Juliet.

Track 18
ATC: Sunair 332, runway 25, cleared for take-off, wind 340 degrees 16 knots.
PILOT: Taking off, Sunair 332.
PILOT: Sunair 332 stopping. Take-off abandoned, due to engine failure.
ATC: Do you request taxi to the parking area Sunair 332?
PILOT: Affirm, request return to parking area.

Track 19
PILOT: Sunair 596, runway 25, ready for departure.
ATC: Sunair 596, runway 25, cleared for take-off, wind calm.
PILOT: Sunair 596, taking off. (pause)
ATC: Sunair 596, stop immediately, I say again, stop immediately, flames coming from left main gear.
PILOT: Sunair 596, stopping.
PILOT: Sunair 596, activating escape slides, request emergency services.

Track 20
PILOT: Sunair 879, take-off aborted due to tyre blow-out. We slid slightly off the runway.
ATC: Sunair 879, are you able to taxi off the runway?
PILOT: Negative, the right gear is bogged down. Request passenger steps and buses to take the passengers to the terminal.
ATC: Roger, Sunair 879, we'll get a tug to come out to you as well.

Track 21
PILOT: Sunair 670, Rexbury Approach, we've shut down no.1 engine after a bird strike. We're coming back.
ATC: Do you require landing priority, Sunair 670?
PILOT: Negative. There is no fire warning, Sunair 670.
ATC: Roger, Sunair 670, turn left heading 250.

Track 22
PILOT: Sunair 539, we're returning. We seem to have a wheel well fire, the warning light has just flashed on. Request priority landing and emergency services.
ATC: Roger, Sunair 539, I'll call you back.
ATC: Sunair 539, you're number one to land, call Tower on 118.5.
PILOT: 118.5, Sunair 539.

Track 23
PILOT: Sunair 281, we have engine failure. We intend to return to Rexbury, but we have to dump 40 tons of fuel first.
ATC: Roger, Sunair 281, proceed to fuel dumping area, at 5000 feet, right pattern over Forest. Report when reaching.
PILOT: Sunair 281, 5000 feet over Forest. (pause)
PILOT: Sunair 281, reaching Forest, ready to dump fuel.
ATC: Roger, go ahead Sunair 281, break. All aircraft, Rexbury Control, fuel dumping in progress, DC8, on radial 240 Forest VOR, ranging 14 to 20 nm, avoid flight below 5000 feet within 10 nautical miles of fuel dumping track.
PILOT: Sunair 281, fuel dumping completed, request approach to Rexbury.

Track 24
PILOT: Sunair928, we've just come through some severe turbulence. What kind of traffic is there ahead of us?
ATC: It must've been wake turbulence, there's a 747 ahead, although normal separation was provided.

Track 25
ATC: Sunair 596, what is your rate of climb?
PILOT: 700 feet per minute.
ATC: Due to traffic, can you adjust your rate of climb to be above flight level 180 at the FIR boundary?
PILOT: Above flight level 180 at the FIR boundary, wilco, Sunair 596.

Track 26
PILOT: MAYDAY MAYDAY MAYDAY, Winton Control, Sunair 165, we have fire in the hold, we are making an emergency descent to FL30, leaving FL310, left of Green 4, heading to Newbridge for emergency landing, please advise. Present position, radial 040, 50 miles from Winton VOR.

Track 27
PILOT: Winton Control, Sunair 883, we are unable to control pressurisation, cabin altitude is rising fast, request immediate descent to flight level 120.
ATC: Roger, descend to flight level 120, report reaching.
PILOT: Descending to FL120, Sunair 883.
PILOT: Sunair 83, reaching FL120.
ATC: Roger, Sunair 883, what are your intentions?
PILOT: Request resume our flight to Rexbury at this level.

Track 28
PILOT: Sunair 596, could we have a slightly lower flight level? We're experiencing moderate turbulence at this level.
ATC: Sunair 596, call you back.
ATC: Sunair 596, descend to FL280.
PILOT: Descending to FL280, Sunair 596.

Track 29
PILOT: Sunair 725, request divert to Overby, a passenger is seriously ill, probably a heart attack.
ATC: Roger Sunair 725, turn right heading 290, I'll tell Overby you require medical assistance on landing.
PILOT: Turning right 290, Sunair 725.

Track 30
PILOT: MAYDAY, MAYDAY, MAYDAY, Sunair 822, there is depressurisation, we are making an emergency descent to FL25, heading to Overby for emergency landing.

Track 31
PILOT: Sunair 506, we have lost all electrical power, except the emergency circuit. Request to divert immediately to Newbridge.
ATC: Roger, Sunair 506, turn left heading 030, descend to FL150.
PILOT: Turning left heading 030, leaving FL330, descending to level 150, Sunair 506.

Track 32
ATC: Sunair 312, request 10 degrees heading change right of track to avoid build-up.
PILOT: Roger, Sunair 312, what will your heading be?
PILOT: Heading 250 degrees, Sunair 312.
PILOT: Sunair 312, we're clear of CBs now.
ATC: Roger, Sunair 312, turn left heading 230 to come back on track.

Track 33
ATC: SF153, unknown traffic, 10 o'clock, 5 miles crossing left to right.
PILOT: SF153, negative contact, request vectors.
ATC: Turn left, heading 050.
PILOT: Left turn, heading 050, SF153.
ATC: SF153, clear of traffic, resume own navigation, direct C, magnetic track 070, distance 27 miles.
PILOT: Roger, track 070, SF153

Track 34
PILOT: Sunair 593, we've just had to dive to avoid colliding with converging traffic.
ATC: Do you have any other details? Did you see the type or the markings?
PILOT: It was a white jet, that's all we know.
ATC: Do you wish to file an airmiss report?
PILOT: Affirm. It was a very close thing. I'll check if the passengers are OK.
PILOT: Sunair 593, six passengers have been badly bruised, but there's a doctor on board, so we'll continue on our route.
ATC: Roger, Sunair 593.

Track 35
PILOT: Sunair 715, we have a serious fuel leak, request divert to Overby.
ATC: Sunair 715, turn right now, heading 280, descend to FL110.
PILOT: Turning right 280, leaving level 180, descending to FL110, Sunair 715.
ATC: Do you require emergency assistance at Overby?
PILOT: Affirm, Sunair 715.
ATC: Roger, will advise.

Track 36
ATC: Sunair 177, Winton Control, your company has informed us you may have a bomb on board.
PILOT: Do you have any information about the type of bomb?
ATC: Negative.
PILOT: Diverting immediately to Newbridge, request emergency services on landing, Sunair 177.

Track 37
PILOT: Winton Control, Sunair 939, ready to descend.
ATC: Roger, Sunair 939, descend to FL190.
PILOT: Leaving FL310, descending to FL190, Sunair 939. (pause)
PILOT: Sunair 939, we're having problems with the pressurization, we'll have to descend slowly.
ATC: Roger, Sunair 939, recleared to FL170, call me back when reaching.
PILOT: Descending to FL170, Sunair 939.

Track 38
PILOT: MAYDAY MAYDAY MAYDAY, Winton Control, Sunair 662, we have fire in the rear toilets, we are descending to FL30, request an emergency landing at Winton, position, 50 miles West of Winton, heading 75 degrees.
ATC: Sunair 662, Winton Control, roger Mayday, break. All stations on 126.3 stop transmitting, Mayday. (pause)
PILOT: Mayday Winton. Sunair 662, fire now under control, cancel distress.
ATC: Roger, Sunair 662. Mayday all stations distress traffic ended.

Track 39
PILOT: Sunair 779, transmitting blind due to receiver failure. Sunair 779, FL 290, heading 110, over Plaintree VOR this time, descending to be at FL100 over RIV intersection, standard arrival procedure next for landing runway 32 at Winton.

Track 40
PILOT: SF 662, Orly Tower, our left main landing gear is jammed.
ATC: SF 662, what are your intentions?
PILOT: Request proceed to holding area in order to carry out complete check.
ATC: Roger, climb 2000 ft and turn left heading 350 to MEL VOR.
PILOT: Climbing 2000 ft, turning left heading 350 to MEL. (pause)
PILOT: SF 662, over MEL 2000 ft, landing gear down but maybe not locked. We intend to make a low pass near the Tower to have the undercarriage checked.
ATC: Roger, make a low pass at 200 ft heading 200, North of Tower.
PILOT: At 200 ft, heading 200, North of Tower. (pause)
ATC: SF662, your landing gear seems to be completely extended.
PILOT: SF662, request emergency services and we intend to land.

Track 41
PILOT: Sunair 594, outer marker.
ATC: Sunair 594, you're number 1 to land. Caution wind shear reported at 600 feet 2 miles final, runway 07.
PILOT: Number 1 to land, Sunair 594. (pause)
PILOT: Sunair 594, going around.
ATC: Sunair 594, standard procedure, when passing 1000 ft, turn right to Redhill VOR.

Track 42
PILOT: Sunair 572, unable to extend flaps beyond 10 degrees. Request high speed flat approach to runway 26 which is the longest available.
ATC: Roger, Sunair 572, proceed to holding pattern over RIV VOR while we sort out the traffic, call you back when ready.
PILOT: Thank you Winton, request emergency services for landing, Sunair 572.

Track 43
PILOT: Winton Tower, Sunair 323, over outer marker, good morning.
ATC: Sunair 323, good morning, you are number 2 for landing, report short final.
PILOT: Number 2 to land, Sunair 323. (pause)
PILOT: Sunair 323, short final.
ATC: Sunair 323, the aircraft in front of you is unable to vacate the runway, go around.
PILOT: Going around, Sunair 323. (pause)
PILOT: Approach, Sunair 323.
ATC: Sunair 323, climb 4000 ft, proceed to Redhill holding pattern, runway 07 is blocked by a crashed aircraft.
PILOT: Roger, Sunair 323, may we proceed to runway 12?
ATC: Standby one, I'll call you back.
ATC: Sunair 323, can you accept a crosswind of 18 knots gusting to 25?
PILOT: Affirm, Sunair 323.

Track 44
ATC: Sunair 350, cleared to land, wind 320 degrees 12 knots.
PILOT: Cleared to land, Sunair 350. (pause)
PILOT: Winton Tower, Sunair 350, we aquaplaned after touch-down and have at least 2 tyres blown out on right main gear. We are unable to vacate the runway, please advise company maintenance and we request passenger steps and buses to take the passengers to the terminal.

Track 45
PILOT: Winton Tower, Sunair 697, long final.
ATC: Sunair 697, number 1 to land, wind calm. (pause)
ATC: Sunair 697, go around, standard procedure, there's a runway lighting failure.
PILOT: Going around. Confirm the standard procedure, Sunair 697.
ATC: Climb 3000 feet on runway heading and contact Approach on 121.3.
PILOT: Climbing 3000 ft, and Approach on 121.3.
PILOT: Winton Approach, Sunair 697.
ATC: Sunair 697, proceed to holding area over Redhill.
PILOT: We're running low on fuel, we cannot hold longer than five minutes, do you know how long the delay will be?
ATC: Delay is undetermined for the moment there seems to be a problem with the generators.
PILOT: Request divert to Overby, Sunair 697.

Track 46
ATC: Sunair 229, take the first convenient turn-off, then turn right into taxiway Bravo.
PILOT: Sunair 229, runway vacated.
ATC: Sunair 229, stop taxi, a 727 has taken a wrong turning and is blocking the taxiway. You'll have to wait until a tug pushes him back beyond the next intersection.
PILOT: Roger, holding, Sunair 229.

Track 47
ATC: Sunair 223, take the second left and contact Ground on 121.7.
PILOT: 121.7, Sunair 223.
PILOT: Winton Ground, Sunair 223, good morning. We seem to have had a nose gear tyre blow out on landing. Request a tug to tow us to the apron.
ATC: Roger, Sunair 223, can you move forward under your own power, 50 yards or so until you're past the next intersection?
PILOT: Affirm, I think we can manage that, slowly.
ATC: Thank you, Sunair 223, we'll get a tug out to you as soon as possible.

Track 48
ATC: Departure information Foxtrot, 02.30 hours weather, surface wind 250 degrees 10 knots gusting to 20, temperature 8, dew point 6, QNH 1011 millibars, departure runway 33.

Track 49
ATC: Departure information Golf, take-off runway 28R, 330 degrees 20 knots, visibility 10 km or more, temperature +1, dew point -3, QNH 1022, no sig.

Track 50
ATC: This is Heathrow Departure information E, 18.15 hours weather, 200 degrees 09 knots; temperature +21, dew point +09, QNH 1017 millibars, departure runway 28L.
"""

@st.cache_data
def get_transcripts_dict():
    tracks = re.split(r'(Track \d+)', TRANSCRIPT_TEXT)
    t_dict = {}
    current_track = None
    for part in tracks:
        if part.startswith('Track'):
            current_track = part.strip()
        elif current_track:
            t_dict[current_track] = part.strip()
    return t_dict

# --- 2. QUẢN LÝ TRẠNG THÁI ---
def init_states():
    if 'user_name' not in st.session_state: st.session_state.user_name = ""
    if 'db_loaded' not in st.session_state: st.session_state.db_loaded = False
    
    # Ở đây chúng ta thay thế bộ nhớ 'từng câu' bằng bộ nhớ 'từng Track'
    if 'tracks_completed' not in st.session_state: st.session_state.tracks_completed = []

init_states()

# --- 3. CÁC HÀM TỰ ĐỘNG ĐỒNG BỘ CLOUD (THEO TRACK) ---
def fetch_progress_from_db(user):
    if not API_URL: return None
    try:
        # Gửi request không chạy nền để đảm bảo lấy được dữ liệu khi F5
        res = requests.get(f"{API_URL}?action=get_progress&user={user}", timeout=5)
        if res.status_code == 200: return res.json()
    except: pass
    return None

def save_icao_progress():
    # Khi nút "Bài tiếp theo" được bấm, đẩy danh sách Track đã xong lên Drive
    if not API_URL or st.session_state.user_name == "": return
    payload = {
        "user": st.session_state.user_name, 
        "track_completed": json.dumps(st.session_state.tracks_completed)
    }
    # Sử dụng request.post thẳng (không chạy nền) để đảm bảo không rớt mạng giữa chừng khi chuyển trang
    try:
        requests.post(API_URL, json=payload, timeout=5)
    except: pass

def complete_track_and_next(tracks_list):
    # Đánh dấu Track hiện tại là đã xong
    current_track = st.session_state.selected_track_key
    if current_track not in st.session_state.tracks_completed:
        st.session_state.tracks_completed.append(current_track)
        save_icao_progress() # Đồng bộ lên Cloud ngay lập tức
    
    # Chuyển sang bài tiếp theo
    current_idx = tracks_list.index(current_track)
    if current_idx < len(tracks_list) - 1:
        st.session_state.selected_track_key = tracks_list[current_idx + 1]

def go_prev_track(tracks_list):
    current_idx = tracks_list.index(st.session_state.selected_track_key)
    if current_idx > 0:
        st.session_state.selected_track_key = tracks_list[current_idx - 1]

# --- 4. TẢI DỮ LIỆU ĐỀ THI VÀ AUDIO ---
@st.cache_data(ttl=60)
def load_database():
    sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQo3-ExtlDVOnEaTOC2rJMMzbHbazP2CxWGCNG7nyjKwaj8I9EyAfapCg6EUQxi5POgufMmkSxpRXf-/pub?output=tsv"
    df = pd.read_csv(sheet_url, sep='\t')
    return df.dropna(subset=['Track_Name'])

df = load_database()
transcript_dict = get_transcripts_dict()

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
    
    st.markdown("<br><hr><p style='text-align: center; color: gray; font-style: italic;'>💡 Tiến độ bài nghe của bạn sẽ được lưu theo Track lên Cloud, tắt máy mở lại không bị mất.</p>", unsafe_allow_html=True)
    st.stop()

# --- TẢI TIẾN ĐỘ TỪ CLOUD ---
if not df.empty and not st.session_state.db_loaded:
    with st.spinner("🔄 Đang đồng bộ tiến độ ôn tập từ Cloud..."):
        progress = fetch_progress_from_db(st.session_state.user_name)
        
        if progress and progress.get("status") == "found":
            tracks_str = progress.get("track_completed", "[]")
            if tracks_str:
                st.session_state.tracks_completed = json.loads(tracks_str)
        else:
            st.session_state.tracks_completed = []
            
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
    
    completed_count = len(st.session_state.tracks_completed)
    total_tracks = len(unique_tracks)
    st.info(f"📊 Tiến độ tổng: **{completed_count}/{total_tracks}** Track")

    # Tạo giao diện Danh sách Track (Đánh dấu check cho bài đã học)
    display_tracks = []
    for t in unique_tracks:
        if t in st.session_state.tracks_completed:
            display_tracks.append(f"✅ {t}")
        else:
            display_tracks.append(f"📖 {t}")

    # Đồng bộ hóa hộp chọn với lựa chọn hiện tại
    current_display = f"✅ {st.session_state.selected_track_key}" if st.session_state.selected_track_key in st.session_state.tracks_completed else f"📖 {st.session_state.selected_track_key}"
    
    selected_display = st.selectbox(
        "📌 Danh sách Track:", 
        display_tracks,
        index=display_tracks.index(current_display)
    )
    # Tách chuỗi hiển thị để lấy lại tên Track gốc (VD: "✅ Track 01" -> "Track 01")
    st.session_state.selected_track_key = selected_display[2:].strip()
    
    if st.button("🗑️ Xóa toàn bộ tiến độ"):
        st.session_state.tracks_completed = []
        save_icao_progress()
        st.rerun()
        
    st.write("---")

# --- 7. KHU VỰC HIỂN THỊ CHÍNH ---
st.title("✈️ Luyện nghe Tiếng Anh Hàng không")

if df.empty:
    st.warning("⚠️ Cơ sở dữ liệu đang trống hoặc link tải file bị lỗi.")
else:
    selected_track = st.session_state.selected_track_key
    track_data = df[df['Track_Name'] == selected_track]
    
    st.markdown("---")
    st.subheader(f"Đang phát: {selected_track}")
    
    # 7.1. PHÁT AUDIO
    drive_id = track_data.iloc[0]['Drive_ID']
    if pd.isna(drive_id) or str(drive_id).strip() == "":
        st.error("⚠️ Bài này chưa có ID Audio.")
    else:
        with st.spinner('Đang tải Audio...'):
            audio_bytes = load_audio(drive_id)
            st.audio(audio_bytes, format="audio/mp3")

    # 7.2. HIỂN THỊ TRANSCRIPT (KỊCH BẢN) NGAY DƯỚI AUDIO
    with st.expander("📖 Xem Transcript (Kịch bản hội thoại)"):
        script_text = transcript_dict.get(selected_track, "Chưa có dữ liệu Transcript cho bài này.")
        st.markdown(script_text.replace('\n', '  \n'))

    # 7.3. HIỂN THỊ CÂU HỎI VÀ ĐÁP ÁN (Dọn sạch ô nhập liệu)
    st.markdown("### 📝 Câu hỏi bài tập")

    if selected_track in st.session_state.tracks_completed:
        st.success("✅ Bạn đã ôn xong Track này!")

    for i, (index, row) in enumerate(track_data.iterrows()):
        with st.container():
            st.write(f"**Câu {i+1}: {row['Question']}**")
            
            with st.expander(f"👁️ Xem đáp án chuẩn"):
                st.info(f"**Đáp án:** {row['Answer']}")
            st.markdown("<br>", unsafe_allow_html=True)

    # --- KHU VỰC NÚT ĐIỀU HƯỚNG BÀI NGHE ---
    st.write("---")
    col1, col2, col3 = st.columns([1, 4, 1])
    
    current_track_idx = unique_tracks.index(selected_track)
    
    if current_track_idx > 0:
        col1.button("⬅ Bài trước", on_click=go_prev_track, args=(unique_tracks,))

    if current_track_idx < len(unique_tracks) - 1:
        # Nút Next Track đóng vai trò đánh dấu hoàn thành toàn bộ Track lên Cloud
        col3.button("Hoàn tất & Sang bài tiếp theo ➡️", on_click=complete_track_and_next, args=(unique_tracks,), type="primary")
    else:
        if col3.button("Hoàn tất toàn bộ 🎉", type="primary"):
            if selected_track not in st.session_state.tracks_completed:
                st.session_state.tracks_completed.append(selected_track)
                save_icao_progress()
            st.success("Chúc mừng bạn đã ôn xong 50 bài nghe!")
            st.balloons()
