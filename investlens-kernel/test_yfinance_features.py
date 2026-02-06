
import yfinance as yf
import json

def test_data(ticker_symbol):
    print(f"Fetching data for {ticker_symbol}...")
    try:
        stock = yf.Ticker(ticker_symbol)
        
        print("\n--- RECOMMENDATIONS ---")
        try:
            recs = stock.recommendations
            if recs is not None and not recs.empty:
                print(recs.tail())
            else:
                print("No recommendations found.")
        except Exception as e:
            print(f"Error fetching recommendations: {e}")

        print("\n--- FINANCIALS ---")
        try:
            fin = stock.financials
            if fin is not None and not fin.empty:
                print(fin.iloc[:, :2]) # Show first 2 columns
            else:
                print("No financials found.")
        except Exception as e:
            print(f"Error fetching financials: {e}")
            
        print("\n--- NEWS ---")
        try:
            news = stock.news
            if news:
                for n in news[:3]:
                    print(f"- {n.get('title')} ({n.get('publisher')})")
            else:
                print("No news found.")
        except Exception as e:
            print(f"Error fetching news: {e}")

    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    test_data("AAPL")
