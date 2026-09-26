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
        font-size: 18px !important;
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


# Comprehensive CIE 9618 Vocabulary & Clues Database (20 Chapters, 10 clues each)
TOPIC_DATA = {
    "Chapter 1: Data Representation": {
        "BIT": "Smallest unit of binary storage.",
        "BYTE": "A sequence of 8 bits.",
        "NIBBLE": "Half a byte, consisting of 4 bits.",
        "BINARY": "Base-2 numeric representation scheme.",
        "HEX": "Base-16 system useful for short hex codes.",
        "ASCII": "7-bit standardized character encoding.",
        "UNICODE": "Universal text set encoding standard.",
        "BITMAP": "Raster image made of grid pixels.",
        "VECTOR": "Image drawn using geometric equations.",
        "SOUND": "Analog audio digitised via sampling.",
    },
    "Chapter 2: Communication & Networking": {
        "ROUTER": "Routes packets between separate networks.",
        "SWITCH": "Connects devices inside a local network.",
        "SERVER": "Provides central network resources.",
        "CLIENT": "Device requesting services from server.",
        "MODEM": "Modulates digital data to analog.",
        "PACKET": "Unit of data sent across network.",
        "BANDWIDTH": "Max data capacity of a link.",
        "TOPOLOGY": "Physical layout structure of network.",
        "ETHERNET": "Standard physical cabling connection.",
        "GATEWAY": "Connects networks with different protocols.",
    },
    "Chapter 3: Hardware & Logic Gates": {
        "RAM": "Volatile temporary computer main memory.",
        "ROM": "Non-volatile memory holding boot code.",
        "SENSOR": "Input hardware detecting external events.",
        "ACTUATOR": "Output device causing mechanical movement.",
        "AND": "Logic gate requiring all inputs true.",
        "OR": "Logic gate outputting true if any input true.",
        "NOT": "Logic gate inverting the input state.",
        "NAND": "Logic gate outputting false when all true.",
        "NOR": "Logic gate returning true only if all false.",
        "XOR": "Logic gate requiring exclusive single input.",
    },
    "Chapter 4: Processor Fundamentals": {
        "ALU": "Performs CPU math and logic checks.",
        "CU": "Coordinates instruction timing and signals.",
        "FETCH": "Retrieves next instruction from memory.",
        "DECODE": "Translates raw opcode into control steps.",
        "EXECUTE": "Carries out processed instruction steps.",
        "REGISTER": "Ultra-fast temporary CPU storage cell.",
        "ACC": "Accumulator storing current ALU result.",
        "MAR": "Register holding memory read address.",
        "MDR": "Register holding fetched memory data.",
        "CLOCK": "Generates sync pulses for CPU steps.",
    },
    "Chapter 5: System Software & Translators": {
        "COMPILER": "Translates high-level code all at once.",
        "INTERPRETER": "Translates high-level code line-by-line.",
        "ASSEMBLER": "Translates assembly code into machine code.",
        "UTILITY": "System software for maintenance tasks.",
        "DRIVER": "Software translating OS calls for hardware.",
        "SPOOLING": "Queues output jobs to disk temporarily.",
        "SCHEDULE": "OS process allocation strategy.",
        "KERNEL": "Core internal component of an OS.",
        "INTERRUPT": "Signal pausing CPU execution for priority.",
        "VIRTUAL": "Simulated memory space using disk area.",
    },
    "Chapter 6: Security & Data Integrity": {
        "VIRUS": "Malicious code replicating to other files.",
        "PHISHING": "Deceptive attempt to steal user credentials.",
        "SPYWARE": "Software secretly tracking user activity.",
        "FIREWALL": "Filters incoming and outgoing network traffic.",
        "PARITY": "Error check bit appended to binary byte.",
        "CHECKSUM": "Hash value used to verify data transfer.",
        "VALIDATION": "Automated check for acceptable input format.",
        "VERIFICATION": "Check ensuring data matches original source.",
        "MALWARE": "Umbrella term for harmful software.",
        "BACKUP": "Duplicate copy created for recovery.",
    },
    "Chapter 7: Ethics & Ownership": {
        "COPYRIGHT": "Legal protection for created content.",
        "PLAGIARISM": "Claiming another's work as your own.",
        "SHAREWARE": "Trial software free for limited time.",
        "FREEWARE": "Software distributed at zero monetary cost.",
        "OPENSOURCE": "Software with publicly editable code.",
        "PRIVACY": "Right to keep personal data secret.",
        "CREATIVE": "Licensing framework for sharing media.",
        "PATENT": "Exclusive right granted for inventions.",
        "MORAL": "Individual beliefs on right versus wrong.",
        "ETHICS": "Systematic rules governing conduct.",
    },
    "Chapter 8: Databases & SQL": {
        "TABLE": "Structure storing database records.",
        "RECORD": "A single row of database attributes.",
        "FIELD": "A single column attribute in a row.",
        "PRIMARY": "Unique key identifying each record row.",
        "FOREIGN": "Key referencing primary key of another table.",
        "INDEX": "Structure speeding up database searches.",
        "QUERY": "Command requesting specific dataset items.",
        "SCHEMA": "Overall structural design of database.",
        "NORMALISE": "Process eliminating redundant data items.",
        "VIEW": "Virtual table generated from SQL query.",
    },
    "Chapter 9: Computational Thinking": {
        "ABSTRACTION": "Filtering out irrelevant detail elements.",
        "DECOMPOSE": "Breaking complex problems into sub-problems.",
        "ALGORITHM": "Step-by-step procedure to solve task.",
        "FLOWCHART": "Diagram displaying algorithmic process.",
        "PSEUDOCODE": "Language-independent structured algorithm code.",
        "TRACE": "Manual step execution verification method.",
        "INPUT": "Data entered into computational process.",
        "OUTPUT": "Result produced by computational process.",
        "SEQUENCE": "Ordering steps sequentially in order.",
        "SELECTION": "Decision branch choosing logical paths.",
    },
    "Chapter 10: Data Structures & ADTs": {
        "ARRAY": "Indexed list of same data type.",
        "STACK": "LIFO linear data structure collection.",
        "QUEUE": "FIFO linear data structure collection.",
        "LINKED": "Node structure connected via pointers.",
        "TREE": "Hierarchical structure with root node.",
        "GRAPH": "Vertices connected by directional edges.",
        "RECORD": "Composite data type grouping variables.",
        "POINTER": "Variable storing memory address index.",
        "HASH": "Function mapping keys to table slots.",
        "TUPLE": "Immutable ordered sequence structure.",
    },
    "Chapter 11: Programming Basics": {
        "VARIABLE": "Named storage container with modifiable value.",
        "CONSTANT": "Named value remaining fixed during runtime.",
        "INTEGER": "Whole number without fractional part.",
        "STRING": "Sequence string of text characters.",
        "BOOLEAN": "Data type taking True or False value.",
        "LOOP": "Control structure repeating block execution.",
        "FUNCTION": "Subroutine returning a value upon call.",
        "PROCEDURE": "Subroutine executing without value return.",
        "SCOPE": "Region where variable remains accessible.",
        "PARAMETER": "Input variable passed to subroutine.",
    },
    "Chapter 12: Software Development Life Cycle": {
        "ANALYSIS": "Gathering system requirements from user.",
        "DESIGN": "Creating system structure specifications.",
        "TESTING": "Evaluating software for bugs and errors.",
        "WATERFALL": "Sequential linear development model.",
        "AGILE": "Iterative flexible development approach.",
        "PROTOTYPE": "Early working model built for demonstration.",
        "ALPHA": "Internal testing phase by developers.",
        "BETA": "External testing phase by end users.",
        "UNIT": "Testing individual subroutines or modules.",
        "MAINTAIN": "Updating software after initial deployment.",
    },
    "Chapter 13: Advanced Data Representation": {
        "MANTISSA": "Part of float holding precision digits.",
        "EXPONENT": "Part of float defining scale power.",
        "OVERFLOW": "Error when calculated value is too large.",
        "UNDERFLOW": "Error when value is too small to record.",
        "TRUNCATE": "Dropping trailing digits without rounding.",
        "ROUNDING": "Approximating number to target digits.",
        "PRECISION": "Degree of accuracy in float storage.",
        "NORMALISED": "Float format maximizing bit precision.",
        "COMPLEMENT": "Method used to store negative binary values.",
        "REAL": "Data type representing numbers with decimals.",
    },
    "Chapter 14: Internet Protocols & Switching": {
        "PACKET": "Data block sent across IP networks.",
        "CIRCUIT": "Dedicated physical channel connection line.",
        "PROTOCOL": "Standard rules governing communication.",
        "TCPIP": "Core suite of internet network protocols.",
        "DNS": "Translates domain names to IP addresses.",
        "HTTP": "Protocol retrieving web page content.",
        "HTTPS": "Encrypted protocol transferring web pages.",
        "FTP": "Protocol transferring files between hosts.",
        "SMTP": "Protocol used for sending email messages.",
        "SOCKET": "IP address combined with port number.",
    },
    "Chapter 15: Boolean Algebra & Logic": {
        "DE MORGAN": "Theorem simplifying inverted logic expressions.",
        "KARNAUGH": "Map method simplifying Boolean expressions.",
        "IDENTITY": "Boolean rule where terms retain state.",
        "ABSORPTION": "Boolean law removing redundant variables.",
        "TAUTOLOGY": "Expression evaluating always to true.",
        "CIRCUIT": "Interconnected group of logic gates.",
        "FLIPFLOP": "Bistable circuit storing one bit state.",
        "ADDER": "Circuit performing binary addition math.",
        "HALFEDDER": "Adder circuit without carry-in input.",
        "FULLADDER": "Adder circuit handling carry-in bit.",
    },
    "Chapter 16: System Software & VMs": {
        "PAGING": "Memory split into fixed-size blocks.",
        "SEGMENT": "Memory split into logical variable blocks.",
        "VIRTUAL": "Software emulation of hardware system.",
        "HYPERVISOR": "Software managing multiple virtual machines.",
        "THREAD": "Smallest unit of execution in process.",
        "MUTEX": "Lock preventing concurrent resource access.",
        "DEADLOCK": "State where processes block each other.",
        "BUFFER": "Temporary area balancing data transfer speed.",
        "TRAP": "Software interrupt caused by exception.",
        "DAEMON": "Background process running without UI.",
    },
    "Chapter 17: Security & Cryptography": {
        "ASYMMETRIC": "Encryption using public and private keys.",
        "SYMMETRIC": "Encryption using single shared key.",
        "DIGITAL": "Certificate verifying public key owner.",
        "SIGNATURE": "Cryptographic proof verifying authenticity.",
        "HASH": "One-way function producing fixed output.",
        "SALT": "Random data added to hash before storage.",
        "CIPHER": "Algorithm used to encrypt plain text.",
        "PLAINTEXT": "Unencrypted original readable message text.",
        "CIPHERTEXT": "Encrypted unreadable converted message text.",
        "TLS": "Protocol providing secure web communication.",
    },
    "Chapter 18: Artificial Intelligence": {
        "AGENT": "Entity perceiving environment and taking action.",
        "HEURISTIC": "Rule of thumb guiding problem solution.",
        "GRAPH": "Search space of state node connections.",
        "DIJKSTRA": "Algorithm finding shortest path distance.",
        "ASTAR": "Best-first path search using heuristics.",
        "TRAINING": "Process teaching model on data set.",
        "SUPERVISED": "Learning model using labeled data sets.",
        "NEURAL": "Model layered on artificial interconnected neurons.",
        "WEIGHT": "Adjustable coefficient value inside neuron.",
        "BIAS": "Constant added to neural activation input.",
    },
    "Chapter 19: Computational Thinking & Recursion": {
        "RECURSION": "Function calling itself within definition.",
        "BASECASE": "Condition stopping recursive function calls.",
        "UNWIND": "Return phase of active stack calls.",
        "STACK": "Memory region storing active call frames.",
        "BINARY": "Search algorithm halving search space.",
        "BUBBLE": "Sorting algorithm swapping adjacent items.",
        "QUICKSORT": "Divide-and-conquer sorting algorithm using pivot.",
        "MERGESORT": "Divide-and-conquer sorting splitting arrays.",
        "INSERTION": "Sorting algorithm placing items in sequence.",
        "BIGOH": "Notation describing algorithmic complexity.",
    },
    "Chapter 20: Advanced Programming Paradigms": {
        "OBJECT": "Instance of class encapsulating data.",
        "CLASS": "Blueprint defining properties and methods.",
        "INHERIT": "Class deriving properties from parent.",
        "POLYMORPH": "Methods taking different behavior forms.",
        "ENCAPSULATE": "Hiding internal data state details.",
        "PARADIGM": "Style or approach of programming.",
        "DECLARATIVE": "Paradigm describing what program accomplishes.",
        "FUNCTIONAL": "Paradigm evaluating mathematical functions.",
        "METHOD": "Function defined inside class scope.",
        "OVERLOAD": "Multiple methods sharing identical name.",
    },
}


