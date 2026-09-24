import random
import string
import time
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import streamlit as st

# Configure Streamlit page layout and title
st.set_page_config(
    page_title="CIE 9618 Word Search", page_icon="🧩", layout="wide"
)

# Apply CSS for square wireframe grid cells and highlight colors
st.markdown(
    """
<style>
    /* Zero-gap block layout for tight wireframe alignment */
    div[data-testid="stHorizontalBlock"] {
        gap: 0px !important;
    }
    
    /* Style grid buttons as square boxes */
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

    /* Primary highlight state when a cell is clicked */
    div.stButton > button[kind="primary"] {
        background-color: #ffeb3b !important;
        color: #000000 !important;
        border: 2px solid #000000 !important;
    }

    /* Cell hover effect */
    div.stButton > button:hover {
        background-color: #e0e0e0 !important;
        border-color: #000000 !important;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Google Sheets API Authentication Scope Setup
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


@st.cache_resource
def init_google_sheet():
    """Establishes connection to Google Sheets using Streamlit secrets credentials."""
    creds_dict = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    client = gspread.authorize(creds)
    return client.open("CIE-Leaderscore-Board").worksheet("COMPSCI")


# Vocabulary & Clues Database across CIE Computer Science Topics
TOPIC_DATA = {
    "Topic 1: Information Representation": {
        "MEDIA": "Composed of sound and images.",
        "CACHE": "Fastest storage access.",
        "BIT": "The smallest unit stored in computer.",
    },
    "Topic 2: Communication": {
        "ROUTER": "Directs data packets across networks.",
        "BANDWIDTH": "Data transfer capacity rate.",
        "SERVER": "Provides resources or services to clients.",
    },
    "Topic 3: Hardware": {
        "RAM": "Volatile temporary working storage.",
        "ROM": "Non-volatile memory holding boot instructions.",
        "REGISTER": "High-speed temporary processor storage.",
    },
    "Topic 4: Processor Fundamentals": {
        "ALU": "Performs arithmetic and logic operations.",
        "BUS": "Parallel wires transferring data/signals.",
        "FETCH": "First step of the CPU instruction cycle.",
    },
}


def generate_multidirectional_grid(words, grid_size=7):
    """Generates an N x N grid with words placed horizontally, vertically,

    or diagonally.
    """
    grid = [["" for _ in range(grid_size)] for _ in range(grid_size)]
    placed_positions = {}

    # Multi-directional movement vectors: (row_delta, col_delta)
    DIRECTIONS = [
        (0, 1),  # Horizontal (Left -> Right)
        (1, 0),  # Vertical (Top -> Bottom)
        (1, 1),  # Diagonal Down-Right
        (-1, 1),  # Diagonal Up-Right
    ]

    for word in words:
        placed = False
        attempts = 0

        while not placed and attempts < 100:
            attempts += 1
            dr, dc = random.choice(DIRECTIONS)

            start_r = random.randint(0, grid_size - 1)
            start_c = random.randint(0, grid_size - 1)

            end_r = start_r + dr * (len(word) - 1)
            end_c = start_c + dc * (len(word) - 1)

            # Ensure word fits within grid dimensions
            if 0 <= end_r < grid_size and 0 <= end_c < grid_size:
                can_place = True
                for i in range(len(word)):
                    r = start_r + dr * i
                    c = start_c + dc * i
                    if grid[r][c] != "" and grid[r][c] != word[i]:
                        can_place = False
                        break

                if can_place:
                    coords = []
                    for i in range(len(word)):
                        r = start_r + dr * i
                        c = start_c + dc * i
                        grid[r][c] = word[i]
                        coords.append((r, c))
                    placed_positions[word] = coords
                    placed = True

    # Fill remaining empty cells with random uppercase letters
    for r in range(grid_size):
        for c in range(grid_size):
            if grid[r][c] == "":
                grid[r][c] = random.choice(string.ascii_uppercase)

    return grid, placed_positions


# Set default grid dimensions
GRID_SIZE = 7

# Initialize Session States
if "selected_topic" not in st.session_state:
    st.session_state.selected_topic = "Topic 1: Information Representation"

if "start_time" not in st.session_state:
    st.session_state.start_time = time.time()

# --- TOP HEADER BAR: PLAYER NAME & TOPIC DROPDOWN ---
top_col1, top_col2 = st.columns([1, 3])

with top_col1:
    player_name = st.text_input(
        "TYPE NAME", value="Student 1", key="player_name_input"
    )

with top_col2:
    new_topic = st.selectbox(
        "Topic Choice",
        list(TOPIC_DATA.keys()),
        index=list(TOPIC_DATA.keys()).index(st.session_state.selected_topic),
        key="topic_select",
    )

    # Automatic state reset if the user switches topics
    if new_topic != st.session_state.selected_topic:
        st.session_state.selected_topic = new_topic
        word_dict = TOPIC_DATA[new_topic]
        grid, placed_positions = generate_multidirectional_grid(
            list(word_dict.keys()), GRID_SIZE
        )
        st.session_state.grid = grid
        st.session_state.placed_positions = placed_positions
        st.session_state.selected_cells = set()
        st.session_state.start_time = time.time()
        st.rerun()

word_dict = TOPIC_DATA[st.session_state.selected_topic]

if "grid" not in st.session_state or "placed_positions" not in st.session_state:
    grid, placed_positions = generate_multidirectional_grid(
        list(word_dict.keys()), GRID_SIZE
    )
    st.session_state.grid = grid
    st.session_state.placed_positions = placed_positions

if "selected_cells" not in st.session_state:
    st.session_state.selected_cells = set()

st.markdown("<br>", unsafe_allow_html=True)

# --- MAIN SECTION: PUZZLE GRID & CLUES ---
col_grid, col_clues = st.columns([1, 1])

# Left Column: Interactive Grid Buttons
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
            grid, placed_positions = generate_multidirectional_grid(
                list(word_dict.keys()), GRID_SIZE
            )
            st.session_state.grid = grid
            st.session_state.placed_positions = placed_positions
            st.session_state.selected_cells = set()
            st.rerun()

    with ctrl_col3:
        if st.button("CLEAR HIGHLIGHTS"):
            st.session_state.selected_cells = set()
            st.rerun()

    # Verification Logic on Game Submission
    if submit_game:
        elapsed_time = round(time.time() - st.session_state.start_time, 1)

        found_words = 0
        for word, coords in st.session_state.placed_positions.items():
            if all(coord in st.session_state.selected_cells for coord in coords):
                found_words += 1

        total_words = len(word_dict)

        if found_words == total_words:
            st.balloons()
            st.success(
                f"🎉 Perfect! All {total_words} words found in {elapsed_time}s!"
            )
            try:
                sheet = init_google_sheet()
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                sheet.append_row(
                    [
                        player_name,
                        st.session_state.selected_topic,
                        elapsed_time,
                        timestamp,
                    ]
                )
                st.info(
                    "Score successfully uploaded to Google Sheets Leaderboard!"
                )
            except Exception as e:
                st.error(f"Could not write score to database: {e}")
        else:
            st.warning(
                f"You found {found_words}/{total_words} words. Highlight all target word letters on the grid!"
            )

# --- LIVE LEADERBOARD DISPLAY ---
st.markdown("---")
st.subheader("🏆 Live Leaderboard")

try:
    # Fetch records directly from Google Sheets
    sheet = init_google_sheet()
    records = sheet.get_all_records()

    if records:
        df = pd.DataFrame(records)

        # 1. Convert Duration column to numerical values for sorting
        df["Duration (seconds)"] = pd.to_numeric(
            df["Duration (seconds)"], errors="coerce"
        )

        # 2. Sort entries by fastest completion time (ascending)
        df = df.sort_values(by="Duration (seconds)", ascending=True).reset_index(
            drop=True
        )

        # 3. Add custom Rank icons for top players
        def format_rank(index):
            if index == 0:
                return "🥇 1st"
            elif index == 1:
                return "🥈 2nd"
            elif index == 2:
                return "🥉 3rd"
            else:
                return f"{index + 1}th"

        df.insert(0, "Rank", [format_rank(i) for i in range(len(df))])

        # 4. Render clean table without raw index column
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No scores submitted yet.")

except Exception as e:
    st.caption("Leaderboard loading...")
