import streamlit as st
import pandas as pd
import os

# ===== 基本設定 =====
st.set_page_config(
    page_title="Job Finder AI",
    page_icon="🚀",
    layout="wide"
)

DATA_FILE = "wantedly_jobs.csv"
FAV_FILE = "favorites.csv"

# ===== データ読み込み =====
@st.cache_data
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    return pd.DataFrame(columns=["keyword","title","company","date","link"])

def load_fav():
    if os.path.exists(FAV_FILE):
        return pd.read_csv(FAV_FILE)
    return pd.DataFrame(columns=["keyword","title","company","date","link"])

def save_fav(df):
    df.to_csv(FAV_FILE, index=False, encoding="utf-8-sig")

df = load_data()
favorites = load_fav()

# ===== ヘッダー =====
st.title("🚀 Job Finder AI")
st.caption("求人収集 × 自動化 × 通知")

# ===== KPI =====
col1, col2, col3 = st.columns(3)

col1.metric("求人数", len(df))
col2.metric("カテゴリ数", df["keyword"].nunique() if len(df) else 0)
col3.metric("お気に入り", len(favorites))

st.divider()

# ===== サイドバー =====
with st.sidebar:
    st.header("🔍 フィルター")

    keyword = st.text_input("キーワード検索")
    exclude = st.text_input("除外（カンマ区切り）")
    company = st.text_input("会社名")
    selected_kw = st.multiselect("カテゴリ", df["keyword"].unique())

# ===== フィルタ処理 =====
filtered = df.copy()

if keyword:
    filtered = filtered[filtered["title"].str.contains(keyword, na=False)]

if exclude:
    for ex in exclude.split(","):
        filtered = filtered[~filtered["title"].str.contains(ex.strip(), na=False)]

if company:
    filtered = filtered[filtered["company"].str.contains(company, na=False)]

if selected_kw:
    filtered = filtered[filtered["keyword"].isin(selected_kw)]

# ===== 件数 =====
st.subheader(f"📄 求人一覧（{len(filtered)}件）")
st.dataframe(filtered, use_container_width=True)

st.divider()

# ===== カード表示 =====
st.subheader("✨ ピックアップ")

for _, row in filtered.head(5).iterrows():
    with st.container():
        st.markdown(f"### {row['title']}")
        st.write(f"🏢 {row['company']} | 🏷 {row['keyword']}")
        st.markdown(f"[🔗 詳細を見る]({row['link']})")
        st.divider()

# ===== お気に入り追加 =====
st.subheader("⭐ お気に入り追加")

if len(filtered) > 0:
    selected = st.selectbox("求人を選択", filtered["title"])

    if st.button("追加"):
        row = filtered[filtered["title"] == selected]
        favorites = pd.concat([favorites, row]).drop_duplicates(subset=["link"])
        save_fav(favorites)
        st.success("追加しました")

# ===== お気に入り表示 =====
st.subheader("⭐ お気に入り一覧")
favorites = load_fav()
st.dataframe(favorites, use_container_width=True)

st.divider()

# ===== ダウンロード =====
st.download_button(
    "📥 CSVダウンロード",
    filtered.to_csv(index=False).encode("utf-8-sig"),
    "jobs.csv"
)
