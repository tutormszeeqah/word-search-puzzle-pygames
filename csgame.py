import random
import string
import time
import gspread
from google.oauth2.service_account import Credentials
import streamlit as st

# Set page configuration to wide mode
st.set_page_config(page_title="CIE 9618 Word Puzzle", page_icon="🧩", layout="wide")

# Custom CSS to force exact square cells, compact spacing, and wireframe styling
st.markdown("""
<style>
    /* Force buttons to be perfect square cells and remove gap spacing */
    div[data-testid="stHorizontalBlock"] {
        gap: 0px !important;
    }
    
    /* Style button cells as wireframe squares */
    div.stButton > button {
        width: 100% !important;
        aspect-ratio: 1 / 1 !important; /* Enforces strict square proportions */
        height: auto !important;
        font-size: 20px !important;
        font-weight: 900 !important;
        border-radius: 0px !important; /* Flat sharp corners */
        border: 1.5px solid #000000 !important; /* Solid black border */
        color: #000000 !important;
        background-color: #ffffff !important;
        padding: 0px !important;
        margin: 0px !important;
    }

    /* Highlighted square cell state */
    div.stButton > button[kind="primary"] {
        background-color: #ffeb3b !important; /* Yellow background */
        color: #000000 !important;
        border: 2px solid #000000 !important;
    }

    /* Hover effect */
    div.stButton > button:hover {
        background-color: #e0e0e0 !important;
        border-color: #000000 !important;
    }
</style>
""", unsafe_allow_html=True)

# Google Sheets Setup
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

@st.cache_resource
def init_google_sheet():
    """Authenticates with Google Sheets API using Streamlit secrets."""
    creds_dict = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    client = gspread.authorize(creds)
    return client.open("CIE-Leaderscore-Board").worksheet("COMPSCI")

# Word search vocabulary & clues database
TOPIC_DATA = {
    "Topic 1: Information Representation": {
        "MEDIA": "Composed of sound and images.",
        "CACHE": "Fastest storage access.",
        "BIT": "The smallest unit stored in computer.",
    }
}

def create_word_search(words, grid_size=7):
    """Generates a grid_size x grid_size matrix filled with hidden words & random filler letters."""
    grid = [["" for _ in range(grid_size)] for _ in range(grid_size)]
    
    # Place words horizontally
    for idx, word in enumerate(words):
        row = idx * 2
        if row < grid_size:
            max_start_col = max(0, grid_size - len(word))
            start_col = random.randint(0, max_start_col)
            for c_idx, char in enumerate(word):
                if start_col + c_idx < grid_size:
                    grid[row][start_col + c_idx] = char
                
    # Fill remaining empty cells with random uppercase letters
    for r in range(grid_size):
        for c in range(grid_size):
            if grid[r][c] == "":
                grid[r][c] = random.choice(string.ascii_uppercase)
                
    return grid

# Session State Initialization
if "selected_topic" not in st.session_state:
    st.session_state.selected_topic = "Topic 1: Information Representation"

word_dict = TOPIC_DATA[st.session_state.selected_topic]
GRID_SIZE = 7  # Fixed grid size matching wireframe style (7x7)

if "start_time" not in st.session_state:
    st.session_state.start_time = time.time()

if "grid" not in st.session_state:
    st.session_state.grid = create_word_search(list(word_dict.keys()), GRID_SIZE)

if "selected_cells" not in st.session_state:
    st.session_state.selected_cells = set()

# --- TOP SECTION: NAME & TOPIC CHOICE ---
top_col1, top_col2 = st.columns([1, 3])

with top_col1:
    player_name = st.text_input("TYPE NAME", value="Student 1", key="player_name_input")

with top_col2:
    selected_topic = st.selectbox(
        "Topic Choice", 
        list(TOPIC_DATA.keys()), 
        key="topic_select"
    )

st.markdown("<br>", unsafe_allow_html=True)

# --- MAIN CONTENT: GRID (LEFT) & CLUES / CONTROLS (RIGHT) ---
main_col_left, main_col_right = st.columns([1, 1])

# Left Column: Square Grid Matrix
with main_col_left:
    st.subheader(f"Puzzle Grid ({GRID_SIZE} × {GRID_SIZE})")
    
    for r in range(GRID_SIZE):
        cols = st.columns(GRID_SIZE)
        for c in range(GRID_SIZE):
            letter = st.session_state.grid[r][c]
            cell_key = f"cell_{r}_{c}"
            is_highlighted = (r, c) in st.session_state.selected_cells

            # Use primary button style for yellow highlighted background
            button_type = "primary" if is_highlighted else "secondary"

            if cols[c].button(letter, key=cell_key, type=button_type):
                if (r, c) in st.session_state.selected_cells:
                    st.session_state.selected_cells.remove((r, c))
                else:
                    st.session_state.selected_cells.add((r, c))
                st.rerun()

# Right Column: Clues, Inputs, & Action Buttons
with main_col_right:
    st.subheader("Clues & Word Submission")
    
    # Display Clues List
    user_answers = {}
    with st.form("answers_form"):
        for idx, (word, clue) in enumerate(word_dict.items(), 7):
            st.write(f"**{idx}. {clue}**")
            user_answers[word] = st.text_input(
                f"Enter Word for #{idx}", 
                key=f"ans_{idx}"
            ).strip().upper()
            
        submit_game = st.form_submit_button("SUBMIT GAME")

    st.markdown("---")
    
    # Action Control Buttons Matching Wireframe Layout
    ctrl_row1_col1, ctrl_row1_col2, ctrl_row1_col3 = st.columns(3)
    
    with ctrl_row1_col1:
        if st.button("SCOREBOARD"):
            st.info("Leaderboard is active and connected to Google Sheets!")
            
    with ctrl_row1_col2:
        if st.button("PLAY"):
            st.session_state.start_time = time.time()
            st.session_state.grid = create_word_search(list(word_dict.keys()), GRID_SIZE)
            st.session_state.selected_cells = set()
            st.rerun()

    with ctrl_row1_col3:
        if st.button("CLEAR HIGHLIGHTS"):
            st.session_state.selected_cells = set()
            st.rerun()

    # Form Submission Handler
    if submit_game:
        elapsed_time = round(time.time() - st.session_state.start_time, 1)
        correct_count = sum(1 for w, ans in user_answers.items() if ans == w)
        
        if correct_count == len(word_dict):
            st.balloons()
            st.success(f"🎉 Perfect! Completed in {elapsed_time} seconds!")
            try:
                sheet = init_google_sheet()
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                sheet.append_row([player_name, selected_topic, elapsed_time, timestamp])
                st.info("Score successfully uploaded to Google Sheets!")
            except Exception as e:
                st.error(f"Score upload failed: {e}")
        else:
            st.warning(f"You got {correct_count}/{len(word_dict)} correct. Try again!")
