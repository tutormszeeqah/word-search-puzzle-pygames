import random
import string
import time
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import streamlit as st

# Configure Streamlit page for Geography
st.set_page_config(
    page_title="CIE 9696 Geography Word Search", page_icon="🌍", layout="wide"
)

# Apply CSS for square wireframe grid cells and highlight colors
st.markdown(
    """
<style>
    div[data-testid="stHorizontalBlock"] {
        gap: 0px !important;
    }
    
    div.stButton > button {
        width: 100% !important;
        aspect-ratio: 1 / 1 !important;
        height: auto !important;
        font-size: 18px !important;
        font-weight: 900 !important;
        border-radius: 0px !important;
        border: 1.5px solid #000000 !important;
        color: #000000 !important;
        background-color: #ffffff !important;
        padding: 0px !important;
        margin: 0px !important;
    }

    div.stButton > button[kind="primary"] {
        background-color: #ffeb3b !important;
        color: #000000 !important;
        border: 2px solid #000000 !important;
    }

    div.stButton > button:hover {
        background-color: #e0e0e0 !important;
        border-color: #000000 !important;
    }
</style>
""",
    unsafe_allow_html=True,
)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


@st.cache_resource
def init_google_sheet():
    """Establishes connection to Google Sheets for GEOG tab."""
    creds_dict = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    client = gspread.authorize(creds)
    return client.open("CIE-Leaderscore-Board").worksheet("GEOG")


# CIE 9696 Geography Syllabus Dataset
TOPIC_DATA = {
    "Core Physical: Hydrology & Fluvial": {
        "HYDROGRAPH": "Graph showing river discharge over time.",
        "MEANDER": "Winding curve or bend in a river course.",
        "DELTA": "Landform created by deposition at a river mouth.",
        "OXBOW": "U-shaped lake formed when a meander is cut off.",
        "ABRASION": "Erosion caused by debris scraping river beds.",
        "INFILTRATION": "Water entering the soil surface from above.",
        "PERCOLATION": "Downward movement of water through soil layer.",
        "LE VEE": "Natural embankment formed along river banks.",
        "DISCHARGE": "Volume of water flowing through a channel.",
        "WATERSHED": "Boundary separating adjacent drainage basins.",
    },
    "Core Physical: Atmosphere & Weather": {
        "ALBEDO": "Fraction of solar radiation reflected by surface.",
        "INSOLATION": "Incoming solar radiation received by Earth.",
        "CONDENSATION": "Phase change from water vapor into liquid.",
        "CORIOLIS": "Deflection of winds due to Earth rotation.",
        "RADIATION": "Transfer of heat energy via electromagnetic waves.",
        "CONVECTION": "Vertical movement of air caused by heating.",
        "LATENT": "Heat energy absorbed or released during phase change.",
        "ISOBAR": "Line connecting points of equal atmospheric pressure.",
        "HUMIDITY": "Amount of water vapor present in atmosphere.",
        "MIST": "Suspended liquid droplets reducing visibility slightly.",
    },
    "Core Physical: Rocks & Weathering": {
        "FREEZE": "Thaw weathering physical breakdown process.",
        "HALOCLASTY": "Salt crystallization weathering process.",
        "MASS": "Wasting movement of soil down slopes by gravity.",
        "SLUMP": "Rotational slip movement of rock along curved plane.",
        "LITHOLOGY": "Physical characteristics of rock types.",
        "JOINT": "Fracture in rock without relative displacement.",
        "CARBONATION": "Chemical weathering of limestone by carbonic acid.",
        "SCARP": "Steep slope or cliff formed by faulting or erosion.",
        "TALUS": "Accumulation of loose rock debris at cliff base.",
        "TECTONICS": "Large-scale crustal processes and movement.",
    },
    "Core Human: Population": {
        "MORTALITY": "Death rate measurement within a population.",
        "FERTILITY": "Average number of children born per woman.",
        "MALTHUS": "Theorist proposing population grows exponentially.",
        "BOSERUP": "Theorist claiming innovation expands food supply.",
        "CENSUS": "Official periodic count of a national population.",
        "DEPENDENCY": "Ratio of non-working age to working population.",
        "DEMOGRAPHIC": "Study of statistics illustrating human population.",
        "TRANSITION": "Model tracking birth/death rate changes.",
        "OPTIMUM": "Ideal population size matching resource capacity.",
        "LONGEVITY": "Average lifespan duration within a population.",
    },
    "Core Human: Migration": {
        "REMITTANCE": "Money sent home by migrant workers abroad.",
        "REFUGEE": "Person forced to flee country due to persecution.",
        "ASYLUM": "Protection granted by nation to political refugees.",
        "INTERNAL": "Migration occurring within national boundaries.",
        "STEP": "Migration occurring in stages up urban hierarchy.",
        "VOLUNTARY": "Migration chosen freely by individual choice.",
        "PUSH": "Negative factor compelling people to leave an area.",
        "PULL": "Positive factor attracting migrants to a region.",
        "BARRIER": "Obstacle hindering movement between places.",
        "DIASPORA": "Scattered population originating from single locale.",
    },
    "Core Human: Settlement Dynamics": {
        "URBAN": "Densely populated built-up city area.",
        "RURAL": "Countryside region outside major urban centers.",
        "GENTRIFY": "Renovating urban area to suit middle class.",
        "SPRAWL": "Uncontrolled expansion of urban boundaries.",
        "CONURBATION": "Continuous urban region formed by merging towns.",
        "HIERARCHY": "Ordering settlements by population size/services.",
        "SHANTY": "Informal settlement built from scrap material.",
        "CBD": "Central business district holding commercial hub.",
        "SUBURB": "Residential district located on city outskirts.",
        "BLIGHT": "Decay and deterioration of urban properties.",
    },
}


