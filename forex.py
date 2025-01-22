from yahoo_fin import stock_info as si
import datetime
from textblob import TextBlob
from newsapi import NewsApiClient
from dotenv import load_dotenv
import os
import matplotlib.pyplot as plt
import time
import nltk
from collections import Counter
import re


nltk.download('punkt')
nltk.download('stopwords')


load_dotenv()


NEWS_API_KEY = os.getenv('NEWS_API_KEY')


newsapi = NewsApiClient(api_key=NEWS_API_KEY)


from nltk.corpus import stopwords
stop_words = set(stopwords.words('english'))

def get_stock_info(symbol):
    try:
        stock_data = si.get_data(symbol, start_date="2023-01-01", end_date=datetime.datetime.now()) 
        last_close = stock_data['close'].iloc[-1]
        volume = stock_data['volume'].iloc[-1]
        print(f"**{symbol} Bilgileri:**")
        print(f"Son Kapanış Fiyatı: ${last_close:.2f}")
        print(f"Günlük Hacim: {volume}")

        plt.figure(figsize=(10, 5))
        plt.plot(stock_data.index, stock_data['close'], label='Kapanış Fiyatı', color='blue')
        plt.title(f"{symbol} Fiyat Geçmişi")
        plt.xlabel('Tarih')
        plt.ylabel('Fiyat (USD)')
        plt.grid(True)
        plt.savefig('stock_chart.png')
        print("Grafik kaydedildi: stock_chart.png")
        
    except Exception as e:
        print(f"Bir hata oluştu: {e}")

def get_stock_news(symbol):
    try:
        query = symbol.split('.')[0] + " stock"
        articles = newsapi.get_everything(q=query, language='en', sort_by='relevancy', page_size=10)
        
        if articles.get('articles'):
            print("**Son Haberler ve Analizi:**")
            all_keywords = []

            for i, article in enumerate(articles['articles']):
                title = article['title']
                url = article['url']
                analysis = TextBlob(title)
                sentiment = analysis.sentiment.polarity
                sentiment_label = 'Pozitif' if sentiment > 0 else 'Negatif' if sentiment < 0 else 'Nötr'
                print(f"\n**Haber {i + 1}:** {title}")
                print(f"Kaynak: {article['source']['name']}")
                print(f"AI Analiz: {sentiment_label}")
                print(f"Link: {url}")
                keywords = extract_keywords(title)
                all_keywords.extend(keywords)

            print("\n**Anahtar Kelimeler:**")
            most_common_keywords = Counter(all_keywords).most_common(10)
            for keyword, freq in most_common_keywords:
                print(f"{keyword}: {freq}")
        else:
            print(f"{symbol} için haber bulunamadı.")
    except Exception as e:
        print(f"Haberleri alırken bir hata oluştu: {e}")


def extract_keywords(text):
    words = nltk.word_tokenize(text.lower())
    filtered_words = [word for word in words if word.isalpha() and word not in stop_words]
    return filtered_words

def get_global_stock_data(symbols):
    for symbol in symbols:
        print(f"\n\n****{symbol} Hisse Bilgisi ve Haberleri****")
        get_stock_info(symbol)
        get_stock_news(symbol)

def format_symbols(symbols):
    bist_symbols, global_symbols = [], []
    for symbol in symbols:
        symbol = symbol.strip().upper()
        if symbol.endswith(".IS") or symbol in {"BIST100", "XU100"}:
            bist_symbols.append(symbol if symbol.endswith(".IS") else symbol + ".IS")
        else:
            global_symbols.append(symbol)
    return bist_symbols, global_symbols

while True:
    symbols = input("Global veya BIST hisseleri girin (AAPL, ALARK): ").strip().split(',')
    bist_symbols, global_symbols = format_symbols(symbols)

    if bist_symbols:
        print("\nBIST Hisse Sorguları:")
        get_global_stock_data(bist_symbols)         

    if global_symbols:
        print("\nGlobal Hisse Sorguları:")
        get_global_stock_data(global_symbols)

    devam_et = input("\nBaşka hisse senetleri hakkında bilgi almak ister misiniz? (Evet/Hayır): ").strip().lower()
    if devam_et != 'evet':
        print("Program Sonlandırılıyor. Görüşmek Üzere")
        break