def generate_multidirectional_grid(words, grid_size=10):
    """Generates an N x N grid with words placed horizontally, vertically, or diagonally."""
    grid = [["" for _ in range(grid_size)] for _ in range(grid_size)]
    placed_positions = {}

    DIRECTIONS = [(0, 1), (1, 0), (1, 1), (-1, 1)]

    for word in words:
        placed = False
        attempts = 0

        while not placed and attempts < 150:
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


# Upgraded grid size to fit 10 words
GRID_SIZE = 10

# Initialize Session States
if "selected_topic" not in st.session_state:
    st.session_state.selected_topic = "Chapter 1: Data Representation"

if "start_time" not in st.session_state:
    st.session_state.start_time = time.time()

if "submitted" not in st.session_state:
    st.session_state.submitted = False

# --- TOP HEADER BAR: PLAYER NAME & TOPIC DROPDOWN ---
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

    # Display clues along with green/red answers if the game has been submitted
    for idx, (word, clue) in enumerate(word_dict.items(), start=1):
        if st.session_state.submitted:
            coords = st.session_state.placed_positions.get(word, [])
            is_correct = all(
                coord in st.session_state.selected_cells for coord in coords
            )
            color = "#2e7d32" if is_correct else "#d32f2f"  # Green or Red
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
            st.session_state.submitted = False
            st.rerun()

    with ctrl_col3:
        if st.button("CLEAR HIGHLIGHTS"):
            st.session_state.selected_cells = set()
            st.rerun()

    # Verification Logic on Game Submission
    if submit_game:
        st.session_state.submitted = True
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
                f"You found {found_words}/{total_words} words. Review the color-coded terms above!"
            )
        st.rerun()

# --- LIVE LEADERBOARD DISPLAY ---
st.markdown("---")
st.subheader("🏆 Live Leaderboard")

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
