import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="就活AI求人ダッシュボード", layout="wide")

st.title("📊 就活AI求人ダッシュボード")
st.write("Wantedlyの求人を自動収集・整理するツール")

DATA_FILE = "wantedly_jobs.csv"
FAV_FILE = "favorites.csv"

@st.cache_data
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    return pd.DataFrame(columns=["keyword","title","company","date","link"])

df = load_data()

def load_fav():
    if os.path.exists(FAV_FILE):
        return pd.read_csv(FAV_FILE)
    return pd.DataFrame(columns=df.columns)

def save_fav(fav_df):
    fav_df.to_csv(FAV_FILE, index=False, encoding="utf-8-sig")

favorites = load_fav()

# ===== フィルタ =====
st.sidebar.header("検索")

keyword = st.sidebar.text_input("キーワード")
exclude = st.sidebar.text_input("除外")
company = st.sidebar.text_input("会社名")

filtered = df.copy()

if keyword:
    filtered = filtered[filtered["title"].str.contains(keyword, na=False)]

if exclude:
    for ex in exclude.split(","):
        filtered = filtered[~filtered["title"].str.contains(ex.strip(), na=False)]

if company:
    filtered = filtered[filtered["company"].str.contains(company, na=False)]

st.write(f"件数: {len(filtered)}")
st.dataframe(filtered, use_container_width=True)

st.divider()

# ===== お気に入り =====
st.subheader("⭐ お気に入り")

selected = st.selectbox("選択", filtered["title"] if len(filtered) else [])

if st.button("追加"):
    row = filtered[filtered["title"] == selected]
    favorites = pd.concat([favorites, row]).drop_duplicates(subset=["link"])
    save_fav(favorites)
    st.success("追加しました")

favorites = load_fav()
st.dataframe(favorites, use_container_width=True)

# ===== リンク =====
st.subheader("🔗 リンク")
for _, row in filtered.head(10).iterrows():
    st.markdown(f"- [{row['title']}]({row['link']})")

# ===== DL =====
st.download_button(
    "CSVダウンロード",
    filtered.to_csv(index=False).encode("utf-8-sig"),
    "jobs.csv"
)