import os
import requests
from playwright.sync_api import sync_playwright

DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")
TARGET_URL = "https://patient.digikar-smart.jp/institutions/41e9afbb-777b-4052-b928-df75cf7cb74a/reserve?treatmentMenuId=bd79037b-3f52-4e54-8c5f-c7c93b0ecc96&firstVisit=true"

def send_discord_notify(message):
    if DISCORD_WEBHOOK_URL:
        requests.post(DISCORD_WEBHOOK_URL, json={"content": message})

def check_availability():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(TARGET_URL, timeout=60000)
            page.wait_for_load_state("networkidle")
            content = page.content()
            
            is_full = ("予約できる日時がありません" in content) or ("受付終了" in content) or ("現在満席" in content)
            
            if not is_full:
                msg = f"【予約チャンス！】八王子石井クリニックのボトックス予約枠に空きが出た可能性があります！\n確認URL: {TARGET_URL}"
                send_discord_notify(msg)
                print("空き枠検出！通知を送信しました。")
            else:
                print("現在も満席です。")
        except Exception as e:
            print(f"エラー発生: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    check_availability()
