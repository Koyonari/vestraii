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
    """Get a comprehensive list of top stocks by combining multiple sources"""
    try:
        all_tickers = set()
        
        # Try S&P 500 components
        try:
            from io import StringIO
            
            headers = {
                'User-Agent': get_random_user_agent(),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Connection': 'keep-alive',
            }
            sp500_url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
            sp500_response = requests.get(sp500_url, headers=headers, timeout=15)
            sp500_response.raise_for_status()
            
            # Parse tables from Wikipedia - use StringIO to avoid FutureWarning
            tables = pd.read_html(StringIO(sp500_response.text))
            
            # The first table usually contains the S&P 500 companies
            sp500_df = tables[0]
            
            # Try different possible column names for ticker symbol
            ticker_column = None
            for col in ['Symbol', 'Ticker', 'Ticker symbol', 'Stock']:
                if col in sp500_df.columns:
                    ticker_column = col
                    break
            
            if ticker_column:
                tickers = sp500_df[ticker_column].dropna().astype(str).str.strip().tolist()
                all_tickers.update(tickers)
                print(f"✓ Fetched {len(tickers)} S&P 500 tickers")
            else:
                # If no ticker column found, try to extract from first column
                if len(sp500_df.columns) > 0:
                    # Usually the first column is the ticker - convert to string first
                    first_col_data = sp500_df.iloc[:, 0].dropna().astype(str)
                    # Filter out non-ticker values (tickers are usually 1-5 uppercase letters)
                    tickers = [t.strip() for t in first_col_data if isinstance(t, str) and 1 <= len(t) <= 5 and t.replace('.', '').replace('-', '').isalnum()]
                    
                    if tickers:
                        all_tickers.update(tickers)
                        print(f"✓ Fetched {len(tickers)} S&P 500 tickers from first column")
                    else:
                        raise ValueError("Could not extract valid tickers from table")
                else:
                    raise ValueError("Could not identify ticker column in S&P 500 table")
                    
        except Exception as e:
            print(f"Warning: Could not fetch S&P 500 data: {e}")
        
        # Add NASDAQ 100 components
        try:
            from io import StringIO
            
            ndx_url = "https://en.wikipedia.org/wiki/Nasdaq-100"
            headers['User-Agent'] = get_random_user_agent()  # Rotate user agent
            ndx_response = requests.get(ndx_url, headers=headers, timeout=15)
            ndx_response.raise_for_status()
            
            ndx_tables = pd.read_html(StringIO(ndx_response.text))
            
            # Find the table with ticker information
            ndx_df = None
            for table in ndx_tables:
                if 'Ticker' in table.columns or 'Symbol' in table.columns:
                    ndx_df = table
                    break
            
            if ndx_df is not None:
                ticker_col = 'Ticker' if 'Ticker' in ndx_df.columns else 'Symbol'
                tickers = ndx_df[ticker_col].dropna().str.strip().tolist()
                all_tickers.update(tickers)
                print(f"✓ Fetched {len(tickers)} NASDAQ 100 tickers")
        except Exception as e:
            print(f"Warning: Could not fetch NASDAQ 100 data: {e}")
        
        # Add Dow Jones components
        try:
            from io import StringIO
            
            dow_url = "https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average"
            headers['User-Agent'] = get_random_user_agent()  # Rotate user agent
            dow_response = requests.get(dow_url, headers=headers, timeout=15)
            dow_response.raise_for_status()
            
            dow_tables = pd.read_html(StringIO(dow_response.text))
            
            # Find the table with ticker information
            dow_df = None
            for table in dow_tables:
                if 'Symbol' in table.columns or 'Ticker' in table.columns:
                    dow_df = table
                    break
            
            if dow_df is not None:
                ticker_col = 'Symbol' if 'Symbol' in dow_df.columns else 'Ticker'
                tickers = dow_df[ticker_col].dropna().str.strip().tolist()
                all_tickers.update(tickers)
                print(f"✓ Fetched {len(tickers)} Dow Jones tickers")
        except Exception as e:
            print(f"Warning: Could not fetch Dow Jones data: {e}")
        
        # If we have very few tickers, add fallback tickers
        if len(all_tickers) < 50:
            print(f"Only {len(all_tickers)} tickers found, adding fallback tickers...")
            all_tickers.update(FALLBACK_TICKERS)
        
        # Clean tickers
        tickers = [t.strip().replace('.', '-') for t in all_tickers if t and isinstance(t, str) and len(t) <= 10]
        tickers = list(set(tickers))  # Remove duplicates
        
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
                    name = info.get('shortName', info.get('longName', ticker))
                    sector = info.get('sector', 'Unknown')
                    
                    if market_cap and market_cap > 0:
                        chunk_data.append({
                            'ticker': ticker,
                            'name': name,
                            'market_cap': market_cap,
                            'sector': sector
                        })
                except Exception as e:
                    # Silently skip failed tickers
                    pass
                
                # Rate limiting
                time.sleep(random.uniform(REQUEST_DELAY_MIN, REQUEST_DELAY_MAX))
            
            results.extend(chunk_data)
            success_count = len([r for r in chunk_data if r['market_cap'] > 0])
            print(f"Processed chunk {idx+1}/{len(ticker_chunks)} ({success_count} successful)")
            
            if idx < len(ticker_chunks) - 1:  # Don't sleep after last chunk
                time.sleep(CHUNK_DELAY)
        
        # Convert to DataFrame and sort by market cap
        stocks_df = pd.DataFrame(results)
        stocks_df = stocks_df[stocks_df['market_cap'] > 0]  # Filter out invalid entries
        stocks_df = stocks_df.sort_values('market_cap', ascending=False).reset_index(drop=True)
        
        print(f"\nFound {len(stocks_df)} valid stocks with market cap data")
        if len(stocks_df) < 100:
            print(f"Warning: Only {len(stocks_df)} stocks available for analysis")
        
        # Take top 100 by market cap
        top_stocks = stocks_df.head(100)
        return top_stocks
    
    except Exception as e:
        print(f"Error getting top stocks: {e}")
        import traceback
        traceback.print_exc()
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
            name = info.get('shortName', info.get('longName', ticker))
            sector = info.get('sector', 'Unknown')
            
            results.append({
                'ticker': ticker,
                'name': name,
                'market_cap': market_cap if market_cap else 0,
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
    
    df = pd.DataFrame(results)
    df = df[df['market_cap'] > 0]  # Filter out invalid entries
    return df.sort_values('market_cap', ascending=False).reset_index(drop=True)


def scrape_finviz_news(ticker):
    """Scrape news headlines for a specific ticker from Finviz"""
    url = f'https://finviz.com/quote.ashx?t={ticker}'
    headers = {
        'User-Agent': get_random_user_agent(),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0',
        'Referer': 'https://finviz.com/'
    }
    
    max_retries = 3
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            if attempt > 0:
                time.sleep(retry_delay)
            
            time.sleep(random.uniform(REQUEST_DELAY_MIN, REQUEST_DELAY_MAX))
            
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Check if we got a valid page
            if "is not found" in soup.text or "Error" in soup.title.text:
                return pd.DataFrame()
            
            news_table = soup.find(id='news-table')
            if not news_table:
                continue
            
            news_data = []
            current_date = datetime.now().strftime('%m/%d/%y')
            
            for row in news_table.find_all('tr'):
                if not row.td:
                    continue
                
                try:
                    date_cell = row.td.text.strip().split() if row.td and row.td.text else []
                    
                    date_str = current_date
                    time_str = ''
                    
                    if len(date_cell) >= 1:
                        if ':' in date_cell[0]:
                            time_str = date_cell[0]
                        elif len(date_cell) >= 2:
                            date_str = date_cell[0]
                            time_str = date_cell[1] if ':' in date_cell[1] else ''
                    
                    headline = row.a.text.strip() if row.a else None
                    source = row.span.text.strip() if row.span else "Unknown"
                    
                    if headline and len(headline) > 5:
                        news_data.append([date_str, time_str, headline, source])
                
                except Exception:
                    continue
            
            if news_data:
                return pd.DataFrame(news_data, columns=['date', 'time', 'headline', 'source'])
            
        except Exception as e:
            if attempt == max_retries - 1:
                return pd.DataFrame()
    
    return pd.DataFrame()


def scrape_yahoo_finance_news(ticker):
    """Scrape news from Yahoo Finance for a specific ticker"""
    news_data = []
    
    try:
        time.sleep(random.uniform(REQUEST_DELAY_MIN, REQUEST_DELAY_MAX))
        
        # Use yfinance news (more reliable)
        try:
            import yfinance as yf
            stock = yf.Ticker(ticker)
            news = stock.news
            
            if news:
                for item in news[:20]:
                    headline = item.get('title', '')
                    if headline and len(headline) > 5:
                        news_data.append([
                            datetime.now().strftime('%m/%d/%y'),
                            'N/A',
                            headline,
                            item.get('publisher', 'Yahoo Finance')
                        ])
                
                if news_data:
                    return pd.DataFrame(news_data, columns=['date', 'time', 'headline', 'source'])
        except Exception:
            pass
        
        # Fallback: try scraping main quote page
        base_url = f'https://finance.yahoo.com/quote/{ticker}'
        headers = {
            'User-Agent': get_random_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }
        
        try:
            response = requests.get(base_url, headers=headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            news_items = (
                soup.select('h3') +
                soup.select('h4') +
                soup.find_all('a', href=lambda x: x and '/news/' in str(x))
            )
            
            for item in news_items[:20]:
                headline = item.text.strip()
                if headline and len(headline) > 10 and not any(skip in headline.lower() for skip in ['sponsored', 'advertisement', 'sign in', 'subscribe']):
                    news_data.append([
                        datetime.now().strftime('%m/%d/%y'),
                        'N/A',
                        headline,
                        'Yahoo Finance'
                    ])
            
            if news_data:
                seen = set()
                unique_news = []
                for item in news_data:
                    if item[2] not in seen:
                        seen.add(item[2])
                        unique_news.append(item)
                news_data = unique_news
                
        except Exception:
            pass
    
    except Exception:
        pass
    
    return pd.DataFrame(news_data, columns=['date', 'time', 'headline', 'source']) if news_data else pd.DataFrame()


def get_stock_price_data(ticker, days=90):
    """Get historical stock price data using yfinance (default: 90 days = 3 months)"""
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        stock = yf.Ticker(ticker)
        
        # Try to fetch historical data
        hist = stock.history(start=start_date, end=end_date)
        
        if hist is None:
            print(f"    ⚠ yfinance returned None for {ticker}")
            return None
        
        if hist.empty:
            print(f"    ⚠ No historical data for {ticker}")
            return None
        
        # Ensure we have data and required columns
        if len(hist) == 0:
            print(f"    ⚠ Empty history for {ticker}")
            return None
        
        # Check if 'Close' column exists
        if 'Close' not in hist.columns:
            print(f"    ⚠ No Close price data for {ticker}")
            return None
        
        # Filter out NaN values
        hist = hist.dropna(subset=['Close'])
        
        if len(hist) == 0:
            print(f"    ⚠ All Close prices are NaN for {ticker}")
            return None
        
        return hist
    
    except Exception as e:
        print(f"    ✗ Error fetching price data for {ticker}: {type(e).__name__}: {str(e)}")
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
