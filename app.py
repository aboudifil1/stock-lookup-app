import streamlit as st
import requests
import os
from datetime import datetime
from typing import Optional, Dict, List, Literal

# Page configuration
st.set_page_config(
    page_title="Stock Lookup",
    page_icon="📈",
    layout="wide"
)

# Types
MetricStatus = Literal['good', 'neutral', 'bad']

def safe_fetch(url: str, endpoint_name: str) -> Dict:
    """Safely fetch and parse JSON from API"""
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 429:
            return {"success": False, "data": None, "rate_limited": True}
        
        if response.status_code in [404, 403]:
            return {"success": False, "data": None, "not_found": True, "forbidden": response.status_code == 403}
        
        if not response.ok:
            return {"success": False, "data": None}
        
        return {"success": True, "data": response.json()}
    except Exception as e:
        st.error(f"Error fetching {endpoint_name}: {str(e)}")
        return {"success": False, "data": None}

def evaluate_pe(pe: float) -> Dict:
    """Evaluate P/E ratio"""
    if pe == 0 or pe != pe:  # NaN check
        return {"value": None, "status": "neutral", "label": "N/A"}
    if pe < 15:
        return {"value": pe, "status": "good", "label": "Under 15"}
    if pe <= 25:
        return {"value": pe, "status": "neutral", "label": "15-25"}
    if pe > 35:
        return {"value": pe, "status": "bad", "label": "Above 35"}
    return {"value": pe, "status": "neutral", "label": "25-35"}

def evaluate_eps(eps: float) -> Dict:
    """Evaluate EPS"""
    if eps == 0 or eps != eps:
        return {"value": None, "status": "neutral", "label": "N/A"}
    if eps > 0:
        return {"value": eps, "status": "good", "label": "Positive"}
    return {"value": eps, "status": "bad", "label": "Negative"}

def evaluate_price_position(price: float, low: float, high: float) -> Dict:
    """Evaluate price position in 52-week range"""
    if price == 0 or low == 0 or high == 0 or high == low:
        return {"value": None, "status": "neutral", "label": "N/A"}
    range_val = high - low
    position = (price - low) / range_val
    if position < 0.25:
        return {"value": position * 100, "status": "neutral", "label": "Bottom 25%"}
    if position <= 0.75:
        return {"value": position * 100, "status": "good", "label": "Middle 50%"}
    return {"value": position * 100, "status": "neutral", "label": "Top 25%"}

def evaluate_analyst(analyst: Optional[Dict]) -> Dict:
    """Evaluate analyst recommendations"""
    if not analyst:
        return {"value": None, "status": "neutral", "label": "N/A"}
    
    strong_buy = analyst.get("strongBuy", 0) or 0
    buy = analyst.get("buy", 0) or 0
    hold = analyst.get("hold", 0) or 0
    sell = analyst.get("sell", 0) or 0
    strong_sell = analyst.get("strongSell", 0) or 0
    
    buy_score = strong_buy * 2 + buy
    sell_score = strong_sell * 2 + sell
    
    if buy_score > sell_score and buy_score > hold:
        return {"value": buy_score, "status": "good", "label": "Buy"}
    if sell_score > buy_score:
        return {"value": sell_score, "status": "bad", "label": "Sell"}
    return {"value": hold, "status": "neutral", "label": "Hold"}

def evaluate_profit_margin(margin: Optional[float]) -> Dict:
    """Evaluate profit margin"""
    if margin is None or margin != margin:
        return {"value": None, "status": "neutral", "label": "N/A"}
    if margin > 15:
        return {"value": margin, "status": "good", "label": "Above 15%"}
    if margin >= 5:
        return {"value": margin, "status": "neutral", "label": "5-15%"}
    return {"value": margin, "status": "bad", "label": "Below 5%"}

def evaluate_debt_to_equity(ratio: Optional[float]) -> Dict:
    """Evaluate debt-to-equity ratio"""
    if ratio is None or ratio != ratio:
        return {"value": None, "status": "neutral", "label": "N/A"}
    if ratio < 0.5:
        return {"value": ratio, "status": "good", "label": "Below 0.5"}
    if ratio <= 1.5:
        return {"value": ratio, "status": "neutral", "label": "0.5-1.5"}
    return {"value": ratio, "status": "bad", "label": "Above 1.5"}

