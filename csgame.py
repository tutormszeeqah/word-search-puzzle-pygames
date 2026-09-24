import streamlit as st
import time
import pandas as pd
import random
import string
import gspread
from google.oauth2.service_account import Credentials

# ---------------------------------------------------------------------------
# 1. PAGE CONFIGURATION & CUSTOM CSS STYLING
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="CIE 9618 CS Word Search Portal",
    page_icon="🧩",
    layout="wide"
)

# Custom CSS for UI cards, podium boxes, and grid typography
st.markdown("""
<style>
    .podium-box {
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        color: white;
        font-weight: bold;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 15px;
    }
    .gold { background: linear-gradient(135deg, #FFD700, #FFA500); color: #333; }
    .silver { background: linear-gradient(135deg, #C0C0C0, #808080); color: #fff; }
    .bronze { background: linear-gradient(135deg, #CD7F32, #8B4513); color: #fff; }
    
    .grid-cell {
        display: inline-block;
        width: 24px;
        height: 24px;
        line-height: 24px;
        text-align: center;
        font-family: monospace;
        font-weight: bold;
        border: 1px solid #e2e8f0;
        margin: 1px;
        border-radius: 3px;
        background-color: #ffffff;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# 2. GOOGLE SHEETS CONNECTION & DATA ENGINE
# ---------------------------------------------------------------------------
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def get_sheet_client():
    """Connects to Google Sheets using local key file or Streamlit Secrets."""
    try:
        # Tries Streamlit Secrets first, falls back to local json file
        if "gcp_service_account" in st.secrets:
            creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=SCOPES)
        else:
            creds = Credentials.from_service_account_file("google_key.json", scopes=SCOPES)
        client = gspread.authorize(creds)
        return client.open("CIE_9618_Leaderboard").sheet1
    except Exception as e:
        return None

def update_leaderboard(player_name, topic, duration):
    """Saves or updates player score in Google Sheets (replaces if better time)."""
    sheet = get_sheet_client()
    if not sheet:
        return

    records = sheet.get_all_records()
    now_str = time.strftime("%Y-%m-%d %H:%M:%S")
    
    # Check if player already exists
    player_found = False
    for i, row in enumerate(records, start=2): # Row 1 is header
        if str(row.get("Player Name")).strip().lower() == player_name.strip().lower():
            player_found = True
            existing_time = float(row.get("Duration (seconds)", 999999))
            # Replace score if the new time is faster
            if duration < existing_time:
                sheet.update_cell(i, 2, topic)
                sheet.update_cell(i, 3, round(duration, 2))
                sheet.update_cell(i, 4, now_str)
            break
            
    if not player_found:
        sheet.append_row([player_name, topic, round(duration, 2), now_str])

def fetch_leaderboard():
    """Fetches records from Google Sheets and returns sorted Pandas DataFrame."""
    sheet = get_sheet_client()
    if not sheet:
        # Return fallback sample data if database not yet connected
        data = [
            {"Player Name": "Alex", "Topic": "Topic 1", "Duration (seconds)": 34.2, "Timestamp": "2026-09-24"},
            {"Player Name": "Beatrix", "Topic": "Topic 1", "Duration (seconds)": 41.5, "Timestamp": "2026-09-24"},
            {"Player Name": "Charlie", "Topic": "Topic 2", "Duration (seconds)": 52.0, "Timestamp": "2026-09-24"},
            {"Player Name": "David", "Topic": "Topic 3", "Duration (seconds)": 68.1, "Timestamp": "2026-09-24"}
        ]
        return pd.DataFrame(data)

    records = sheet.get_all_records()
    if not records:
        return pd.DataFrame(columns=["Player Name", "Topic", "Duration (seconds)", "Timestamp"])
    
    df = pd.DataFrame(records)
    df["Duration (seconds)"] = pd.to_numeric(df["Duration (seconds)"])
    return df.sort_values(by="Duration (seconds)", ascending=True).reset_index(drop=True)

# ---------------------------------------------------------------------------
# 3. GAME DATA & GENERATOR
# ---------------------------------------------------------------------------
SYLLABUS_TOPICS = {
    "Topic 1: Information Representation": [
        {"clue": "Base-16 positional number system used in low-level programming.", "keyword": "HEXADECIMAL"},
        {"clue": "Volatile main memory used for temporary working data storage.", "keyword": "RAM"},
        {"clue": "Data transmission where bits travel sequentially one by one.", "keyword": "SERIAL"}
    ],
    "Topic 2: Communication and Networking": [
        {"clue": "Global system of interconnected computer networks.", "keyword": "INTERNET"},
        {"clue": "Unique numerical identifier assigned to every network device.", "keyword": "IPADDRESS"},
        {"clue": "Rules governing communication and data transfer between systems.", "keyword": "PROTOCOL"}
    ],
    "Topic 3: Hardware & System Software": [
        {"clue": "Component that performs arithmetic and logical operations.", "keyword": "ALU"},
        {"clue": "Translates high-level source code to machine code all at once.", "keyword": "COMPILER"},
        {"clue": "Network security system that monitors incoming traffic.", "keyword": "FIREWALL"}
    ]
}

# ---------------------------------------------------------------------------
# 4. SESSION STATE INITIALIZATION
# ---------------------------------------------------------------------------
if "player_name" not in st.session_state:
    st.session_state.player_name = ""
if "game_started" not in st.session_state:
    st.session_state.game_started = False
if "is_paused" not in st.session_state:
    st.session_state.is_paused = False
if "start_time" not in st.session_state:
    st.session_state.start_time = 0.0
if "accumulated_time" not in st.session_state:
    st.session_state.accumulated_time = 0.0
if "current_topic" not in st.session_state:
    st.session_state.current_topic = list(SYLLABUS_TOPICS.keys())[0]
if "solved_clues" not in st.session_state:
    st.session_state.solved_clues = set()

# ---------------------------------------------------------------------------
# 5. SIDEBAR CONTROLS
# ---------------------------------------------------------------------------
st.sidebar.title("🎮 Student Portal")
name_input = st.sidebar.text_input("Enter Student Name:", value=st.session_state.player_name, disabled=st.session_state.game_started)
if name_input:
    st.session_state.player_name = name_input

selected_topic = st.sidebar.selectbox("Choose 9618 Syllabus Topic:", list(SYLLABUS_TOPICS.keys()), disabled=st.session_state.game_started)
st.session_state.current_topic = selected_topic

# ---------------------------------------------------------------------------
# 6. MAIN INTERFACE & CONTROL BUTTONS
# ---------------------------------------------------------------------------
st.title("🧩 CIE 9618 Computer Science Game Portal")

if not st.session_state.player_name:
    st.warning("⚠️ Please enter your name in the sidebar to unlock the game controls.")
else:
    # Game Navigation Buttons
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        if st.button("▶️ PLAY", use_container_width=True, disabled=st.session_state.game_started):
            st.session_state.game_started = True
            st.session_state.is_paused = False
            st.session_state.start_time = time.time()
            st.session_state.accumulated_time = 0.0
            st.session_state.solved_clues = set()
            st.rerun()

    with c2:
        if st.session_state.game_started:
            if not st.session_state.is_paused:
                if st.button("⏸️ PAUSE", use_container_width=True):
                    st.session_state.is_paused = True
                    st.session_state.accumulated_time += time.time() - st.session_state.start_time
                    st.rerun()
            else:
                if st.button("▶️ RESUME", use_container_width=True):
                    st.session_state.is_paused = False
                    st.session_state.start_time = time.time()
                    st.rerun()

    with c3:
        if st.button("❌ QUIT", use_container_width=True, disabled=not st.session_state.game_started):
            st.session_state.game_started = False
            st.session_state.is_paused = False
            st.session_state.accumulated_time = 0.0
            st.rerun()

    with c4:
        if st.button("⏭️ NEXT LEVEL", use_container_width=True):
            topics = list(SYLLABUS_TOPICS.keys())
            idx = (topics.index(st.session_state.current_topic) + 1) % len(topics)
            st.session_state.current_topic = topics[idx]
            st.session_state.game_started = False
            st.session_state.accumulated_time = 0.0
            st.rerun()

    st.markdown("---")

    # ---------------------------------------------------------------------------
    # 7. GAMEPLAY & TIMER AREA
    # ---------------------------------------------------------------------------
    if st.session_state.game_started:
        if st.session_state.is_paused:
            st.info("⏸️ Game is Paused. Click RESUME to continue.")
        else:
            # Calculate Live Timer
            elapsed = st.session_state.accumulated_time + (time.time() - st.session_state.start_time)
            st.metric(label="⏱️ Live Time Duration", value=f"{elapsed:.1f} seconds")

            # Active Clues & Verification System
            st.subheader(f"Topic: {st.session_state.current_topic}")
            clues = SYLLABUS_TOPICS[st.session_state.current_topic]
            
            for idx, item in enumerate(clues, 1):
                col_clue, col_input = st.columns([3, 1])
                with col_clue:
                    st.write(f"**{idx}.** {item['clue']}")
                with col_input:
                    ans = st.text_input(f"Answer #{idx}", key=f"q_{idx}").strip().upper()
                    if ans == item['keyword']:
                        st.session_state.solved_clues.add(item['keyword'])
                        st.success("✓ Correct!")

            # Complete Level Trigger
            if len(st.session_state.solved_clues) == len(clues):
                final_time = st.session_state.accumulated_time + (time.time() - st.session_state.start_time)
                st.session_state.game_started = False
                
                st.balloons()
                st.success(f"🎉 Level Complete! Final Duration: {final_time:.2f} seconds.")
                
                # Update Leaderboard in Google Sheets
                update_leaderboard(st.session_state.player_name, st.session_state.current_topic, final_time)
                st.rerun()

    # ---------------------------------------------------------------------------
    # 8. LEADERBOARD DISPLAY (PODIUM BOXES + LIST)
    # ---------------------------------------------------------------------------
    st.markdown("---")
    st.header("🏆 Leaderboard (Shortest Time Wins)")

    df_ranks = fetch_leaderboard()

    if not df_ranks.empty:
        # TOP 3 SQUARE PODIUM BOXES
        top_cols = st.columns(3)
        
        # 1st Place Box (Gold)
        if len(df_ranks) >= 1:
            p1 = df_ranks.iloc[0]
            with top_cols[0]:
                st.markdown(f"""
                <div class="podium-box gold">
                    <h3>🥇 1st Place</h3>
                    <h2>{p1['Player Name']}</h2>
                    <p>{p1['Duration (seconds)']}s ({p1['Topic']})</p>
                </div>
                """, unsafe_allow_html=True)

        # 2nd Place Box (Silver)
        if len(df_ranks) >= 2:
            p2 = df_ranks.iloc[1]
            with top_cols[1]:
                st.markdown(f"""
                <div class="podium-box silver">
                    <h3>🥈 2nd Place</h3>
                    <h2>{p2['Player Name']}</h2>
                    <p>{p2['Duration (seconds)']}s ({p2['Topic']})</p>
                </div>
                """, unsafe_allow_html=True)

        # 3rd Place Box (Bronze)
        if len(df_ranks) >= 3:
            p3 = df_ranks.iloc[2]
            with top_cols[2]:
                st.markdown(f"""
                <div class="podium-box bronze">
                    <h3>🥉 3rd Place</h3>
                    <h2>{p3['Player Name']}</h2>
                    <p>{p3['Duration (seconds)']}s ({p3['Topic']})</p>
                </div>
                """, unsafe_allow_html=True)

        # REMAINING PLAYERS LIST (Rank 4+)
        if len(df_ranks) > 3:
            st.subheader("📊 Remaining Rankings")
            df_remaining = df_ranks.iloc[3:].copy()
            df_remaining.index = range(4, 4 + len(df_remaining))
            st.table(df_remaining[["Player Name", "Topic", "Duration (seconds)", "Timestamp"]])
