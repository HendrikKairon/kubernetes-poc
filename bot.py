import sys
import time
import requests
import ccxt
import os
import logging
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

logging.basicConfig(level=logging.INFO)


def send_message(chat_id, text):
    url = f"{BASE_URL}/sendMessage"
    params = {"chat_id": chat_id, "text": text}
    response = requests.post(url, params=params)
    if response.status_code != 200:
        logging.error(f"Failed to send message. Error: {response.text}")


def main():
    # Use a default symbol if not provided
    symbol = sys.argv[1] if len(sys.argv) > 1 else "BTC/USDT"
    exchange = ccxt.binance()
    starting_message = f"Starting price fetch for {symbol}."
    send_message(CHAT_ID, starting_message)

    while True:
        try:
            ticker = exchange.fetch_ticker(symbol)
        except Exception as e:
            logging.error(f"Failed to fetch ticker: {e}")
            continue

        price = ticker["last"]
        timestamp = ticker["timestamp"]
        timestamp_s = timestamp / 1000.0

        utc_time = datetime.utcfromtimestamp(timestamp_s)
        logging.info(f"Printing price in pod: {price} at {utc_time}")
        message = f"Fetched price from exchange: {symbol} - {price} at {utc_time}"
        send_message(CHAT_ID, message)
        time.sleep(5)


if __name__ == "__main__":
    main()
