import random
import string
import time
import gspread
from google.oauth2.service_account import Credentials
import streamlit as st

# Configure page settings
st.set_page_config(page_title="CIE 9618 Word Search", page_icon="🧩", layout="wide")

# Apply CSS for square wireframe cells and custom button styling
st.markdown("""
<style>
    /* Compact zero-gap row spacing for exact wireframe look */
    div[data-testid="stHorizontalBlock"] {
        gap: 0px !important;
    }
    
    /* Grid cell buttons styled as border-touching squares */
    div.stButton > button {
        width: 100% !important;
        aspect-ratio: 1 / 1 !important;
        height: auto !important;
        font-size: 20px !important;
        font-weight: 900 !important;
        border-radius: 0px !important;
        border: 1.5px solid #000000 !important;
        color: #000000 !important;
        background-color: #ffffff !important;
        padding: 0px !important;
        margin: 0px !important;
    }

    /* Highlighted yellow cell state */
    div.stButton > button[kind="primary"] {
        background-color: #ffeb3b !important;
        color: #000000 !important;
        border: 2px solid #000000 !important;
    }

    /* Hover animation */
    div.stButton > button:hover {
        background-color: #e0e0e0 !important;
        border-color: #000000 !important;
    }
</style>
""", unsafe_allow_html=True)

# Google Sheets API Authentication
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

@st.cache_resource
def init_google_sheet():
    """Connects to Google Sheets using Streamlit secrets."""
    creds_dict = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    client = gspread.authorize(creds)
    return client.open("CIE-Leaderscore-Board").worksheet("COMPSCI")

# Vocabulary & Clues Dictionary
TOPIC_DATA = {
    "Topic 1: Information Representation": {
        "MEDIA": "Composed of sound and images.",
        "CACHE": "Fastest storage access.",
        "BIT": "The smallest unit stored in computer.",
    }
}

def generate_guaranteed_grid(words, grid_size=7):
    """Guarantees every target word is accurately placed inside the N x N grid."""
    grid = [["" for _ in range(grid_size)] for _ in range(grid_size)]
    placed_positions = {}  # Tracks placed word character coordinates

    # Place each word horizontally on a separate row
    for row_idx, word in enumerate(words):
        if row_idx < grid_size:
            max_col = grid_size - len(word)
            start_col = random.randint(0, max_col)
            
            coords = []
            for c_offset, letter in enumerate(word):
                r, c = row_idx, start_col + c_offset
                grid[r][c] = letter
                coords.append((r, c))
            
            placed_positions[word] = coords

    # Fill all remaining empty matrix spots with random uppercase letters
    for r in range(grid_size):
        for c in range(grid_size):
            if grid[r][c] == "":
                grid[r][c] = random.choice(string.ascii_uppercase)

    return grid, placed_positions

# Initialize Session States
GRID_SIZE = 7

if "selected_topic" not in st.session_state:
    st.session_state.selected_topic = "Topic 1: Information Representation"

word_dict = TOPIC_DATA[st.session_state.selected_topic]

if "start_time" not in st.session_state:
    st.session_state.start_time = time.time()

if "grid" not in st.session_state or "placed_positions" not in st.session_state:
    grid, placed_positions = generate_guaranteed_grid(list(word_dict.keys()), GRID_SIZE)
    st.session_state.grid = grid
    st.session_state.placed_positions = placed_positions

if "selected_cells" not in st.session_state:
    st.session_state.selected_cells = set()

# --- TOP BAR: NAME & TOPIC SELECTOR ---
top_col1, top_col2 = st.columns([1, 3])

with top_col1:
    player_name = st.text_input("TYPE NAME", value="Student 1", key="player_name_input")

with top_col2:
    selected_topic = st.selectbox("Topic Choice", list(TOPIC_DATA.keys()), key="topic_select")

st.markdown("<br>", unsafe_allow_html=True)

# --- MAIN SECTION: PUZZLE GRID & CLUES LIST ---
col_grid, col_clues = st.columns([1, 1])

# Left Column: Square Grid Matrix
with col_grid:
    st.subheader(f"Puzzle Grid ({GRID_SIZE} × {GRID_SIZE})")
    
    for r in range(GRID_SIZE):
        cols = st.columns(GRID_SIZE)
        for c in range(GRID_SIZE):
            letter = st.session_state.grid[r][c]
            cell_key = f"cell_{r}_{c}"
            is_highlighted = (r, c) in st.session_state.selected_cells

            button_type = "primary" if is_highlighted else "secondary"

            if cols[c].button(letter, key=cell_key, type=button_type):
                if (r, c) in st.session_state.selected_cells:
                    st.session_state.selected_cells.remove((r, c))
                else:
                    st.session_state.selected_cells.add((r, c))
                st.rerun()

# Right Column: Clues List & Control Buttons
with col_clues:
    st.subheader("Clues & Word Submission")
    
    # Render numbering starting at 1 (removed text input boxes)
    for idx, (word, clue) in enumerate(word_dict.items(), start=1):
        st.markdown(f"**{idx}. {clue}**")
        st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("---")

    # Wireframe Control Buttons
    ctrl_col1, ctrl_col2, ctrl_col3 = st.columns(3)
    
    with ctrl_col1:
        submit_game = st.button("SUBMIT GAME")
        
    with ctrl_col2:
        if st.button("PLAY / RESTART"):
            st.session_state.start_time = time.time()
            grid, placed_positions = generate_guaranteed_grid(list(word_dict.keys()), GRID_SIZE)
            st.session_state.grid = grid
            st.session_state.placed_positions = placed_positions
            st.session_state.selected_cells = set()
            st.rerun()

    with ctrl_col3:
        if st.button("CLEAR HIGHLIGHTS"):
            st.session_state.selected_cells = set()
            st.rerun()

    # Automatic Verification Logic
    if submit_game:
        elapsed_time = round(time.time() - st.session_state.start_time, 1)
        
        # Verify if all coordinates for each word are highlighted
        found_words = 0
        for word, coords in st.session_state.placed_positions.items():
            if all(coord in st.session_state.selected_cells for coord in coords):
                found_words += 1

        total_words = len(word_dict)
        
        if found_words == total_words:
            st.balloons()
            st.success(f"🎉 Perfect! All {total_words} words highlighted correctly in {elapsed_time}s!")
            try:
                sheet = init_google_sheet()
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                sheet.append_row([player_name, selected_topic, elapsed_time, timestamp])
                st.info("Score recorded on Google Sheets Leaderboard!")
            except Exception as e:
                st.error(f"Could not connect to database: {e}")
        else:
            st.warning(f"You found {found_words}/{total_words} words. Highlight all target letters on the grid!")
