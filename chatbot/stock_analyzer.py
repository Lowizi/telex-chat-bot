"""
Stock Analysis Module
Provides real-time stock data fetching, valuation calculations, and AI-powered recommendations
"""
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
import os
from openai import OpenAI


class StockAnalyzer:
    """
    Comprehensive stock analysis tool that:
    - Fetches real-time stock data
    - Calculates valuation metrics
    - Determines if stock is undervalued
    - Provides AI-powered recommendations
    """
    
    def __init__(self):
        """Initialize with OpenAI client if API key is available"""
        self.openai_client = None
        openai_key = os.getenv('OPENAI_API_KEY')
        if openai_key:
            self.openai_client = OpenAI(api_key=openai_key)
    
    def get_stock_data(self, symbol: str) -> Optional[Dict]:
        """
        Fetch comprehensive stock data using yfinance
        
        Args:
            symbol: Stock ticker symbol (e.g., 'AAPL', 'TSLA')
            
        Returns:
            Dictionary with stock data or None if error
        """
        try:
            stock = yf.Ticker(symbol.upper())
            info = stock.info
            
            # Get historical data for calculations
            hist = stock.history(period="1y")
            
            if hist.empty:
                return None
            
            data = {
                'symbol': symbol.upper(),
                'name': info.get('longName', symbol),
                'current_price': info.get('currentPrice') or info.get('regularMarketPrice'),
                'market_cap': info.get('marketCap'),
                'pe_ratio': info.get('trailingPE'),
                'forward_pe': info.get('forwardPE'),
                'pb_ratio': info.get('priceToBook'),
                'ps_ratio': info.get('priceToSalesTrailing12Months'),
                'peg_ratio': info.get('pegRatio'),
                'dividend_yield': info.get('dividendYield'),
                'eps': info.get('trailingEps'),
                'revenue': info.get('totalRevenue'),
                'profit_margin': info.get('profitMargins'),
                'debt_to_equity': info.get('debtToEquity'),
                'roe': info.get('returnOnEquity'),
                'roa': info.get('returnOnAssets'),
                'beta': info.get('beta'),
                '52w_high': info.get('fiftyTwoWeekHigh'),
                '52w_low': info.get('fiftyTwoWeekLow'),
                'avg_volume': info.get('averageVolume'),
                'sector': info.get('sector'),
                'industry': info.get('industry'),
                'recommendation': info.get('recommendationKey'),
                'target_price': info.get('targetMeanPrice'),
                'analyst_count': info.get('numberOfAnalystOpinions'),
                
                # Historical data
                'history': hist,
                '52w_return': self._calculate_return(hist, 252),  # 252 trading days in a year
                '1m_return': self._calculate_return(hist, 21),
                '1w_return': self._calculate_return(hist, 5),
            }
            
            return data
            
        except Exception as e:
            print(f"Error fetching stock data for {symbol}: {e}")
            return None
    
    def _calculate_return(self, hist: pd.DataFrame, days: int) -> Optional[float]:
        """Calculate percentage return over specified days"""
        try:
            if len(hist) < days:
                return None
            start_price = hist['Close'].iloc[-days]
            end_price = hist['Close'].iloc[-1]
            return ((end_price - start_price) / start_price) * 100
        except:
            return None
    
    def calculate_intrinsic_value(self, data: Dict) -> Optional[Dict]:
        """
        Calculate intrinsic value using multiple valuation methods
        
        Methods:
        1. DCF (Discounted Cash Flow) - simplified
        2. P/E comparison to industry average
        3. Graham Number (value investing)
        4. PEG ratio analysis
        """
        try:
            results = {}
            current_price = data.get('current_price')
            
            if not current_price:
                return None
            
            # 1. P/E Based Valuation
            pe_ratio = data.get('pe_ratio')
            if pe_ratio and pe_ratio > 0:
                # Compare to S&P 500 average P/E (~15-20)
                fair_pe = 18  # Historical average
                eps = data.get('eps', 0)
                if eps > 0:
                    pe_fair_value = eps * fair_pe
                    results['pe_fair_value'] = pe_fair_value
                    results['pe_upside'] = ((pe_fair_value - current_price) / current_price) * 100
            
            # 2. Graham Number (Benjamin Graham's formula)
            eps = data.get('eps')
            book_value = current_price / data.get('pb_ratio', 1) if data.get('pb_ratio') else None
            
            if eps and book_value and eps > 0 and book_value > 0:
                graham_number = (22.5 * eps * book_value) ** 0.5
                results['graham_number'] = graham_number
                results['graham_upside'] = ((graham_number - current_price) / current_price) * 100
            
            # 3. PEG Ratio Analysis (< 1 is undervalued, > 2 is overvalued)
            peg_ratio = data.get('peg_ratio')
            if peg_ratio:
                results['peg_ratio'] = peg_ratio
                results['peg_valuation'] = 'undervalued' if peg_ratio < 1 else 'overvalued' if peg_ratio > 2 else 'fairly valued'
            
            # 4. Price to Book Analysis
            pb_ratio = data.get('pb_ratio')
            if pb_ratio:
                # P/B < 1 often indicates undervaluation
                results['pb_ratio'] = pb_ratio
                results['pb_signal'] = 'undervalued' if pb_ratio < 1 else 'overvalued' if pb_ratio > 3 else 'neutral'
            
            # 5. Analyst Target Price
            target_price = data.get('target_price')
            if target_price:
                results['target_price'] = target_price
                results['target_upside'] = ((target_price - current_price) / current_price) * 100
            
            return results
            
        except Exception as e:
            print(f"Error calculating intrinsic value: {e}")
            return None
    
    def is_undervalued(self, data: Dict, valuation: Dict) -> Tuple[bool, str, float]:
        """
        Determine if stock is undervalued based on multiple factors
        
        Returns:
            (is_undervalued, confidence_level, expected_upside)
        """
        signals = []
        upside_estimates = []
        
        # Check PEG ratio
        if valuation.get('peg_valuation') == 'undervalued':
            signals.append('peg')
            upside_estimates.append(20)  # Conservative estimate
        
        # Check P/E fair value
        pe_upside = valuation.get('pe_upside')
        if pe_upside and pe_upside > 10:
            signals.append('pe')
            upside_estimates.append(pe_upside)
        
        # Check Graham Number
        graham_upside = valuation.get('graham_upside')
        if graham_upside and graham_upside > 15:
            signals.append('graham')
            upside_estimates.append(graham_upside)
        
        # Check P/B ratio
        if valuation.get('pb_signal') == 'undervalued':
            signals.append('pb')
            upside_estimates.append(15)
        
        # Check analyst target
        target_upside = valuation.get('target_upside')
        if target_upside and target_upside > 10:
            signals.append('analyst')
            upside_estimates.append(target_upside)
        
        # Check profitability metrics
        roe = data.get('roe')
        profit_margin = data.get('profit_margin')
        if roe and roe > 0.15 and profit_margin and profit_margin > 0.10:
            signals.append('profitability')
        
        # Determine verdict
        num_signals = len(signals)
        avg_upside = np.mean(upside_estimates) if upside_estimates else 0
        
        if num_signals >= 3:
            return True, 'high', avg_upside
        elif num_signals >= 2:
            return True, 'medium', avg_upside
        elif num_signals >= 1:
            return True, 'low', avg_upside
        else:
            return False, 'none', 0
    
    def generate_recommendation(self, data: Dict, valuation: Dict, is_undervalued: bool, 
                               confidence: str, upside: float) -> str:
        """
        Generate AI-powered recommendation using OpenAI
        Falls back to rule-based recommendation if OpenAI not available
        """
        
        # Prepare analysis summary
        summary = self._prepare_analysis_summary(data, valuation, is_undervalued, confidence, upside)
        
        if self.openai_client:
            try:
                # Use OpenAI to generate natural language recommendation
                prompt = f"""You are a professional stock analyst. Based on the following analysis, 
provide a clear, concise investment recommendation (2-3 paragraphs max).

Stock Analysis:
{summary}

Provide:
1. Clear recommendation (Strong Buy/Buy/Hold/Sell/Strong Sell)
2. Key reasons (2-3 points)
3. Risk factors to consider
4. Target price range if applicable

Keep it professional but conversational."""

                response = self.openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are a professional stock analyst providing investment recommendations."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=500,
                    temperature=0.7
                )
                
                return response.choices[0].message.content
                
            except Exception as e:
                print(f"OpenAI error, falling back to rule-based: {e}")
        
        # Fallback to rule-based recommendation
        return self._generate_rule_based_recommendation(data, valuation, is_undervalued, confidence, upside)
    
    def _prepare_analysis_summary(self, data: Dict, valuation: Dict, 
                                  is_undervalued: bool, confidence: str, upside: float) -> str:
        """Prepare a text summary of the analysis"""
        lines = [
            f"Company: {data['name']} ({data['symbol']})",
            f"Current Price: ${data['current_price']:.2f}",
            f"Sector: {data.get('sector', 'N/A')}",
            f"",
            "Valuation Metrics:",
            f"- P/E Ratio: {data.get('pe_ratio', 'N/A')}",
            f"- P/B Ratio: {data.get('pb_ratio', 'N/A')}",
            f"- PEG Ratio: {data.get('peg_ratio', 'N/A')}",
            f"- ROE: {data.get('roe', 'N/A')}",
            f"",
            f"Undervalued: {'Yes' if is_undervalued else 'No'}",
            f"Confidence: {confidence}",
            f"Expected Upside: {upside:.1f}%",
            f"",
        ]
        
        if valuation.get('target_price'):
            lines.append(f"Analyst Target: ${valuation['target_price']:.2f} ({valuation.get('analyst_count', 0)} analysts)")
        
        return "\n".join(lines)
    
    def _generate_rule_based_recommendation(self, data: Dict, valuation: Dict,
                                           is_undervalued: bool, confidence: str, upside: float) -> str:
        """Generate recommendation using rules when OpenAI is not available"""
        symbol = data['symbol']
        name = data['name']
        price = data['current_price']
        
        if is_undervalued and confidence == 'high' and upside > 20:
            action = "🟢 STRONG BUY"
            reasoning = f"{name} appears significantly undervalued with {upside:.1f}% potential upside."
        elif is_undervalued and confidence in ['high', 'medium'] and upside > 10:
            action = "🟢 BUY"
            reasoning = f"{name} shows good value with {upside:.1f}% potential upside."
        elif is_undervalued and confidence == 'low':
            action = "🟡 HOLD/ACCUMULATE"
            reasoning = f"{name} may be slightly undervalued but with limited confidence."
        else:
            action = "🟡 HOLD"
            reasoning = f"{name} appears fairly valued at current levels."
        
        # Add explanations for metrics
        pe_ratio = data.get('pe_ratio', 'N/A')
        pe_explanation = ""
        if pe_ratio != 'N/A' and pe_ratio:
            if pe_ratio < 15:
                pe_explanation = " (undervalued - stock is cheap)"
            elif pe_ratio > 25:
                pe_explanation = " (expensive - high growth expected)"
            else:
                pe_explanation = " (fairly valued)"
        
        peg_ratio = data.get('peg_ratio', 'N/A')
        peg_explanation = ""
        if peg_ratio != 'N/A' and peg_ratio:
            if peg_ratio < 1:
                peg_explanation = " (undervalued gem!)"
            elif peg_ratio > 2:
                peg_explanation = " (overvalued)"
            else:
                peg_explanation = " (fair)"
        
        roe = data.get('roe', 0)
        roe_explanation = ""
        if roe:
            roe_pct = roe * 100
            if roe_pct > 20:
                roe_explanation = " (excellent profitability!)"
            elif roe_pct > 15:
                roe_explanation = " (good profitability)"
            elif roe_pct > 10:
                roe_explanation = " (decent profitability)"
            else:
                roe_explanation = " (low profitability)"
        
        beta = data.get('beta', 'N/A')
        beta_explanation = ""
        if beta != 'N/A' and beta:
            if beta > 1.5:
                beta_explanation = " (very volatile)"
            elif beta > 1:
                beta_explanation = " (more volatile than market)"
            elif beta < 0.5:
                beta_explanation = " (very stable)"
            else:
                beta_explanation = " (stable)"
        
        recommendation = f"""
**{action}** - {symbol} @ ${price:.2f}

{reasoning}

**Key Metrics Explained:**
• P/E Ratio: {pe_ratio}{pe_explanation}
  (Price/Earnings - How much you pay per $1 of profit. Lower is cheaper.)
  
• PEG Ratio: {peg_ratio}{peg_explanation}
  (P/E adjusted for growth. Under 1.0 is good value.)
  
• ROE: {f"{roe*100:.1f}%" if roe else 'N/A'}{roe_explanation}
  (Return on Equity - How efficiently company uses shareholder money. Higher is better.)
  
• 52-Week Return: {f"{data.get('52w_return', 0):.1f}%" if data.get('52w_return') else 'N/A'}
  (How much stock gained/lost in past year.)

**Risk Assessment:**
• Beta: {beta}{beta_explanation}
  (Volatility vs market. 1.0 = same as market, >1.0 = more risky.)
  
• Debt/Equity: {data.get('debt_to_equity', 'N/A')}
  (How much debt company has. Lower is safer.)

💡 **Disclaimer:** This is for educational purposes only. Always do your own research and consider consulting a financial advisor before investing.
"""
        return recommendation.strip()
    
    def analyze_stock(self, symbol: str) -> str:
        """
        Complete stock analysis pipeline
        Returns formatted analysis with recommendation
        """
        try:
            # 1. Fetch data
            data = self.get_stock_data(symbol)
            if not data:
                return f"❌ Unable to fetch data for {symbol.upper()}. Please check the ticker symbol."
            
            # 2. Calculate valuation
            valuation = self.calculate_intrinsic_value(data)
            if not valuation:
                return f"❌ Unable to calculate valuation for {symbol.upper()}."
            
            # 3. Determine if undervalued
            is_undervalued, confidence, upside = self.is_undervalued(data, valuation)
            
            # 4. Generate recommendation
            recommendation = self.generate_recommendation(data, valuation, is_undervalued, confidence, upside)
            
            return recommendation
            
        except Exception as e:
            return f"❌ Error analyzing {symbol.upper()}: {str(e)}"


# Create singleton instance
stock_analyzer = StockAnalyzer()


def handle_user_message(message: str) -> str:
    """
    Handle incoming user messages
    Analyze stock if message indicates so, otherwise inform about stock focus
    """
    # Simple keyword check for stock analysis intent
    stock_keywords = ['stock', 'buy', 'sell', 'hold', 'analyze', 'recommend']
    
    if any(keyword in message.lower() for keyword in stock_keywords):
        # Extract stock symbol from message (naive approach, improve as needed)
        words = message.split()
        for word in words:
            if len(word) <= 5 and any(char.isdigit() for char in word):  # Simple check for ticker-like word
                return stock_analyzer.analyze_stock(word)
    
    return "I only do stocks. Please provide a stock ticker symbol to analyze."