def evaluate_beta(beta: Optional[float]) -> Dict:
    """Evaluate beta"""
    if beta is None or beta != beta:
        return {"value": None, "status": "neutral", "label": "N/A"}
    if 0.5 <= beta <= 1.2:
        return {"value": beta, "status": "good", "label": "0.5-1.2"}
    if 1.2 < beta <= 2.0:
        return {"value": beta, "status": "neutral", "label": "1.2-2.0"}
    if beta > 2.0:
        return {"value": beta, "status": "bad", "label": "Above 2.0"}
    return {"value": beta, "status": "neutral", "label": "Below 0.5"}

def get_status_icon(status: MetricStatus) -> str:
    """Get emoji icon for status"""
    icons = {"good": "✅", "neutral": "⚠️", "bad": "🔴"}
    return icons.get(status, "⚠️")

def get_buy_signal_icon(recommendation: str) -> str:
    """Get emoji icon for buy signal"""
    icons = {"buy": "🟢", "hold": "🟡", "avoid": "🔴"}
    return icons.get(recommendation, "🟡")

def fetch_stock_data(ticker: str, api_key: str) -> Optional[Dict]:
    """Fetch stock data from Finnhub API"""
    normalized_ticker = ticker.upper().strip()
    
    # Calculate date range for news (last 7 days)
    to_date = int(datetime.now().timestamp())
    from_date = to_date - (7 * 24 * 60 * 60)
    
    # Fetch all data in parallel
    profile_result = safe_fetch(
        f"https://finnhub.io/api/v1/stock/profile2?symbol={normalized_ticker}&token={api_key}",
        "profile"
    )
    metric_result = safe_fetch(
        f"https://finnhub.io/api/v1/stock/metric?symbol={normalized_ticker}&metric=all&token={api_key}",
        "metric"
    )
    quote_result = safe_fetch(
        f"https://finnhub.io/api/v1/quote?symbol={normalized_ticker}&token={api_key}",
        "quote"
    )
    news_result = safe_fetch(
        f"https://finnhub.io/api/v1/company-news?symbol={normalized_ticker}&from={from_date}&to={to_date}&token={api_key}",
        "news"
    )
    recommendation_result = safe_fetch(
        f"https://finnhub.io/api/v1/stock/recommendation?symbol={normalized_ticker}&token={api_key}",
        "recommendation"
    )
    price_target_result = safe_fetch(
        f"https://finnhub.io/api/v1/stock/price-target?symbol={normalized_ticker}&token={api_key}",
        "price-target"
    )
    
    # Check for rate limiting
    if any(r.get("rate_limited") for r in [profile_result, metric_result, quote_result]):
        st.error("Rate limit exceeded. Please try again later.")
        return None
    
    # Extract data
    profile_data = profile_result.get("data") if profile_result.get("success") else None
    metric_data = metric_result.get("data", {}).get("metric") if metric_result.get("success") else None
    quote_data = quote_result.get("data") if quote_result.get("success") else None
    
    # Process news
    news_items = []
    if news_result.get("success") and isinstance(news_result.get("data"), list):
        news_items = news_result["data"][:8]
    
    # Process analyst data
    analyst_data = None
    if recommendation_result.get("success") and recommendation_result.get("data"):
        rec_data = recommendation_result["data"]
        if isinstance(rec_data, list) and len(rec_data) > 0:
            latest = rec_data[0]
            analyst_data = {
                "strongBuy": latest.get("strongBuy", 0),
                "buy": latest.get("buy", 0),
                "hold": latest.get("hold", 0),
                "sell": latest.get("sell", 0),
                "strongSell": latest.get("strongSell", 0),
            }
    
    if price_target_result.get("success") and price_target_result.get("data"):
        target = price_target_result["data"]
        if not analyst_data:
            analyst_data = {}
        analyst_data.update({
            "targetHigh": target.get("targetHigh"),
            "targetLow": target.get("targetLow"),
            "targetMean": target.get("targetMean"),
            "targetMedian": target.get("targetMedian"),
        })
    
    if not profile_data and not metric_data and not quote_data:
        st.error("Failed to fetch stock data from all endpoints")
        return None
    
    # Extract metrics
    current_price = quote_data.get("c", 0) if quote_data else 0
    week52_low = metric_data.get("52WeekLow", 0) if metric_data else 0
    week52_high = metric_data.get("52WeekHigh", 0) if metric_data else 0
    pe_ttm = metric_data.get("peTTM", 0) if metric_data else 0
    eps_ttm = metric_data.get("epsTTM", 0) if metric_data else 0
    revenue_growth_yoy = metric_data.get("revenueGrowthYearOverYear") if metric_data else None
    
    profit_margin = None
    if metric_data:
        profit_margin = (
            metric_data.get("profitMargin") or
            metric_data.get("netProfitMargin") or
            metric_data.get("netIncomeMargin") or
            metric_data.get("profitMarginTTM")
        )
    
    debt_to_equity = None
    if metric_data:
        debt_to_equity = (
            metric_data.get("totalDebtToEquity") or
            metric_data.get("debtToEquity") or
            metric_data.get("debtEquityRatio") or
            metric_data.get("totalDebtToEquityRatio")
        )
    
    beta = metric_data.get("beta") if metric_data else None
    price_to_book = (
        metric_data.get("priceToBookRatio") or
        metric_data.get("priceToBook") or
        metric_data.get("pbRatio")
    ) if metric_data else None
    return_on_equity = metric_data.get("roe") if metric_data else None
    
    # Perform evaluations
    pe_eval = evaluate_pe(pe_ttm)
    eps_eval = evaluate_eps(eps_ttm)
    price_pos_eval = evaluate_price_position(current_price, week52_low, week52_high)
    analyst_eval = evaluate_analyst(analyst_data)
    profit_margin_eval = evaluate_profit_margin(profit_margin)
    debt_to_equity_eval = evaluate_debt_to_equity(debt_to_equity)
    beta_eval = evaluate_beta(beta)
    
    # Calculate buy signal
    evaluations = [pe_eval, eps_eval, price_pos_eval, analyst_eval, 
                   profit_margin_eval, debt_to_equity_eval, beta_eval]
    greens = sum(1 for e in evaluations if e["status"] == "good")
    yellows = sum(1 for e in evaluations if e["status"] == "neutral")
    reds = sum(1 for e in evaluations if e["status"] == "bad")
    
    recommendation = "hold"
    if greens >= 5:
        recommendation = "buy"
    elif reds >= 2:
        recommendation = "avoid"
    
    buy_signal = {
        "score": greens - reds,
        "greens": greens,
        "yellows": yellows,
        "reds": reds,
        "recommendation": recommendation,
    }
    
    return {
        "companyName": profile_data.get("name") if profile_data else normalized_ticker,
        "ceoName": profile_data.get("ceo", "N/A") if profile_data else "N/A",
        "currentPrice": current_price,
        "week52Low": week52_low,
        "week52High": week52_high,
        "epsTTM": eps_ttm,
        "peTTM": pe_ttm,
        "news": news_items,
        "analyst": analyst_data,
        "revenueGrowthYoY": revenue_growth_yoy,
        "profitMargin": profit_margin,
        "debtToEquity": debt_to_equity,
        "beta": beta,
        "priceToBook": price_to_book,
        "returnOnEquity": return_on_equity,
        "peEvaluation": pe_eval,
        "epsEvaluation": eps_eval,
        "pricePositionEvaluation": price_pos_eval,
        "analystEvaluation": analyst_eval,
        "profitMarginEvaluation": profit_margin_eval,
        "debtToEquityEvaluation": debt_to_equity_eval,
        "betaEvaluation": beta_eval,
        "buySignal": buy_signal,
    }

