import random
import string
import time
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="CIE 9700 Biology Word Search", page_icon="🧬", layout="wide"
)

# Custom CSS for square wireframe grid buttons
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
    """Connects to BIOLOGY tab on Google Sheets."""
    creds_dict = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    client = gspread.authorize(creds)
    return client.open("CIE-Leaderscore-Board").worksheet("BIOLOGY")


TOPIC_DATA = {
    "Cell Structure & Organelles": {
        "NUCLEOLUS": "Dense region in nucleus where ribosomes assemble.",
        "RIBOSOME": "Site of protein synthesis in eukaryotic cells.",
        "THYLAKOID": "Membrane sac inside chloroplast holding chlorophyll.",
        "LYSOSOME": "Organelle containing hydrolytic digestive enzymes.",
        "PLASMODES": "Microscopic channel through plant cell walls.",
        "CENTRIOLE": "Organizes spindle fibers during cell division.",
        "TONOPLAST": "Membrane surrounding central vacuole in plants.",
        "CHROMATIN": "DNA wrapped around histone proteins in nucleus.",
        "CRISTAE": "Folds of inner mitochondrial membrane.",
        "GLYCOCALYX": "Carbohydrate coat on outer cell membrane surface.",
    },
    "Biological Molecules": {
        "GLYCOSIDIC": "Covalent bond joining carbohydrate monomers.",
        "AMYLOSE": "Unbranched helical polysaccharide component.",
        "AMYLOPECTIN": "Branched polysaccharide linked by 1-6 bonds.",
        "ESTERGOND": "Bond formed between glycerol and fatty acids.",
        "COLLAGEN": "Fibrous structural protein with triple helix.",
        "HEMOGLOBIN": "Globular protein transporting oxygen in blood.",
        "DISULFIDE": "Strong covalent bond stabilizing protein tertiary structure.",
        "HYDROPHILIC": "Water-attracting polar functional group.",
        "HYDROPHOBIC": "Water-repelling non-polar fatty acid tail.",
        "MONOMER": "Single repeating unit polymerizing into larger chains.",
    },
    "Enzymes & Inhibition": {
        "ACTIVE": "Site where substrate binds to enzyme molecule.",
        "ALLOSTERIC": "Secondary binding site for non-competitive inhibition.",
        "COMPETITIVE": "Inhibitor structural analogue competing for active site.",
        "DENATURE": "Loss of tertiary structure changing active site shape.",
        "INDUCED": "Fit hypothesis where enzyme adjusts shape upon binding.",
        "COFACTOR": "Non-protein helper required for enzyme activity.",
        "COENZYME": "Organic cofactor carrying chemical groups.",
        "CATALASE": "Enzyme breaking down toxic hydrogen peroxide.",
        "VMAX": "Maximum rate of reaction when enzyme is saturated.",
        "KM": "Substrate concentration at half maximum velocity.",
    },
    "Transport in Plants & Mammals": {
        "TRANSPIRATION": "Evaporation of water vapor from leaf stomata.",
        "APOPLAST": "Pathway moving water along plant cell walls.",
        "SYMPLAST": "Pathway moving water through cytoplasm via plasmodesmata.",
        "CASPARIAN": "Waxy strip in endodermis blocking apoplast path.",
        "XYLEM": "Lignified vessel transporting water and minerals.",
        "PHLOEM": "Vascular tissue transporting sucrose and amino acids.",
        "TRANSLOCATION": "Energy-requiring movement of assimilates in phloem.",
        "SYSTEMIC": "Circulation carrying oxygenated blood to body systems.",
        "CORONARY": "Artery supplying oxygenated blood to cardiac muscle.",
        "HEMOGLOBIN": "Conformational change increasing oxygen binding affinity.",
    },
    "Genetics & Protein Synthesis": {
        "TRANSCRIPTION": "Synthesis of mRNA strand from DNA template.",
        "TRANSLATION": "Polypeptide assembly at ribosome using mRNA.",
        "ANTICODON": "Triplet base sequence on tRNA matching mRNA codon.",
        "MUTATION": "Random change in base sequence of DNA molecule.",
        "SEMI": "Conservative DNA replication yielding one new strand.",
        "POLYMERASE": "Enzyme synthesizing complementary nucleotide chain.",
        "HELICASE": "Enzyme unwinding DNA double helix structure.",
        "EXON": "Coding segment of RNA preserved after splicing.",
        "INTRON": "Non-coding RNA segment removed during splicing.",
        "PROMOTER": "DNA sequence initiating RNA polymerase binding.",
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
                st.info("Score uploaded to Biology Leaderboard!")
            except Exception as e:
                st.error(f"Could not upload score: {e}")
        else:
            st.warning(f"You found {found_words}/{total_words} words.")
        st.rerun()

st.markdown("---")
st.subheader("🏆 Biology Live Leaderboard")
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
