import os
import time
import openai
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_content(prompt="Write a short daily update about Solana meme coins."):
    resp = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=100,
        temperature=0.7
    )
    return resp.choices[0].text.strip()

def post_to_twitter(text):
    # Placeholder function. If you want real posting, integrate a library (e.g. Tweepy).
    print(f"Mock tweet: {text}")

def daily_content_cycle():
    content = generate_content()
    post_to_twitter(content)

def main():
    while True:
        daily_content_cycle()
        # Sleep for 24 hours (86400 seconds)
        time.sleep(86400)

if __name__ == "__main__":
    main()

