import streamlit as st
import pandas as pd

CSV_URL = (
    "https://gist.githubusercontent.com/sshima1203/xxxxx/raw/prediction_latest.csv"
    f"?t={int(time.time() // 300)}"
)
# ==================================================
# Page config
# ==================================================
st.set_page_config(
    page_title="アルバトリオン同好会AI競馬予想",
    page_icon="icon.png",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ==================================================
# CSS
# ==================================================
st.markdown("""
<meta charset="UTF-8">
<meta name="google" content="notranslate">
<meta http-equiv="Content-Language" content="ja">

<style>
header[data-testid="stHeader"] { display: none; }
footer { display: none; }

div[data-testid="stAppViewContainer"] > .main,
div.block-container {
    padding-top: 0 !important;
}

html, body, [data-testid="stAppViewContainer"] {
    background: radial-gradient(circle at top, #0b1220 0%, #020617 65%);
    color: #ffffff;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

button {
    background: #0b1220 !important;
    color: #ffffff !important;
    border: 1px solid rgba(148,163,184,0.28) !important;
    box-shadow: none !important;
}

button:hover {
    background: #111827 !important;
}

.app-header {
    position: sticky;
    top: 0;
    z-index: 50;
    padding: 10px 12px 8px;
    background: rgba(2,6,23,0.94);
}

.header-title {
    font-size: 0.9rem;
    font-weight: 700;
    margin-bottom: 6px;
}

.breadcrumb {
    display: flex;
    gap: 6px;
    overflow-x: auto;
}
.breadcrumb::-webkit-scrollbar { display: none; }

.breadcrumb .stButton > button {
    background: rgba(56,189,248,0.14) !important;
    border: 1px solid rgba(56,189,248,0.45) !important;
    border-radius: 999px !important;
    padding: 4px 12px !important;
    font-size: 0.65rem !important;
    color: #ffffff !important;
}

.body { padding-top: 10px; }

.section-title {
    font-size: 1.05rem;
    font-weight: 700;
    margin: 0.6rem 0 0.4rem;
}

.race-row {
    display: flex;
    padding: 6px 0;
    border-bottom: 1px solid rgba(148,163,184,0.18);
}
.rank { width: 28px; font-weight: 700; }
.horse { font-size: 0.9rem; }

a {
    color: #38bdf8;
    font-weight: 600;
    text-decoration: none;
}
</style>
""", unsafe_allow_html=True)

# ==================================================
# CSV Load（最終・正解）
# ==================================================
def load_all():
    df = pd.read_csv(
        CSV_URL,
        encoding="utf-8-sig",  # BOM対策のみ残す
    )

    # 列名正規化（保険）
    df.columns = [
        c.replace("\ufeff", "")
         .strip()
         .upper()
        for c in df.columns
    ]
    return df

df = load_all()




# ==================================================
# 必須列チェック（ここで止める）
# ==================================================
REQUIRED_COLS = {
    "RACE_ID",
    "RACE_NAME",
    "HORSE_NAME",
    "HORSE_NUM",
    "FINISH_POSITION",
    "NETKEIBA_URL",
}

missing = REQUIRED_COLS - set(df.columns)
if missing:
    st.error(f"CSVの列が不足しています: {missing}")
    st.write("現在の列一覧:", df.columns.tolist())
    st.stop()

# ==================================================
# State
# ==================================================
for k in ["course", "kaisai", "day", "race"]:
    st.session_state.setdefault(k, None)

# ==================================================
# Helpers
# ==================================================
COURSE_MAP = {
    "01": "札幌", "02": "函館", "03": "福島", "04": "新潟",
    "05": "東京", "06": "中山", "07": "中京",
    "08": "京都", "09": "阪神", "10": "小倉",
}

def rank_mark(r):
    return {1:"◎", 2:"〇", 3:"▲", 4:"△", 5:"☆"}.get(r, "")

# ==================================================
# Data shaping
# ==================================================
df["RACE_ID"] = df["RACE_ID"].astype(str)
df["COURSE_CODE"] = df["RACE_ID"].str[4:6]
df["COURSE"] = df["COURSE_CODE"].map(COURSE_MAP)
df["KAISAI"] = df["RACE_ID"].str[6:8]
df["DAY"] = df["RACE_ID"].str[8:10]
df["RACE_NO"] = df["RACE_ID"].str[-2:].astype(int)

# ==================================================
# Header
# ==================================================
st.markdown('<div class="app-header">', unsafe_allow_html=True)
st.markdown('<div class="header-title">アルバトリオン同好会 AI競馬予想</div>', unsafe_allow_html=True)
st.markdown('<div class="breadcrumb">', unsafe_allow_html=True)

if st.button("Race"):
    st.session_state.update(course=None, kaisai=None, day=None, race=None)
    st.rerun()

if st.session_state.course:
    if st.button(st.session_state.course):
        st.session_state.update(kaisai=None, day=None, race=None)
        st.rerun()

if st.session_state.race:
    if st.button(f"{int(st.session_state.kaisai)}回{int(st.session_state.day)}日目"):
        st.session_state.race = None
        st.rerun()

st.markdown('</div></div>', unsafe_allow_html=True)

# ==================================================
# Body
# ==================================================
st.markdown('<div class="body">', unsafe_allow_html=True)

if st.session_state.course is None:
    st.markdown("<div class='section-title'>コース</div>", unsafe_allow_html=True)
    for c in sorted(df["COURSE"].dropna().unique()):
        if st.button(c):
            st.session_state.course = c
            st.rerun()

elif st.session_state.day is None:
    st.markdown("<div class='section-title'>開催日</div>", unsafe_allow_html=True)
    for _, r in (
        df[df["COURSE"] == st.session_state.course][["KAISAI", "DAY"]]
        .drop_duplicates()
        .iterrows()
    ):
        if st.button(f"{int(r.KAISAI)}回{int(r.DAY)}日目"):
            st.session_state.kaisai = r.KAISAI
            st.session_state.day = r.DAY
            st.rerun()

elif st.session_state.race is None:
    st.markdown("<div class='section-title'>レース</div>", unsafe_allow_html=True)
    rdf = df[
        (df["COURSE"] == st.session_state.course) &
        (df["KAISAI"] == st.session_state.kaisai) &
        (df["DAY"] == st.session_state.day)
    ][["RACE_ID", "RACE_NAME", "RACE_NO"]].drop_duplicates().sort_values("RACE_NO")

    for _, r in rdf.iterrows():
        if st.button(f"{r.RACE_NO}R  {r.RACE_NAME}"):
            st.session_state.race = r.RACE_ID
            st.rerun()

else:
    ddf = df[df["RACE_ID"] == st.session_state.race].sort_values("FINISH_POSITION")

    race_no = ddf.iloc[0]["RACE_NO"]
    race_name = ddf.iloc[0]["RACE_NAME"]
    netkeiba_url = ddf.iloc[0]["NETKEIBA_URL"]

    st.markdown(
        f"<div class='section-title'>{race_no}R　{race_name}</div>",
        unsafe_allow_html=True
    )

    st.markdown(f"[netkeiba]({netkeiba_url})")

    for _, r in ddf.iterrows():
        st.markdown(
            f"<div class='race-row'>"
            f"<div class='rank'>{rank_mark(r.FINISH_POSITION)}</div>"
            f"<div class='horse'>{r.HORSE_NUM} {r.HORSE_NAME}</div>"
            f"</div>",
            unsafe_allow_html=True
        )

st.markdown('</div>', unsafe_allow_html=True)
