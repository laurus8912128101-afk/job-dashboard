from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import pandas as pd
import time
import os
import requests

# ===== 設定 =====
KEYWORDS = ["エンジニア", "AI", "Web", "インターン"]
EXCLUDE_KEYWORDS = ["営業", "セールス"]
CSV_FILE = "wantedly_jobs.csv"

LINE_TOKEN = "ここにLINEトークン"

# ===== LINE通知 =====
def send_line(message):
    url = "https://notify-api.line.me/api/notify"
    headers = {"Authorization": f"Bearer {LINE_TOKEN}"}
    data = {"message": message}
    requests.post(url, headers=headers, data=data)

# ===== 既存データ取得 =====
old_links = set()
if os.path.exists(CSV_FILE):
    old_df = pd.read_csv(CSV_FILE)
    old_links = set(old_df["link"].tolist())

# ===== Selenium設定 =====
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=options)

titles = []
companies = []
links = []
dates = []
keyword_list = []

messages = []

# ===== スクレイピング =====
for kw in KEYWORDS:
    url = f"https://www.wantedly.com/projects?keywords={kw}"
    print(f"取得中: {kw}")

    driver.get(url)
    time.sleep(5)

    elements = driver.find_elements(By.CSS_SELECTOR, "a")

    for el in elements:
        link = el.get_attribute("href")
        text = el.text.strip()

        if not link or "/projects/" not in link:
            continue

        if not text:
            continue

        if any(ex in text for ex in EXCLUDE_KEYWORDS):
            continue

        if link in links:
            continue

        titles.append(text)
        companies.append("不明")
        links.append(link)
        dates.append("不明")
        keyword_list.append(kw)

        # ===== 新着判定 =====
        if link not in old_links:
            messages.append(f"🆕[{kw}]\n{text}\n{link}")

        if len(titles) >= 50:
            break

    time.sleep(1)

driver.quit()

# ===== 0件対策 =====
if len(titles) == 0:
    print("⚠ データ0件 → ダミー追加")
    titles = ["サンプル求人"]
    companies = ["テスト株式会社"]
    links = ["https://example.com"]
    dates = ["今日"]
    keyword_list = ["テスト"]

# ===== CSV保存 =====
df = pd.DataFrame({
    "keyword": keyword_list,
    "title": titles,
    "company": companies,
    "date": dates,
    "link": links
})

df.to_csv(CSV_FILE, index=False, encoding="utf-8-sig")

print(f"保存完了: {len(df)}件")

# ===== LINE通知（まとめ）=====
if messages:
    text = "【新着求人まとめ】\n\n" + "\n\n".join(messages[:5])
    send_line(text)
    print("LINE通知送信")
else:
    print("新着なし")
