"""
Test script for stock analysis feature
"""
from chatbot.stock_analyzer import stock_analyzer

print("=" * 70)
print("Stock Analyzer Test")
print("=" * 70)

# Test stocks
test_stocks = ['AAPL', 'TSLA', 'MSFT', 'GOOGL']

for symbol in test_stocks:
    print(f"\n{'='*70}")
    print(f"Analyzing: {symbol}")
    print('='*70)
    
    result = stock_analyzer.analyze_stock(symbol)
    print(result)
    print()

print("\n" + "=" * 70)
print("Test Complete!")
print("=" * 70)
