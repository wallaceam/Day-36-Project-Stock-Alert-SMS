import requests as r
import datetime
import os
from twilio.rest import Client
import html

today = datetime.datetime.today().date()
yesterday = today - datetime.timedelta(days=1)
day_before_yesterday = yesterday - datetime.timedelta(days=1)

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"
STOCK_ENDPOINT = "https://www.alphavantage.co/query"
STOCK_API_KEY = "TBJQA7R7B7FS1IVR"
stock_params = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK,
    "apikey": STOCK_API_KEY
}

NEWS_ENDPOINT = "https://newsapi.org/v2/everything"
NEWS_API_KEY = "6f36ccaba024465ba46f26c1f4a2e290"
news_params = {
    "q": f"+{COMPANY_NAME}",
    "sortBy": "relevancy",
    "apiKey": NEWS_API_KEY,
    "language": "en",
}

# -------------------------------------- Get stock data -------------------------------------- #
stock_response = r.get(url=STOCK_ENDPOINT, params=stock_params)
stock_response.raise_for_status()
stock_data = stock_response.json()
close_yesterday = float(stock_data["Time Series (Daily)"][str(yesterday)]["4. close"])
close_day_b4_yesterday = float(stock_data["Time Series (Daily)"][str(day_before_yesterday)]["4. close"])
close_diff = close_yesterday - close_day_b4_yesterday
abs_close_diff = abs(close_diff)
diff_percent = round(((abs_close_diff / close_yesterday) * 100), 1)
five_percent = close_yesterday / 20

# -------------------------------------- If major price change, get news data -------------------------------------- #
if abs_close_diff >= five_percent:
    news_response = r.get(url=NEWS_ENDPOINT, params=news_params)
    news_response.raise_for_status()
    news_data = news_response.json()
    top_3_articles = news_data["articles"][0:3]

    # -------------------------------------- Send 3 news stories as SMS -------------------------------------- #
    if close_diff > 0:
        symbol = "🔺"
    else:
        symbol = "🔻"

    account_sid = os.environ["TWILIO_ACCOUNT_SID"]
    auth_token = os.environ['TWILIO_AUTH_TOKEN']
    client = Client(account_sid, auth_token)

    for article in top_3_articles:
        headline = html.unescape(top_3_articles[top_3_articles.index(article)]["title"])
        brief = html.unescape(top_3_articles[top_3_articles.index(article)]["description"])
        message = client.messages.create(
            body=f"{STOCK}: {symbol}{diff_percent}\nHeadline: {headline}\nBrief: {brief}",
            from_="+17628008695",
            to="+46720134980"
        )

        print(message.body)
