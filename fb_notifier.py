import os
import requests
from bs4 import BeautifulSoup
import re

KEYWORDS = ["應援棒", "手燈", "應援棒2.0", "未拆卡包"]

FACEBOOK_COOKIE = os.environ.get("FACEBOOK_COOKIE")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
GROUP_URL = os.environ.get("GROUP_URL")

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "disable_web_page_preview": True
    }
    try:
        response = requests.post(url, data=payload)
        if not response.ok:
            print("Telegram 發送失敗：", response.text)
    except Exception as e:
        print("Telegram 發送錯誤：", e)

def check_fb_group():
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Cookie": FACEBOOK_COOKIE
    }

    try:
        res = requests.get(GROUP_URL, headers=headers)
        if "login" in res.url or res.status_code != 200:
            send_telegram_message("Facebook Cookie 已失效，請更新。")
            return

        soup = BeautifulSoup(res.text, "html.parser")
        posts = soup.find_all('div')

        for post in posts:
            text = post.get_text()
            matched_keywords = [kw for kw in KEYWORDS if kw in text]
            if matched_keywords:
                href_match = re.search(r'href="(/[^"]+/permalink/[^"]+)"', str(post))
                if href_match:
                    post_url = "https://facebook.com" + href_match.group(1)
                else:
                    post_url = GROUP_URL
                message = f"找到貼文關鍵字：{', '.join(matched_keywords)}\n網址：{post_url}"
                send_telegram_message(message)
                return

    except Exception as e:
        send_telegram_message(f"抓取 Facebook 發生錯誤：{e}")

if __name__ == "__main__":
    check_fb_group()
