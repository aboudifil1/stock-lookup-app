# Stock Lookup App

A Streamlit web application to search for stock information by ticker symbol.

## Features

- Search for stocks by ticker symbol (e.g., AAPL, TSLA)
- Display comprehensive stock metrics:
  - Company name and CEO
  - Current stock price
  - 52-week low/high
  - EPS (TTM) and P/E (TTM)
  - Investment metrics with color-coded evaluations
  - Analyst recommendations and price targets
  - Recent news articles
  - Buy/Hold/Avoid recommendation based on multiple factors

## Tech Stack

- **Streamlit** - Python web framework
- **Python 3.8+**
- **Finnhub API** - Financial data provider

## Setup

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up your API key:**
   
   Get your free API key from [Finnhub](https://finnhub.io/)
   
   **Option A: Environment variable (recommended)**
   ```bash
   export FINNHUB_API_KEY=your_api_key_here
   ```
   
   **Option B: Streamlit secrets file**
   - Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml`
   - Add your API key to the file:
     ```toml
     FINNHUB_API_KEY = "your_api_key_here"
     ```

3. **Run the Streamlit app:**
   ```bash
   streamlit run app.py
   ```

4. **Open your browser:**
   The app will automatically open at [http://localhost:8501](http://localhost:8501)

## Sharing with Friends

### Local Network Access
If you're on the same network, your friend can access the app at:
```
http://YOUR_IP_ADDRESS:8501
```

To find your IP address:
- **Mac/Linux:** `ifconfig` or `ip addr`
- **Windows:** `ipconfig`

### Cloud Deployment (Recommended)
Deploy for free on Streamlit Cloud:
1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repository
4. Your app will be publicly accessible with a shareable link!

## Project Structure

```
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── .streamlit/
│   ├── config.toml            # Streamlit configuration
│   └── secrets.toml.example   # API key template
└── README.md                  # This file
```

## Error Handling

The app handles:
- Invalid ticker symbols
- Missing API key
- Rate limiting
- Network errors
- Missing data fields

## API Endpoints Used

The app uses the following Finnhub API endpoints:
- `/stock/profile2` - Company profile
- `/stock/metric` - Financial metrics
- `/quote` - Real-time quote
- `/company-news` - Recent news
- `/stock/recommendation` - Analyst recommendations
- `/stock/price-target` - Price targets

## Notes

- Free tier of Finnhub API has rate limits (60 calls/minute)
- Some premium endpoints may require a paid plan
- The app gracefully handles missing data and shows "N/A" when unavailable
