import streamlit as st
import pandas as pd
import random
from datetime import datetime
from io import BytesIO
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# --- App Setup ---
st.set_page_config(page_title="Next Jackpot", layout="wide")
st.title("🎰 NEXT JACKPOT")

# --- User Access ---
user_type = st.sidebar.radio("Select Access Level:", ["🎟️ Lucky Pick", "🎲 High Roller"])
game_type = st.selectbox("Choose your game:", ["Powerball", "Mega Millions"])

# --- File IDs ---
powerball_file_id = '15damBhYpCYt523etFZfxH-zd7PZ9JL9p'
megamillions_file_id = '1ldIaZcKj8IjyHUaq2fWLA1_cM71nruyJ'

# --- Download File ---
@st.cache_data(show_spinner=False)
def download_file(file_id):
    try:
        url = f"https://drive.google.com/uc?id={file_id}&export=download"
        session = requests.Session()
        retries = Retry(total=3, backoff_factor=0.5, status_forcelist=[502, 503, 504])
        session.mount('https://', HTTPAdapter(max_retries=retries))
        response = session.get(url, timeout=10)
        response.raise_for_status()

        excel_data = BytesIO(response.content)
        df = pd.read_excel(excel_data, engine='openpyxl')
        df['Draw Date'] = pd.to_datetime(df['Draw Date'], errors='coerce')
        df = df.sort_values(by="Draw Date", ascending=False)
        df['White Balls'] = df['White Ball'].str.split(',').apply(lambda x: [int(i) for i in x if i.strip().isdigit()])
        return df
    except Exception as e:
        st.error(f"⚠️ Failed to load data from Google Drive: {e}")
        return None

def format_jackpot(jackpot_amount):
    try:
        jackpot_amount = float(jackpot_amount)
        return f"{jackpot_amount / 1000:.2f} Billion" if jackpot_amount >= 1000 else f"{jackpot_amount} Million"
    except:
        return jackpot_amount

def get_ball_ranges(game_type):
    if game_type == "Mega Millions":
        return 70, 24
    else:
        return 69, 26

def generate_standard_prediction(white_freq, extra_freq, top_white_count=25, top_extra_count=15):
    top_white = white_freq.head(top_white_count).index.tolist()
    top_extra = extra_freq.head(top_extra_count).index.tolist()
    return sorted(random.sample(top_white, 5)), random.choice(top_extra)

def generate_recent_based_prediction(df, white_col, extra_col, weeks_back, mode="hot"):
    cutoff_date = df['Draw Date'].max() - pd.Timedelta(weeks=weeks_back)
    recent_df = df[df['Draw Date'] >= cutoff_date]
    all_white_balls = sum(recent_df[white_col].tolist(), [])
    white_freq = pd.Series(all_white_balls).value_counts()
    extra_freq = recent_df[extra_col].value_counts()

    max_white, max_extra = get_ball_ranges(game_type)

    if mode == "hot":
        top_white = white_freq[white_freq.index <= max_white].nlargest(25).index.tolist()
        top_extra = extra_freq[extra_freq.index <= max_extra].nlargest(15).index.tolist()
    else:
        all_whites = set(range(1, max_white + 1))
        all_extras = set(range(1, max_extra + 1))
        cold_white = list(all_whites - set(white_freq.index))
        cold_extra = list(all_extras - set(extra_freq.index))

        if len(cold_white) < 5:
            cold_white += white_freq[white_freq.index <= max_white].nsmallest(30).index.tolist()
        if len(cold_extra) < 1:
            cold_extra += extra_freq[extra_freq.index <= max_extra].nsmallest(10).index.tolist()

        top_white = cold_white
        top_extra = cold_extra

    return sorted(random.sample(top_white, 5)), random.choice(top_extra)

# --- Main ---
file_id = powerball_file_id if game_type == "Powerball" else megamillions_file_id
extra_label = "Powerball" if game_type == "Powerball" else "Mega Ball"
extra_col = extra_label

with st.spinner("Loading game data..."):
    df = download_file(file_id)

if df is None:
    st.stop()

# Prepare frequency data
max_white, max_extra = get_ball_ranges(game_type)
white_freq = pd.Series(sum(df['White Balls'], [])).value_counts().sort_index()
white_freq = white_freq[white_freq.index <= max_white]
extra_freq = df[extra_col].value_counts().sort_index()
extra_freq = extra_freq[extra_freq.index <= max_extra]

# --- Prediction Output ---
st.subheader("Your Predictions (copy and paste into Excel)")

predictions = []
if user_type == "🎟️ Lucky Pick":
    if st.button("Generate Lucky Pick Predictions"):
        for _ in range(5):
            nums, extra = generate_standard_prediction(white_freq, extra_freq)
            line = f"{','.join(map(str, nums))}\t{extra}"
            predictions.append(line)
elif user_type == "🎲 High Roller":
    mode = st.radio("Choose Prediction Mode:", ["🎯 Standard Mode", "🔮 Smart Picker", "❄️ Cold Balls Only"])
    lines = st.slider("How many prediction lines?", 1, 10, 5)
    if mode == "🎯 Standard Mode":
        top_white_count = st.slider("Top White Balls", 5, max_white, 25)
        top_extra_count = st.slider(f"Top {extra_label}s", 1, max_extra, 15)
    else:
        weeks = st.slider("Look back over how many weeks?", 1, 12, 4)

    if st.button("Generate High Roller Predictions"):
        for _ in range(lines):
            if mode == "🎯 Standard Mode":
                nums, extra = generate_standard_prediction(white_freq, extra_freq, top_white_count, top_extra_count)
            elif mode == "🔮 Smart Picker":
                nums, extra = generate_recent_based_prediction(df, 'White Balls', extra_col, weeks, mode="hot")
            else:
                nums, extra = generate_recent_based_prediction(df, 'White Balls', extra_col, weeks, mode="cold")
            line = f"{','.join(map(str, nums))}\t{extra}"
            predictions.append(line)

# Show predictions in a copyable format
if predictions:
    st.text_area("Copy below:", "\n".join(predictions), height=200)

