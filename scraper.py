import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import time

KEYWORDS = ["エンジニア", "AI", "Web", "インターン"]
EXCLUDE_KEYWORDS = ["営業", "セールス"]

BASE_URL = "https://www.wantedly.com/projects?keywords="
CSV_FILE = "wantedly_jobs.csv"

HEADERS = {"User-Agent": "Mozilla/5.0"}

titles, companies, links, dates, keyword_list = [], [], [], [], []

# ====== スクレイピング ======
for kw in KEYWORDS:
    url = BASE_URL + kw
    print(f"取得中: {url}")

    res = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(res.text, "html.parser")

    # セレクタを広めに（安定）
    projects = soup.find_all("a", href=True)

    print(f"取得リンク数: {len(projects)}")

    for p in projects:
        link = p.get("href")

        # Wantedlyの求人リンクだけ抽出
        if not link.startswith("/projects/"):
            continue

        title_text = p.text.strip()

        if not title_text:
            continue

        # 除外
        if any(ex in title_text for ex in EXCLUDE_KEYWORDS):
            continue

        full_link = "https://www.wantedly.com" + link

        # 重複防止
        if full_link in links:
            continue

        titles.append(title_text)
        companies.append("不明")
        links.append(full_link)
        dates.append("不明")
        keyword_list.append(kw)

        # 取りすぎ防止
        if len(titles) > 50:
            break

    time.sleep(1)

# ====== データなかった時の保険 ======
if len(titles) == 0:
    print("⚠ データ0件 → ダミー追加")
    titles.append("サンプル求人（表示確認用）")
    companies.append("テスト株式会社")
    links.append("https://example.com")
    dates.append("今日")
    keyword_list.append("テスト")

# ====== 保存 ======
df = pd.DataFrame({
    "keyword": keyword_list,
    "title": titles,
    "company": companies,
    "date": dates,
    "link": links
})

df.to_csv(CSV_FILE, index=False, encoding="utf-8-sig")

print(f"保存完了: {len(df)}件")
