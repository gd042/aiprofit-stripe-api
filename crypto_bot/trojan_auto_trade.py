import os
import logging
import json
import time
import requests
from dotenv import load_dotenv
from telethon import TelegramClient

# Load environment variables securely
load_dotenv()

# 🔹 Set API Credentials (Loaded from Render Environment Variables)
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
BIRDEYE_API_KEY = os.getenv("BIRDEYE_API_KEY")

# ✅ Setup Telegram Client
client = TelegramClient('trojan_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# ✅ Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("crypto_trade_log.txt"),
        logging.StreamHandler()
    ]
)

# ✅ Birdeye API Endpoint (Fetch Trending Coins)
BIRDEYE_TRENDING_URL = "https://api.birdeye.so/trending"

# ✅ Trojan Bot Commands
TROJAN_COMMANDS = {
    "buy": "/buy",    # Buy a token
    "sell": "/sell",  # Sell a token
    "balance": "/balance"  # Check balance
}

# ✅ Trade Configuration
TRADE_AMOUNT = 5  # £5 Test Trades
SLIPPAGE = 2  # 2% Slippage tolerance

# -------------------------------------
# 🚀 FUNCTION: Fetch Trending Solana Coins
# -------------------------------------
def fetch_trending_coins():
    headers = {"x-api-key": BIRDEYE_API_KEY}
    response = requests.get(BIRDEYE_TRENDING_URL, headers=headers)
    
    if response.status_code == 200:
        try:
            data = response.json()
            coins = data.get("pairs", [])
            return coins
        except json.JSONDecodeError:
            logging.error("❌ Failed to parse Birdeye API response.")
    else:
        logging.error(f"❌ Failed to fetch trending coins. Status: {response.status_code}")
    
    return []

# -------------------------------------
# 🚀 FUNCTION: Execute Trade on Trojan Bot
# -------------------------------------
async def execute_trade(token_address, trade_type="buy"):
    """
    Sends a command to the Trojan bot to buy or sell a token.
    """
    command = TROJAN_COMMANDS[trade_type]
    trade_message = f"{command} {token_address} {TRADE_AMOUNT} SOL slippage {SLIPPAGE}"
    
    logging.info(f"🚀 Executing {trade_type.upper()} trade for token: {token_address}")
    
    try:
        async with client:
            await client.send_message("@solana_trojanbot", trade_message)
            logging.info(f"✅ Trade executed: {trade_message}")
    except Exception as e:
        logging.error(f"❌ Trade execution failed: {e}")

# -------------------------------------
# 🚀 FUNCTION: Trading Strategy Execution
# -------------------------------------
async def trade_bot():
    """
    Core loop that continuously scans for trending coins and executes trades.
    """
    while True:
        logging.info("🔍 Scanning for trending tokens...")
        trending_coins = fetch_trending_coins()
        
        if not trending_coins:
            logging.warning("⚠️ No trending tokens found. Retrying in 30 minutes...")
            time.sleep(1800)  # Wait 30 minutes before retrying
            continue
        
        for coin in trending_coins:
            token_address = coin.get("address")
            symbol = coin.get("symbol")
            
            if token_address:
                logging.info(f"🚀 Buying trending token: {symbol} ({token_address})")
                await execute_trade(token_address, trade_type="buy")
                time.sleep(10)  # Wait 10 seconds between trades
        
        logging.info("🕒 Waiting before next scan...")
        time.sleep(1800)  # Wait 30 minutes before scanning again

# -------------------------------------
# 🚀 RUN THE TRADING BOT
# -------------------------------------
if __name__ == "__main__":
    import asyncio
    asyncio.run(trade_bot())
