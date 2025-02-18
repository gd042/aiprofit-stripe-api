import os
import time
import json
import requests
from dotenv import load_dotenv
from telethon.sync import TelegramClient

# Load environment variables
load_dotenv()

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # Your Trojan bot token
BIRDEYE_API_KEY = os.getenv("BIRDEYE_API_KEY")  # Birdeye API Key

# Initialize Telegram Client
client = TelegramClient('trojan_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# Birdeye API URL for trending Solana tokens
BIRDEYE_TRENDING_URL = "https://api.birdeye.so/trending"
HEADERS = {"X-API-KEY": BIRDEYE_API_KEY}

# Trading settings
TRADE_AMOUNT = 5  # £5 per trade
STOP_LOSS_PERCENT = 10  # 10% stop loss
TAKE_PROFIT_PERCENT = 50  # 50% take profit

def fetch_trending_tokens():
    """Fetch trending Solana meme coins from Birdeye API."""
    try:
        response = requests.get(BIRDEYE_TRENDING_URL, headers=HEADERS)
        data = response.json()
        if "pairs" in data:
            return data["pairs"]
        else:
            print("No trending pairs found.")
            return None
    except Exception as e:
        print(f"Error fetching trending tokens: {e}")
        return None

def analyze_token(token):
    """Perform risk analysis on token before buying."""
    liquidity = token.get("liquidity", 0)
    holders = token.get("holders", 0)
    safety_score = 0

    if liquidity > 10000:  # Minimum liquidity check
        safety_score += 1
    if holders > 1000:  # Minimum holders check
        safety_score += 1
    if token.get("name") and "rug" not in token.get("name").lower():
        safety_score += 1

    return safety_score >= 2  # Trade only if score is 2 or above

def buy_token(token):
    """Send buy command to Trojan bot in Telegram."""
    message = f"/buy {token['pair_address']} {TRADE_AMOUNT} SOL"
    print(f"Buying {token['name']} - {message}")
    client.send_message("@solana_trojanbot", message)

def monitor_and_sell(token):
    """Monitor price movement and sell when profit or stop-loss triggers."""
    buy_price = token["price"]
    stop_loss = buy_price * (1 - STOP_LOSS_PERCENT / 100)
    take_profit = buy_price * (1 + TAKE_PROFIT_PERCENT / 100)

    while True:
        time.sleep(60)  # Wait a minute before checking price
        response = requests.get(f"https://api.birdeye.so/price/{token['pair_address']}", headers=HEADERS)
        data = response.json()

        if "price" in data:
            current_price = data["price"]
            if current_price <= stop_loss:
                print(f"Stop-loss hit for {token['name']} - Selling...")
                sell_token(token)
                break
            elif current_price >= take_profit:
                print(f"Take-profit hit for {token['name']} - Selling...")
                sell_token(token)
                break
        else:
            print(f"Failed to fetch updated price for {token['name']}.")

def sell_token(token):
    """Send sell command to Trojan bot in Telegram."""
    message = f"/sell {token['pair_address']} ALL"
    print(f"Selling {token['name']} - {message}")
    client.send_message("@solana_trojanbot", message)

def main():
    print("🚀 Starting Solana Meme Coin Trading Bot...")

    trending_tokens = fetch_trending_tokens()
    if not trending_tokens:
        print("No trending tokens found. Exiting...")
        return

    for token in trending_tokens[:3]:  # Only trade top 3 trending tokens
        if analyze_token(token):
            buy_token(token)
            monitor_and_sell(token)
        else:
            print(f"Skipping {token['name']} due to risk assessment.")

    print("✅ Trading cycle complete. Waiting for next run...")

if __name__ == "__main__":
    main()