# Custom CSS for better styling
st.markdown("""
<style>
    .main {
        background: linear-gradient(to bottom right, #eff6ff, #e0e7ff);
    }
    .stApp {
        background: linear-gradient(to bottom right, #eff6ff, #e0e7ff);
    }
    .stock-card {
        background-color: white;
        padding: 2rem;
        border-radius: 1rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        border: 1px solid #e5e7eb;
        margin-top: 1rem;
    }
    .metric-card {
        background-color: #f9fafb;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #e5e7eb;
        margin-bottom: 0.5rem;
    }
    h1 {
        text-align: center;
        color: #1f2937;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        text-align: center;
        color: #4b5563;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Main UI
st.markdown("<h1>📈 Stock Lookup</h1>", unsafe_allow_html=True)
st.markdown('<p class="subtitle">Search for stock information by ticker symbol</p>', unsafe_allow_html=True)

# Get API key from environment or Streamlit secrets
api_key = os.getenv("FINNHUB_API_KEY")
if not api_key:
    try:
        api_key = st.secrets["FINNHUB_API_KEY"]
    except:
        st.error("⚠️ Please set FINNHUB_API_KEY in your environment variables or Streamlit secrets")
        st.info("💡 You can set it as an environment variable: `export FINNHUB_API_KEY=your_key`")
        st.info("💡 Or create `.streamlit/secrets.toml` with: `FINNHUB_API_KEY = 'your_key'`")
        st.stop()

# Search form
with st.form("stock_search_form"):
    ticker = st.text_input("Enter ticker symbol", placeholder="e.g., AAPL, TSLA", value="").upper()
    submitted = st.form_submit_button("Search", use_container_width=True)

if submitted:
    if not ticker.strip():
        st.error("Please enter a stock ticker")
    else:
        with st.spinner("Loading stock data..."):
            stock_data = fetch_stock_data(ticker.strip(), api_key)
            
            if stock_data:
                # Container for main content
                with st.container():
                    st.markdown('<div class="stock-card">', unsafe_allow_html=True)
                    
                    # Company info
                    st.markdown(f"### {stock_data['companyName']}")
                    st.caption(f"CEO: {stock_data['ceoName']}")
                    st.markdown("---")
                    
                    # Key metrics in a grid
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.markdown("**Current Price**")
                        st.markdown(f"<h2 style='color: #1f2937; margin: 0;'>{stock_data['currentPrice']:.2f}</h2>", unsafe_allow_html=True)
                    with col2:
                        st.markdown("**52-Week Low**")
                        st.markdown(f"<h3 style='color: #1f2937; margin: 0;'>{stock_data['week52Low']:.2f}</h3>", unsafe_allow_html=True)
                    with col3:
                        st.markdown("**52-Week High**")
                        st.markdown(f"<h3 style='color: #1f2937; margin: 0;'>{stock_data['week52High']:.2f}</h3>", unsafe_allow_html=True)
                    with col4:
                        st.markdown("**P/E (TTM)**")
                        st.markdown(f"<h3 style='color: #1f2937; margin: 0;'>{stock_data['peTTM']:.2f}</h3>", unsafe_allow_html=True)
                    
                    # Buy Signal
                    buy_signal = stock_data["buySignal"]
                    rec = buy_signal["recommendation"]
                    rec_text = {
                        "buy": "Looks like a BUY",
                        "hold": "HOLD / Do more research",
                        "avoid": "Caution, potential AVOID"
                    }.get(rec, "HOLD")
                    
                    signal_color = {"buy": "🟢", "hold": "🟡", "avoid": "🔴"}.get(rec, "🟡")
                    st.info(f"{signal_color} **{rec_text}** | Score: {buy_signal['greens']} ✅ | {buy_signal['yellows']} ⚠️ | {buy_signal['reds']} 🔴")
                    
                    st.markdown("---")
                    # Investment Metrics
                    st.subheader("Investment Metrics")
                    metrics_col1, metrics_col2 = st.columns(2)
                    
                    with metrics_col1:
                        pe_eval = stock_data["peEvaluation"]
                        status_icon = get_status_icon(pe_eval['status'])
                        st.markdown(f"**P/E Ratio** {status_icon}")
                        st.markdown(f"<h3>{pe_eval['value']:.2f if pe_eval['value'] is not None else 'N/A'}</h3>", unsafe_allow_html=True)
                        st.caption(pe_eval['label'])
                        
                        eps_eval = stock_data["epsEvaluation"]
                        status_icon = get_status_icon(eps_eval['status'])
                        st.markdown(f"**EPS (TTM)** {status_icon}")
                        st.markdown(f"<h3>${eps_eval['value']:.2f if eps_eval['value'] is not None else 'N/A'}</h3>", unsafe_allow_html=True)
                        st.caption(eps_eval['label'])
                        
                        price_pos_eval = stock_data["pricePositionEvaluation"]
                        status_icon = get_status_icon(price_pos_eval['status'])
                        st.markdown(f"**52-Week Position** {status_icon}")
                        st.markdown(f"<h3>{price_pos_eval['value']:.1f}%</h3>" if price_pos_eval['value'] is not None else "<h3>N/A</h3>", unsafe_allow_html=True)
                        st.caption(price_pos_eval['label'])
                        
                        analyst_eval = stock_data["analystEvaluation"]
                        status_icon = get_status_icon(analyst_eval['status'])
                        st.markdown(f"**Analyst Recommendation** {status_icon}")
                        st.markdown(f"<h3>{analyst_eval['label']}</h3>", unsafe_allow_html=True)
                        st.caption(f"Score: {analyst_eval['value']}" if analyst_eval['value'] is not None else "N/A")
                    
                    with metrics_col2:
                        profit_margin_eval = stock_data["profitMarginEvaluation"]
                        status_icon = get_status_icon(profit_margin_eval['status'])
                        st.markdown(f"**Profit Margin** {status_icon}")
                        st.markdown(f"<h3>{profit_margin_eval['value']:.2f}%</h3>" if profit_margin_eval['value'] is not None else "<h3>N/A</h3>", unsafe_allow_html=True)
                        st.caption(profit_margin_eval['label'])
                        
                        debt_to_equity_eval = stock_data["debtToEquityEvaluation"]
                        status_icon = get_status_icon(debt_to_equity_eval['status'])
                        st.markdown(f"**Debt-to-Equity** {status_icon}")
                        st.markdown(f"<h3>{debt_to_equity_eval['value']:.2f if debt_to_equity_eval['value'] is not None else 'N/A'}</h3>", unsafe_allow_html=True)
                        st.caption(debt_to_equity_eval['label'])
                        
                        beta_eval = stock_data["betaEvaluation"]
                        status_icon = get_status_icon(beta_eval['status'])
                        st.markdown(f"**Beta (Volatility)** {status_icon}")
                        st.markdown(f"<h3>{beta_eval['value']:.2f if beta_eval['value'] is not None else 'N/A'}</h3>", unsafe_allow_html=True)
                        st.caption(beta_eval['label'])
                
                    st.markdown("---")
                    # Additional metrics
                    st.subheader("Additional Metrics")
                    add_col1, add_col2, add_col3 = st.columns(3)
                    with add_col1:
                        if stock_data.get("revenueGrowthYoY") is not None:
                            st.markdown("**Revenue Growth (YoY)**")
                            st.markdown(f"<h3>{stock_data['revenueGrowthYoY']:.2f}%</h3>", unsafe_allow_html=True)
                    with add_col2:
                        if stock_data.get("priceToBook") is not None:
                            st.markdown("**Price-to-Book (P/B)**")
                            st.markdown(f"<h3>{stock_data['priceToBook']:.2f}</h3>", unsafe_allow_html=True)
                    with add_col3:
                        if stock_data.get("returnOnEquity") is not None:
                            st.markdown("**Return on Equity (ROE)**")
                            st.markdown(f"<h3>{stock_data['returnOnEquity']:.2f}%</h3>", unsafe_allow_html=True)
                    
                    st.markdown("---")
                    # Analyst Recommendations
                    if stock_data["analyst"]:
                        st.subheader("Analyst Recommendations")
                        analyst = stock_data["analyst"]
                        
                        analyst_col1, analyst_col2 = st.columns(2)
                        with analyst_col1:
                            if analyst.get("targetMean"):
                                st.markdown("**Price Target (Mean)**")
                                st.markdown(f"<h3>${analyst['targetMean']:.2f}</h3>", unsafe_allow_html=True)
                        with analyst_col2:
                            if analyst.get("targetHigh") and analyst.get("targetLow"):
                                st.markdown("**Price Target Range**")
                                st.markdown(f"<h3>${analyst['targetLow']:.2f} - ${analyst['targetHigh']:.2f}</h3>", unsafe_allow_html=True)
                        
                        rec_tags = []
                        if analyst.get("strongBuy", 0) > 0:
                            rec_tags.append(f"Strong Buy: {analyst['strongBuy']}")
                        if analyst.get("buy", 0) > 0:
                            rec_tags.append(f"Buy: {analyst['buy']}")
                        if analyst.get("hold", 0) > 0:
                            rec_tags.append(f"Hold: {analyst['hold']}")
                        if analyst.get("sell", 0) > 0:
                            rec_tags.append(f"Sell: {analyst['sell']}")
                        if analyst.get("strongSell", 0) > 0:
                            rec_tags.append(f"Strong Sell: {analyst['strongSell']}")
                        
                        if rec_tags:
                            st.write(" ".join([f"`{tag}`" for tag in rec_tags]))
                    
                    st.markdown("---")
                    # News
                    if stock_data["news"]:
                        st.subheader("Recent News")
                        for item in stock_data["news"]:
                            with st.expander(item.get("headline", "No headline")):
                                st.write(f"**Source:** {item.get('source', 'Unknown')}")
                                if item.get("datetime"):
                                    dt = datetime.fromtimestamp(item.get("datetime"))
                                    st.write(f"**Date:** {dt.strftime('%B %d, %Y')}")
                                if item.get("summary"):
                                    st.write(item["summary"])
                                if item.get("url"):
                                    st.markdown(f"[Read more]({item['url']})")
                    else:
                        st.subheader("Recent News")
                        st.info("No recent news available")
                    
                    st.markdown('</div>', unsafe_allow_html=True)
