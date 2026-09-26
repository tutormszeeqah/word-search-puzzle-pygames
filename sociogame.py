import random
import string
import time
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="CIE 9699 Sociology Word Search", page_icon="👥", layout="wide"
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
    """Connects to SOCIO tab on Google Sheets."""
    creds_dict = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    client = gspread.authorize(creds)
    return client.open("CIE-Leaderscore-Board").worksheet("SOCIO")


TOPIC_DATA = {
    "Socialisation & Identity": {
        "CULTURE": "Shared values, beliefs, and practices of society.",
        "NORMS": "Socially expected behaviors guiding conduct.",
        "VALUES": "Beliefs defining what is desirable or important.",
        "IDENTITY": "Individual sense of self shaped by society.",
        "GENDER": "Social and cultural expectations tied to sex.",
        "SUBCULTURE": "Group with distinct norms within wider culture.",
        "AGENCY": "Ability of individuals to act independently.",
        "ANOMIE": "State of normlessness described by Durkheim.",
        "STATUS": "Social standing or position within hierarchy.",
        "ROLE": "Behavior expected of person in specific status.",
    },
    "Research Methods": {
        "POSITIVISM": "Approach using objective quantitative methods.",
        "INTERPRET": "Sociology emphasizing subjective human meanings.",
        "VALIDITY": "Degree to which data reflects social reality.",
        "RELIABLE": "Consistency of research findings when repeated.",
        "ETHICS": "Moral principles governing research conduct.",
        "SAMPLE": "Subgroup chosen to represent target population.",
        "SURVEY": "Data collection tool using structured questions.",
        "ETHNO": "Qualitative study observing cultural settings.",
        "BIAS": "Systematic distortion affecting research objectivity.",
        "TRIANGULATE": "Using multiple methods to cross-check data.",
    },
    "The Family": {
        "NUCLEAR": "Family unit of parents and dependent children.",
        "EXTENDED": "Family network stretching across generations.",
        "PATRIARCHY": "System of social structure dominated by men.",
        "FUNCTIONAL": "Perspective viewing family as vital organ.",
        "MARXISM": "View of family serving capitalist economic goals.",
        "FEMINISM": "Perspective critiquing gender inequality in family.",
        "DIVORCE": "Legal termination of marital union.",
        "FERTILITY": "Birth rate patterns shaping family structures.",
        "DOMESTIC": "Division of labor and chores inside home.",
        "KINSHIP": "Social relationships based on blood or marriage.",
    },
    "Education": {
        "MERITOCRACY": "System where success is based on talent and effort.",
        "HABITUS": "Cultural frameworks described by Bourdieu.",
        "LABELING": "Process where teacher expectations shape performance.",
        "CURRICULUM": "Knowledge and subjects taught within schools.",
        "HIDDEN": "Unspoken norms taught implicitly through schooling.",
        "CAPITAL": "Cultural assets conferring educational advantage.",
        "STREAMING": "Sorting students into classes by general ability.",
        "EQUALITY": "Fair access to educational opportunities for all.",
        "DISADVANTAGE": "Social barriers hindering academic achievement.",
        "MOBILITY": "Movement between different social classes.",
    },
    "Media & Society": {
        "HEGEMONY": "Dominance of ruling class ideas in media.",
        "GATEKEEPER": "Media editor deciding which news is published.",
        "AGENDA": "Media power shaping public debate topics.",
        "STEREOTYPE": "Simplified generalized view of social groups.",
        "HYPODERMIC": "Model assuming direct immediate media impact.",
        "PLURALISM": "View that media reflects diverse audience demand.",
        "DIGITAL": "Modern online communications infrastructure.",
        "CONSUMPTION": "Audience engagement with media products.",
        "REPRESENT": "Portrayal of social categories in media content.",
        "CENSORSHIP": "State restriction of published media content.",
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
                st.info("Score uploaded to Sociology Leaderboard!")
            except Exception as e:
                st.error(f"Could not upload score: {e}")
        else:
            st.warning(f"You found {found_words}/{total_words} words.")
        st.rerun()

st.markdown("---")
st.subheader("🏆 Sociology Live Leaderboard")
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
