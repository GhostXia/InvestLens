import akshare as ak
import sys

def test_name_fetch(ticker="603986"):
    print(f"Testing name fetch for {ticker}...")
    try:
        # Try individual info
        info = ak.stock_individual_info_em(symbol=ticker)
        print("stock_individual_info_em result:")
        print(info)
        # Look for name in the dataframe/series
        # It usually returns a generic info table
    except Exception as e:
        print(f"stock_individual_info_em failed: {e}")

    try:
        # Try real-time spot for single (optimization? no, spot is usually all)
        # But let's see if we can get it from stock_info_a_code_name
        code_name_map = ak.stock_info_a_code_name()
        row = code_name_map[code_name_map['code'] == ticker]
        print("\nstock_info_a_code_name result:")
        print(row)
    except Exception as e:
        print(f"stock_info_a_code_name failed: {e}")

if __name__ == "__main__":
    ticker = sys.argv[1] if len(sys.argv) > 1 else "603986"
    test_name_fetch(ticker)
