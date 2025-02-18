import os
import time
from dotenv import load_dotenv
from telethon import TelegramClient, events

# Load environment variables if local .env is used.
# On Render, environment vars are injected automatically.
load_dotenv()

API_ID = int(os.getenv("TG_API_ID", "0"))
API_HASH = os.getenv("TG_API_HASH")
TROJAN_USERNAME = os.getenv("TROJAN_BOT_USERNAME")

client = TelegramClient('trojan_session', API_ID, API_HASH)

@client.on(events.NewMessage(chats=TROJAN_USERNAME))
async def trojan_response_handler(event):
    print("Trojan says:", event.raw_text)

async def buy_memecoin(token_symbol, amount):
    cmd = f"/buy {token_symbol} {amount}"
    await client.send_message(TROJAN_USERNAME, cmd)

async def sell_memecoin(token_symbol, amount):
    cmd = f"/sell {token_symbol} {amount}"
    await client.send_message(TROJAN_USERNAME, cmd)

async def main_loop():
    while True:
        # Example: no trades, just waits an hour
        print("No trades this cycle. (Replace with your logic!)")
        time.sleep(3600)

with client:
    client.loop.run_until_complete(main_loop())