def generate_multidirectional_grid(words, grid_size=10):
    """Generates grid with longest words placed first."""
    grid = [["" for _ in range(grid_size)] for _ in range(grid_size)]
    placed_positions = {}
    DIRECTIONS = [(0, 1), (1, 0), (1, 1), (-1, 1)]

    sorted_words = sorted(words, key=len, reverse=True)

    for word in sorted_words:
        placed = False
        attempts = 0
        while not placed and attempts < 200:
            attempts += 1
            dr, dc = random.choice(DIRECTIONS)
            start_r = random.randint(0, grid_size - 1)
            start_c = random.randint(0, grid_size - 1)
            end_r = start_r + dr * (len(word) - 1)
            end_c = start_c + dc * (len(word) - 1)

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

    for r in range(grid_size):
        for c in range(grid_size):
            if grid[r][c] == "":
                grid[r][c] = random.choice(string.ascii_uppercase)

    return grid, placed_positions


def check_word_found(word, grid, selected_cells):
    """Flexible check confirming if selected cells spell word."""
    if not selected_cells:
        return False
    selected_letters = "".join(grid[r][c] for r, c in selected_cells)
    return word in selected_letters or word[::-1] in selected_letters


GRID_SIZE = 10

if "selected_topic" not in st.session_state:
    st.session_state.selected_topic = list(TOPIC_DATA.keys())[0]

if "start_time" not in st.session_state:
    st.session_state.start_time = time.time()

if "submitted" not in st.session_state:
    st.session_state.submitted = False

top_col1, top_col2 = st.columns([1, 3])

with top_col1:
    player_name = st.text_input(
        "TYPE NAME", value="Student 1", key="player_name_input"
    )

with top_col2:
    new_topic = st.selectbox(
        "Chapter Choice",
        list(TOPIC_DATA.keys()),
        index=list(TOPIC_DATA.keys()).index(st.session_state.selected_topic),
        key="topic_select",
    )

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
        st.session_state.submitted = False
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

col_grid, col_clues = st.columns([1, 1])

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

with col_clues:
    st.subheader("Clues & Word Submission")

    for idx, (word, clue) in enumerate(word_dict.items(), start=1):
        if st.session_state.submitted:
            coords = st.session_state.placed_positions.get(word, [])
            is_correct = all(
                coord in st.session_state.selected_cells for coord in coords
            ) or check_word_found(word, st.session_state.grid, st.session_state.selected_cells)

            color = "#2e7d32" if is_correct else "#d32f2f"
            symbol = "✓" if is_correct else "✗"

            st.markdown(
                f"**{idx}. {clue}** "
                f"<span style='color:{color}; font-weight:bold; margin-left:10px;'>"
                f"→ {word} [{symbol}]</span>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(f"**{idx}. {clue}**")

    st.markdown("---")
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
            st.session_state.submitted = False
            st.rerun()

    with ctrl_col3:
        if st.button("CLEAR HIGHLIGHTS"):
            st.session_state.selected_cells = set()
            st.rerun()

    if submit_game:
        st.session_state.submitted = True
        elapsed_time = round(time.time() - st.session_state.start_time, 1)

        found_words = 0
        for word, coords in st.session_state.placed_positions.items():
            is_correct = all(
                coord in st.session_state.selected_cells for coord in coords
            ) or check_word_found(word, st.session_state.grid, st.session_state.selected_cells)

            if is_correct:
                found_words += 1

        total_words = len(word_dict)

        if found_words == total_words:
            st.balloons()
            st.success(f"🎉 Perfect! Found all {total_words} words in {elapsed_time}s!")
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
                st.info("Score uploaded to Geography Leaderboard!")
            except Exception as e:
                st.error(f"Could not upload score: {e}")
        else:
            st.warning(f"You found {found_words}/{total_words} words.")
        st.rerun()

st.markdown("---")
st.subheader("🏆 Geography Live Leaderboard")

try:
    sheet = init_google_sheet()
    records = sheet.get_all_records()
    if records:
        df = pd.DataFrame(records)
        df["Duration (seconds)"] = pd.to_numeric(
            df["Duration (seconds)"], errors="coerce"
        )
        df = df.sort_values(by="Duration (seconds)", ascending=True).reset_index(
            drop=True
        )

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
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No scores submitted yet.")
except Exception as e:
    st.caption("Leaderboard loading...")
