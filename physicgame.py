import random
import string
import time
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="CIE 9702 Physics Word Search", page_icon="⚡", layout="wide"
)

st.markdown(
    """
<style>
    div[data-testid="stHorizontalBlock"] { gap: 0px !important; }
    div.stButton > button {
        width: 100% !important; aspect-ratio: 1 / 1 !important; height: auto !important;
        font-size: 18px !important; font-weight: 900 !important; border-radius: 0px !important;
        border: 1.5px solid #000000 !important; color: #000000 !important; background-color: #ffffff !important;
        padding: 0px !important; margin: 0px !important;
    }
    div.stButton > button[kind="primary"] {
        background-color: #ffeb3b !important; color: #000000 !important; border: 2px solid #000000 !important;
    }
    div.stButton > button:hover { background-color: #e0e0e0 !important; border-color: #000000 !important; }
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
    """Connects to PHYSICS tab on Google Sheets."""
    creds_dict = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    client = gspread.authorize(creds)
    return client.open("CIE-Leaderscore-Board").worksheet("PHYSICS")


TOPIC_DATA = {
    "Kinematics & Dynamics": {
        "VELOCITY": "Rate of change of displacement with time.",
        "ACCEL": "Rate of change of velocity over time interval.",
        "MOMENTUM": "Product of mass and velocity of a body.",
        "IMPULSE": "Product of force and time duration applied.",
        "INERTIA": "Resistance of object to changes in motion.",
        "FRICTION": "Force opposing relative motion between surfaces.",
        "PARABOLA": "Trajectory shape of projectile under gravity.",
        "TERMINAL": "Constant velocity achieved when drag equals weight.",
        "ELASTIC": "Collision conserving total kinetic energy.",
        "TENSION": "Pulling force transmitted along string or cable.",
    },
    "Work, Energy & Power": {
        "JOULE": "SI unit of work and energy transfer.",
        "WATT": "SI unit of power representing joules per second.",
        "KINETIC": "Energy possessed by body due to motion.",
        "POTENTIAL": "Stored energy due to position or state.",
        "WORKDONE": "Product of force and distance moved in force direction.",
        "EFFICIENCY": "Ratio of useful output energy to total input.",
        "CONSERVE": "Principle stating energy cannot be created or destroyed.",
        "GRAVITY": "Field force attracting mass toward center of Earth.",
        "DISSIPATE": "Transformation of useful energy into wasted heat.",
        "POWER": "Rate at which work is done per unit time.",
    },
    "Waves & Superposition": {
        "AMPLITUDE": "Maximum displacement from equilibrium position.",
        "FREQUENCY": "Number of complete wave oscillations per second.",
        "WAVELENGTH": "Distance between two consecutive identical crests.",
        "DIFFRACT": "Spreading of waves passing through narrow gap.",
        "REFRACT": "Bending of wave direction at boundary change.",
        "NODE": "Point of zero amplitude on standing wave pattern.",
        "ANTINODE": "Point of maximum amplitude on standing wave.",
        "COHERENT": "Waves having constant phase difference and frequency.",
        "POLARISED": "Wave oscillating in a single transverse plane.",
        "INTENSITY": "Wave power transmitted per unit surface area.",
    },
    "Electricity & Circuits": {
        "CURRENT": "Rate of flow of electric charge carriers.",
        "VOLTAGE": "Potential difference driving electrical current.",
        "RESISTOR": "Component designed to restrict current flow.",
        "POTENTIAL": "Energy converted per unit charge passing component.",
        "INTERNAL": "Resistance within electrical voltage source.",
        "KIRCHHOFF": "Law governing charge conservation at circuit junction.",
        "OHMIC": "Conductor obeying linear voltage-current ratio.",
        "DIODE": "Component allowing unidirectional current flow.",
        "THERMISTOR": "Resistor whose resistance drops as temperature rises.",
        "RHEOSTAT": "Variable resistor controlling circuit current.",
    },
    "Particle & Nuclear Physics": {
        "HADRON": "Subatomic particle made of quarks.",
        "LEPTON": "Fundamental particle like electron or neutrino.",
        "NEUTRINO": "Uncharged fundamental particle emitted in beta decay.",
        "POSITRON": "Antiparticle counterpart of electron with positive charge.",
        "ISOTOPE": "Atoms with same proton number but different neutrons.",
        "FISSION": "Splitting of heavy nucleus into lighter nuclei.",
        "FUSION": "Combining light nuclei into heavier nucleus.",
        "ISOTOPE": "Unstable nucleus releasing ionizing radiation.",
        "HALF LIFE": "Time taken for active nuclei to decay by half.",
        "ALPHA": "Helium nucleus consisting of two protons and two neutrons.",
    },
}


def generate_multidirectional_grid(words, grid_size=10):
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
            ) or check_word_found(
                word, st.session_state.grid, st.session_state.selected_cells
            )
            color = "#2e7d32" if is_correct else "#d32f2f"
            symbol = "✓" if is_correct else "✗"
            st.markdown(
                f"**{idx}. {clue}** <span style='color:{color}; font-weight:bold; margin-left:10px;'>→ {word} [{symbol}]</span>",
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
        found_words = sum(
            1
            for word, coords in st.session_state.placed_positions.items()
            if all(
                coord in st.session_state.selected_cells for coord in coords
            )
            or check_word_found(
                word, st.session_state.grid, st.session_state.selected_cells
            )
        )
        total_words = len(word_dict)
        if found_words == total_words:
            st.balloons()
            st.success(
                f"🎉 Perfect! Found all {total_words} words in {elapsed_time}s!"
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
                st.info("Score uploaded to Physics Leaderboard!")
            except Exception as e:
                st.error(f"Could not upload score: {e}")
        else:
            st.warning(f"You found {found_words}/{total_words} words.")
        st.rerun()

st.markdown("---")
st.subheader("🏆 Physics Live Leaderboard")
try:
    sheet = init_google_sheet()
    records = sheet.get_all_records()
    if records:
        df = pd.DataFrame(records)
        df["Duration (seconds)"] = pd.to_numeric(
            df["Duration (seconds)"], errors="coerce"
        )
        df = df.sort_values(
            by="Duration (seconds)", ascending=True
        ).reset_index(drop=True)

        def format_rank(index):
            return (
                "🥇 1st"
                if index == 0
                else "🥈 2nd"
                if index == 1
                else "🥉 3rd"
                if index == 2
                else f"{index + 1}th"
            )

        df.insert(0, "Rank", [format_rank(i) for i in range(len(df))])
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No scores submitted yet.")
except Exception as e:
    st.caption("Leaderboard loading...")
