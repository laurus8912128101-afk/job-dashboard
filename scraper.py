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

# ====== 前回データ ======
old_links = set()
if os.path.exists(CSV_FILE):
    old_df = pd.read_csv(CSV_FILE)
    old_links = set(old_df["link"].tolist())

titles, companies, links, dates, keyword_list = [], [], [], [], []
messages = []

# ====== スクレイピング ======
for kw in KEYWORDS:
    url = BASE_URL + kw
    res = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(res.text, "html.parser")

    projects = soup.select("a[data-testid='project-card']")

    for p in projects:
        title = p.select_one("h1, h2, h3")
        if not title:
            continue

        title_text = title.text.strip()

        # 除外
        if any(ex in title_text for ex in EXCLUDE_KEYWORDS):
            continue

        company = p.select_one("div")
        link = "https://www.wantedly.com" + p.get("href")

        date_tag = p.select_one("time")
        date_text = date_tag.text.strip() if date_tag else "不明"

        if link in links:
            continue

        if link not in old_links:
            titles.append(title_text)
            companies.append(company.text.strip() if company else "")
            links.append(link)
            dates.append(date_text)
            keyword_list.append(kw)

            messages.append(f"🆕[{kw}]\n{title_text}\n{company.text.strip() if company else ''}\n{date_text}\n{link}")

        time.sleep(0.5)

# ====== 保存 ======
df = pd.DataFrame({
    "keyword": keyword_list,
    "title": titles,
    "company": companies,
    "date": dates,
    "link": links
})

df.to_csv(CSV_FILE, index=False, encoding="utf-8-sig")

print("scraping done")