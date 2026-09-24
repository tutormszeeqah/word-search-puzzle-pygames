import random
import string
import time
import gspread
from google.oauth2.service_account import Credentials
import streamlit as st

# Configure page layout
st.set_page_config(
    page_title="CIE 9618 Interactive Word Search",
    page_icon="🧩",
    layout="wide"
)

# Custom CSS for uniform cell styling & active highlights
st.markdown("""
<style>
    /* Styling for grid letter buttons */
    div.stButton > button {
        width: 100% !important;
        height: 48px !important;
        font-size: 18px !important;
        font-weight: bold !important;
        border-radius: 6px !important;
        border: 2px solid #3182ce !important;
        color: #1a202c !important;
        background-color: #ffffff !important;
        padding: 0px !important;
    }
    div.stButton > button:hover {
        background-color: #ebf8ff !important;
        border-color: #2b6cb0 !important;
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

# Target vocabulary for the topic
WORD_DATA = {
    "HEXADECIMAL": "Base-16 positional number system used in low-level programming.",
    "RAM": "Volatile main memory used for temporary working data storage.",
    "BANDWIDTH": "The maximum data transfer rate across a network path."
}

def calculate_dynamic_grid_size(words):
    """Calculates grid dimensions based on the longest word length."""
    max_len = max(len(w) for w in words)
    # Add a buffer of 2 cells so words aren't squished against edges
    return max(max_len + 2, 8)

def create_word_search(words, grid_size):
    """Generates a grid_size x grid_size matrix filled with hidden words & random filler letters."""
    grid = [["" for _ in range(grid_size)] for _ in range(grid_size)]
    
    # Simple horizontal placement
    for idx, word in enumerate(words):
        row = idx * 2  # Place words on alternating rows
        if row < grid_size:
            max_start_col = grid_size - len(word)
            start_col = random.randint(0, max_start_col)
            for c_idx, char in enumerate(word):
                grid[row][start_col + c_idx] = char
                
    # Fill empty spots with random letters
    for r in range(grid_size):
        for c in range(grid_size):
            if grid[r][c] == "":
                grid[r][c] = random.choice(string.ascii_uppercase)
                
    return grid

# Calculate dynamic size based on current word list
GRID_SIZE = calculate_dynamic_grid_size(list(WORD_DATA.keys()))

# Session State Initialization
if "start_time" not in st.session_state:
    st.session_state.start_time = time.time()

if "grid" not in st.session_state:
    st.session_state.grid = create_word_search(list(WORD_DATA.keys()), GRID_SIZE)

if "selected_cells" not in st.session_state:
    # Stores selected coordinates as a set: {(row, col), ...}
    st.session_state.selected_cells = set()

# Main Header & Controls
st.title("🧩 CIE 9618 Interactive Word Search")

ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([1, 1, 2])
with ctrl_col1:
    if st.button("🔄 RESTART GAME"):
        st.session_state.start_time = time.time()
        st.session_state.grid = create_word_search(list(WORD_DATA.keys()), GRID_SIZE)
        st.session_state.selected_cells = set()
        st.rerun()

with ctrl_col2:
    if st.button("🧹 CLEAR HIGHLIGHTS"):
        st.session_state.selected_cells = set()
        st.rerun()

# Timer Display
elapsed_time = round(time.time() - st.session_state.start_time, 1)
st.metric("⏱ Live Time Duration", f"{elapsed_time} seconds")

st.markdown("---")

# Main Page Layout: Dynamic Grid (Left) | Clues & Inputs (Right)
col_grid, col_clues = st.columns([1.2, 1])

with col_grid:
    st.subheader(f"🔠 Puzzle Grid ({GRID_SIZE} × {GRID_SIZE})")
    st.caption("Click on letter cells to highlight them as you find words!")

    # Render dynamic button grid using Streamlit columns
    for r in range(GRID_SIZE):
        cols = st.columns(GRID_SIZE)
        for c in range(GRID_SIZE):
            letter = st.session_state.grid[r][c]
            cell_key = f"cell_{r}_{c}"
            is_highlighted = (r, c) in st.session_state.selected_cells

            # Use emoji or prefix indicator for highlighted state
            button_label = f"⭐ {letter}" if is_highlighted else letter

            if cols[c].button(button_label, key=cell_key):
                # Toggle highlight state on click
                if (r, c) in st.session_state.selected_cells:
                    st.session_state.selected_cells.remove((r, c))
                else:
                    st.session_state.selected_cells.add((r, c))
                st.rerun()

with col_clues:
    st.subheader("💡 Clues & Word Submission")
    user_answers = {}

    with st.form("leaderboard_form"):
        player_name = st.text_input("Player Name:", value="Student 1")
        
        for idx, (word, clue) in enumerate(WORD_DATA.items(), 1):
            st.markdown(f"**{idx}. {clue}**")
            user_answers[word] = st.text_input(
                f"Enter Word #{idx}", 
                key=f"ans_{idx}"
            ).strip().upper()
            
        submit = st.form_submit_button("Submit Answers & Record Score")

    if submit:
        # Check submitted answers against dictionary keys
        correct_answers = sum(1 for w, ans in user_answers.items() if ans == w)

        if correct_answers == len(WORD_DATA):
            st.balloons()
            st.success(f"🎉 Excellent! All words found in {elapsed_time} seconds!")
            
            # Send results to Google Sheets database
            try:
                sheet = init_google_sheet()
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                sheet.append_row([
                    player_name,
                    "Topic 1: Information Representation",
                    elapsed_time,
                    timestamp
                ])
                st.info("Score recorded on Google Sheets Leaderboard!")
            except Exception as e:
                st.error(f"Failed to record score: {e}")
        else:
            st.warning(f"You got {correct_answers}/{len(WORD_DATA)} correct. Keep checking the grid!")
