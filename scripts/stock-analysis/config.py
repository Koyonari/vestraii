import os
from dotenv import load_dotenv
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
env_path = project_root / '.env.local'
load_dotenv(env_path)

# Supabase Configuration
SUPABASE_URL = os.getenv('NEXT_PUBLIC_SUPABASE_URL')

# Use service role key if available (for server-side operations), otherwise use anon key
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY') or os.getenv('NEXT_PUBLIC_SUPABASE_ANON_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Missing required Supabase environment variables")

# Analysis Configuration
MAX_STOCKS = int(os.getenv('MAX_STOCKS', '100'))
DAYS_BACK = int(os.getenv('DAYS_BACK', '90'))  # 3 months of historical data
PREDICTION_DAYS = int(os.getenv('PREDICTION_DAYS', '30'))  # 1 month of predictions
HISTORICAL_DAYS = 90  # Explicitly set to 90 days (3 months)
MODEL_HISTORY_DAYS = int(os.getenv('MODEL_HISTORY_DAYS', '730'))  # 2 years, so ~8 past earnings reports

# Rate Limiting
REQUEST_DELAY_MIN = float(os.getenv('REQUEST_DELAY_MIN', '1.5'))
REQUEST_DELAY_MAX = float(os.getenv('REQUEST_DELAY_MAX', '3.0'))
CHUNK_SIZE = int(os.getenv('CHUNK_SIZE', '5'))
CHUNK_DELAY = float(os.getenv('CHUNK_DELAY', '5.0'))

# User Agents for Web Scraping
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
]

# Finance-specific lexicon for sentiment analysis.
# Each positive/negative pair shares one magnitude so the lexicon itself doesn't skew
# bullish, and common inflections are listed since VADER matches whole words only.
_FINANCE_TERM_PAIRS = [
    (3.5, ['bullish'], ['bearish']),
    (3.0, ['upgrade', 'upgrades', 'upgraded'], ['downgrade', 'downgrades', 'downgraded']),
    (3.0, ['surge', 'surges', 'surged', 'soar', 'soars', 'soared'],
          ['plunge', 'plunges', 'plunged', 'tumble', 'tumbles', 'tumbled']),
    (3.0, ['rally', 'rallies', 'rallied'], ['crash', 'crashes', 'crashed']),
    (3.0, ['breakthrough'], ['breakdown']),
    (2.5, ['beat', 'beats', 'exceeded', 'exceeds'], ['miss', 'misses', 'missed']),
    (2.5, ['outperform', 'outperforms'], ['underperform', 'underperforms']),
    (2.5, ['buy'], ['sell']),
    (2.0, ['growth', 'profit', 'profits'], ['decline', 'declines', 'loss', 'losses']),
    (2.0, ['strong', 'positive'], ['weak', 'negative']),
    (1.5, ['rise', 'rises', 'rose', 'gain', 'gains', 'jump', 'jumps'],
          ['fall', 'falls', 'fell', 'drop', 'drops', 'slump', 'slumps']),
]
FINANCE_LEXICON = {
    word: magnitude * sign
    for magnitude, positive, negative in _FINANCE_TERM_PAIRS
    for sign, words in ((1, positive), (-1, negative))
    for word in words
}

# Fallback stock tickers
FALLBACK_TICKERS = [
    "AAPL", "MSFT", "AMZN", "GOOGL", "META", "TSLA", "NVDA", "BRK-B", "JPM", "V",
    "JNJ", "UNH", "PG", "MA", "HD", "BAC", "XOM", "AVGO", "CVX", "COST",
    "ABBV", "MRK", "PEP", "KO", "LLY", "TMO", "CSCO", "ABT", "CRM", "MCD",
    "ACN", "WMT", "NKE", "DHR", "TXN", "UPS", "NEE", "PM", "ORCL", "IBM",
    "QCOM", "INTC", "NFLX", "ADBE", "AMD", "CMCSA", "HON", "PFE", "CAT", "UNP"
]
