import yfinance as yf
try:
    print("Fetching major_holders for NVDA...")
    tick = yf.Ticker("NVDA")
    print("--- Major Holders ---")
    print(tick.major_holders)
    print("\n--- Institutional Holders ---")
    print(tick.institutional_holders)
except Exception as e:
    print(e)
