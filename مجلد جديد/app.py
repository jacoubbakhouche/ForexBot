from flask import Flask, request, render_template, jsonify
import threading
import requests
import pandas as pd
from forex_python.converter import CurrencyRates
import time

app = Flask(__name__)

# إعداد API Key الخاص بك
API_KEY = "5DLV8UCQ46V6S7RE"

# الدالة للحصول على البيانات الاقتصادية
def get_economic_data():
    url = f"https://www.alphavantage.co/query?function=FX_DAILY&from_symbol=EUR&to_symbol=USD&apikey={API_KEY}"
    response = requests.get(url)
    data = response.json()
    if "Time Series FX (Daily)" in data:
        return data["Time Series FX (Daily)"]
    else:
        print("Error fetching data:", data)
        return None

# تحليل البيانات الاقتصادية
def analyze_economic_data(data):
    important_news = []
    for date, stats in data.items():
        close_price = float(stats['4. close'])
        important_news.append({
            "date": date,
            "close_price": close_price
        })
    return important_news

# تنفيذ قرارات التداول
def execute_trade(decision, amount, from_currency, to_currency):
    c = CurrencyRates()
    rate = c.get_rate(from_currency, to_currency)
    if decision == "buy":
        print(f"Buying {amount} {from_currency} at rate {rate} {to_currency}")
    elif decision == "sell":
        print(f"Selling {amount} {from_currency} at rate {rate} {to_currency}")

# بوت التداول
def trading_bot():
    while True:
        data = get_economic_data()
        if data:
            important_news = analyze_economic_data(data)
            for news in important_news:
                if news['close_price'] > 1.10:
                    execute_trade("buy", 1000, "EUR", "USD")
                elif news['close_price'] < 1.05:
                    execute_trade("sell", 1000, "EUR", "USD")
        time.sleep(3600)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start-bot', methods=['POST'])
def start_bot():
    bot_thread = threading.Thread(target=trading_bot)
    bot_thread.start()
    return jsonify({"status": "Bot started"})

if __name__ == "__main__":
    app.run(debug=True)
