import pandas as pd
import yfinance as yf
import requests
from bs4 import BeautifulSoup
import time
import random
from datetime import datetime, timedelta
from config import (
    USER_AGENTS, FALLBACK_TICKERS, REQUEST_DELAY_MIN, 
    REQUEST_DELAY_MAX, CHUNK_DELAY, CHUNK_SIZE
)


def get_random_user_agent():
    """Return a random user agent to avoid detection"""
    return random.choice(USER_AGENTS)


def get_top_101_stocks():
    """Get the list of top stocks by market cap from S&P 500"""
    try:
        # Get S&P 500 components
        sp500_url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
        sp500_table = pd.read_html(sp500_url)
        sp500_df = sp500_table[0]
        
        tickers = sp500_df['Symbol'].tolist()
        print(f"Fetching market cap data for {len(tickers)} stocks...")
        
        # Get market cap data in chunks
        results = []
        ticker_chunks = [tickers[i:i + CHUNK_SIZE] for i in range(0, len(tickers), CHUNK_SIZE)]
        
        for idx, chunk in enumerate(ticker_chunks):
            chunk_data = []
            for ticker in chunk:
                try:
                    stock = yf.Ticker(ticker)
                    info = stock.info
                    market_cap = info.get('marketCap', 0)
                    name = info.get('shortName', ticker)
                    sector = info.get('sector', 'Unknown')
                    
                    chunk_data.append({
                        'ticker': ticker,
                        'name': name,
                        'market_cap': market_cap,
                        'sector': sector
                    })
                except Exception as e:
                    print(f"Error fetching data for {ticker}: {e}")
                
                # Rate limiting
                time.sleep(random.uniform(REQUEST_DELAY_MIN, REQUEST_DELAY_MAX))
            
            results.extend(chunk_data)
            print(f"Processed {len(results)} stocks...")
            
            if idx < len(ticker_chunks) - 1:  # Don't sleep after last chunk
                time.sleep(CHUNK_DELAY)
        
        # Convert to DataFrame and sort by market cap
        stocks_df = pd.DataFrame(results)
        stocks_df = stocks_df[stocks_df['market_cap'] > 0]  # Filter out invalid entries
        stocks_df = stocks_df.sort_values('market_cap', ascending=False).reset_index(drop=True)
        
        # Take top 100
        top_100 = stocks_df.head(100)
        return top_100
    
    except Exception as e:
        print(f"Error getting top stocks: {e}")
        return _get_fallback_stocks()


def _get_fallback_stocks():
    """Fallback method to get stock data using predefined list"""
    print("Using fallback stock list...")
    results = []
    
    for ticker in FALLBACK_TICKERS[:50]:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            market_cap = info.get('marketCap', 0)
            name = info.get('shortName', ticker)
            sector = info.get('sector', 'Unknown')
            
            results.append({
                'ticker': ticker,
                'name': name,
                'market_cap': market_cap,
                'sector': sector
            })
        except Exception as e:
            print(f"Error in fallback list for {ticker}: {e}")
            results.append({
                'ticker': ticker,
                'name': ticker,
                'market_cap': 0,
                'sector': 'Unknown'
            })
        
        time.sleep(random.uniform(REQUEST_DELAY_MIN, REQUEST_DELAY_MAX))
    
    return pd.DataFrame(results)


def scrape_finviz_news(ticker):
    """Scrape news headlines for a specific ticker from Finviz"""
    url = f'https://finviz.com/quote.ashx?t={ticker}'
    headers = {
        'User-Agent': get_random_user_agent(),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0'
    }
    
    try:
        time.sleep(random.uniform(REQUEST_DELAY_MIN, REQUEST_DELAY_MAX))
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        news_table = soup.find(id='news-table')
        
        if not news_table:
            print(f"Warning: Could not find news table for {ticker} on Finviz")
            return pd.DataFrame()
        
        news_data = []
        current_date = datetime.now().strftime('%m/%d/%y')
        
        for row in news_table.find_all('tr'):
            if not row.td:
                continue
            
            date_cell = row.td.text.strip().split() if row.td and row.td.text else []
            
            # Parse date and time
            date_str = current_date
            time_str = ''
            
            if len(date_cell) >= 1:
                if ':' in date_cell[0]:  # Just time, use today's date
                    time_str = date_cell[0]
                elif len(date_cell) >= 2:  # Date and time
                    date_str = date_cell[0]
                    time_str = date_cell[1] if ':' in date_cell[1] else ''
            
            headline = row.a.text.strip() if row.a else "No headline"
            source = row.span.text.strip() if row.span else "Unknown"
            
            news_data.append([date_str, time_str, headline, source])
        
        df = pd.DataFrame(news_data, columns=['date', 'time', 'headline', 'source'])
        return df
    
    except Exception as e:
        print(f"Error scraping {ticker} news from Finviz: {e}")
        return pd.DataFrame()


def scrape_yahoo_finance_news(ticker):
    """Scrape news from Yahoo Finance for a specific ticker"""
    url = f'https://finance.yahoo.com/quote/{ticker}/news'
    headers = {
        'User-Agent': get_random_user_agent(),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5'
    }
    
    try:
        time.sleep(random.uniform(REQUEST_DELAY_MIN, REQUEST_DELAY_MAX))
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        news_items = soup.select('li.js-stream-content')
        
        news_data = []
        for item in news_items:
            headline_elem = item.select_one('h3') or item.select_one('h4')
            time_elem = item.select_one('time')
            
            if headline_elem:
                headline = headline_elem.text.strip()
                timestamp = time_elem.text.strip() if time_elem else 'Unknown'
                news_data.append([
                    datetime.now().strftime('%m/%d/%y'), 
                    timestamp, 
                    headline, 
                    'Yahoo Finance'
                ])
        
        df = pd.DataFrame(news_data, columns=['date', 'time', 'headline', 'source'])
        return df
    
    except Exception as e:
        print(f"Error scraping Yahoo Finance news for {ticker}: {e}")
        return pd.DataFrame()


def get_stock_price_data(ticker, days=90):
    """Get historical stock price data using yfinance"""
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        stock = yf.Ticker(ticker)
        hist = stock.history(start=start_date, end=end_date)
        
        if hist.empty:
            print(f"No price data found for {ticker}")
            return None
        
        return hist
    
    except Exception as e:
        print(f"Error getting price data for {ticker}: {e}")
        return None


if __name__ == "__main__":
    # Test the functions
    print("Testing webscrape functions...")
    
    # Test get_top_101_stocks
    stocks = get_top_101_stocks()
    print(f"\nFound {len(stocks)} stocks")
    print(stocks.head())
    
    # Test scraping for AAPL
    if not stocks.empty:
        test_ticker = stocks.iloc[0]['ticker']
        print(f"\nTesting news scraping for {test_ticker}...")
        
        finviz_news = scrape_finviz_news(test_ticker)
        print(f"Finviz news items: {len(finviz_news)}")
        
        price_data = get_stock_price_data(test_ticker)
        print(f"Price data points: {len(price_data) if price_data is not None else 0}")
