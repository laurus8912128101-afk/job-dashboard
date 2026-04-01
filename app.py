import streamlit as st
import pandas as pd
import os

st.set_page_config(
    page_title="Job Finder AI",
    page_icon="🚀",
    layout="wide"
)

# ===== ヘッダー =====
st.title("🚀 Job Finder AI")
st.caption("自動収集された求人を効率的に検索・管理")

DATA_FILE = "wantedly_jobs.csv"

@st.cache_data
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    return pd.DataFrame(columns=["keyword","title","company","date","link"])

df = load_data()

# ===== KPI表示 =====
col1, col2, col3 = st.columns(3)

col1.metric("総求人数", len(df))
col2.metric("キーワード数", df["keyword"].nunique() if len(df) else 0)
col3.metric("最新更新", "今日")

st.divider()

# ===== フィルタUI =====
with st.sidebar:
    st.header("🔍 フィルター")

    keyword = st.text_input("キーワード検索")
    exclude = st.text_input("除外（カンマ区切り）")
    selected_kw = st.multiselect("カテゴリ", df["keyword"].unique())

filtered = df.copy()

if keyword:
    filtered = filtered[filtered["title"].str.contains(keyword, na=False)]

if exclude:
    for ex in exclude.split(","):
        filtered = filtered[~filtered["title"].str.contains(ex.strip(), na=False)]

if selected_kw:
    filtered = filtered[filtered["keyword"].isin(selected_kw)]

# ===== テーブル =====
st.subheader(f"📄 求人一覧（{len(filtered)}件）")
st.dataframe(filtered, use_container_width=True)

st.divider()

# ===== カード表示（SaaSっぽい）=====
st.subheader("✨ ピックアップ")

for _, row in filtered.head(5).iterrows():
    with st.container():
        st.markdown(f"### {row['title']}")
        st.write(f"🏢 {row['company']} | 🏷 {row['keyword']}")
        st.markdown(f"[詳細を見る]({row['link']})")
        st.divider()

# ===== ダウンロード =====
st.download_button(
    "📥 CSVダウンロード",
    filtered.to_csv(index=False).encode("utf-8-sig"),
    "jobs.csv"
)
