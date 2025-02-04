import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta, date
from login_signup import login_signup  # Import login_signup from login_signup.py
import os  # Add this import at the top of the file
import csv  # Ensure this import is present
import matplotlib.pyplot as plt  # Ensure you have this import at the top of your file
from dateutil import parser  # Import dateutil.parser for flexible date parsing
import plotly.graph_objects as go  # Ensure you have this import at the top of your file
from textblob import TextBlob
import time


# File path for user data (login/signup)
USER_DATA_FILE = 'data/users.csv'

# Define the path for collaborative requests
COLLAB_REQUESTS_FILE = 'data/collab_requests.csv'

# Define the path for the portfolio file
PORTFOLIO_FILE = 'data/portfolio.csv'

# Initial setup for virtual balance and portfolio holdings
if "virtual_balance" not in st.session_state:
    st.session_state["virtual_balance"] = 10000000  # Starting balance

if "portfolio_holdings" not in st.session_state:
    st.session_state["portfolio_holdings"] = []  # Empty list to store purchased assets

# Initialize session states with lists for watchlists
if "selected_stock" not in st.session_state:
    st.session_state["selected_stock"] = None
if "selected_crypto" not in st.session_state:
    st.session_state["selected_crypto"] = None
if "active_tab" not in st.session_state:
    st.session_state["active_tab"] = "Stocks"  # Default to Stocks tab
if "stock_watchlist" not in st.session_state:
    st.session_state["stock_watchlist"] = []
if "crypto_watchlist" not in st.session_state or not isinstance(st.session_state["crypto_watchlist"], list):
    st.session_state["crypto_watchlist"] = []
if "portfolio_tab" not in st.session_state:
    st.session_state["portfolio_tab"] = "Stocks"  # Default to Stocks tab in Portfolio

# Check if the user is logged in; otherwise, show login/signup page
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    # Clear the rerun flag if it exists
    if "rerun_flag" in st.session_state:
        del st.session_state["rerun_flag"]
    login_signup()  # Show login/signup page if not logged in
else:
    # Handle rerun flag to simulate rerun behavior
    if "rerun_flag" in st.session_state and st.session_state["rerun_flag"]:
        # Clear the rerun flag and refresh the session state
        del st.session_state["rerun_flag"]
        st.query_params = {}  # Simulate a rerun by resetting query parameters

    # Define the main app logic
    def main():
        st.title("Main App Content")
        st.write(f"Welcome, {st.session_state['username']}!")
    # Function to render the main app pages
    def main():
        st.sidebar.title("Navigation")
        navigation = st.sidebar.radio("Go to", ("Home", "Portfolio", "Watchlist", "Collaborative Investments"))

        if navigation == "Home":
            render_landing_page()
        elif navigation == "Portfolio":
            render_portfolio_page()
        elif navigation == "Watchlist":
            render_watchlist_page()
        elif navigation == "Collaborative Investments":
            st.title("🤝 Collaborative Investments")
            render_collaborative_investment_page()

        # Logout option
        if st.sidebar.button("Logout"):
            st.session_state.clear()  # Clear session state
            st.query_params = {}  # Reset query parameters to simulate rerun

    # Define the landing page function with side-by-side Stocks and Cryptocurrency toggle
    def render_landing_page():
        st.title("Investment Search")
    
        # Display tabs for Stocks and Cryptocurrency side by side
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Stocks", key="stocks_tab"):
                st.session_state["active_tab"] = "Stocks"
        with col2:
            if st.button("Cryptocurrency", key="crypto_tab"):
                st.session_state["active_tab"] = "Cryptocurrency"

        # Display the selected tab's content
        if st.session_state["active_tab"] == "Stocks":
            st.subheader("Stock Search")
            search_query = st.text_input("Search for a stock (Enter ticker or company name)")
            if search_query:
                suggestions = fetch_stock_suggestions(search_query)
                if suggestions:
                    selected_stock = st.selectbox("Select a stock", suggestions)
                    if selected_stock:
                        stock_symbol = selected_stock.split(" - ")[0]
                        display_realtime_stock_chart(stock_symbol)
                        display_stock_analysis(stock_symbol)
                        display_historical_stock_chart_with_indicators(stock_symbol)
                        display_news_sentiment(stock_symbol)
        elif st.session_state["active_tab"] == "Cryptocurrency":
            st.subheader("Cryptocurrency Search")
            crypto_query = st.text_input("Search for a cryptocurrency (Enter symbol or name)")
            if crypto_query:
                suggestions = fetch_crypto_suggestions(crypto_query)
                if suggestions:
                    selected_crypto = st.selectbox("Select a cryptocurrency", suggestions)
                    if selected_crypto:
                        crypto_id = selected_crypto.split(" - ")[0].lower()
                        display_realtime_crypto_chart(crypto_id)
                        display_crypto_analysis(crypto_id)
                        display_historical_crypto_chart_with_indicators(crypto_id)
                        display_news_sentiment(crypto_id)

    


    # Function to add a stock to the watchlist
    def add_stock_to_watchlist(stock_symbol):
        if stock_symbol not in st.session_state["stock_watchlist"]:
            st.session_state["stock_watchlist"].append(stock_symbol)
            st.success(f"{stock_symbol} added to your Stocks Watchlist.")

    # Function to add a cryptocurrency to the watchlist
    def add_crypto_to_watchlist(crypto_id):
        if crypto_id not in st.session_state["crypto_watchlist"]:
            st.session_state["crypto_watchlist"].append(crypto_id)
            st.success(f"{crypto_id} added to your Crypto Watchlist.")

    # Function to fetch stock suggestions from Tiingo API
    def fetch_stock_suggestions(query):
        """
        Fetch stock suggestions based on the user's query from the Tiingo API.

        Args:
            query (str): The search query for stock suggestions.

        Returns:
            list: A list of formatted stock suggestions in the format "ticker - name".
        """
        url = "https://api.tiingo.com/tiingo/utilities/search"
        headers = {"Content-Type": "application/json"}
        params = {"query": query, "token": "33cec2d64e242587073ba2c8f14baa6e7a2e3b8c"}  # Replace with your API key

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()  # Raise an error for bad responses
            data = response.json()
            return [f"{item['ticker']} - {item['name']}" for item in data]
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching stock suggestions: {e}")
            return []

    # Function to fetch cryptocurrency suggestions from CoinCap API
    def fetch_crypto_suggestions(query):
        """
        Fetch cryptocurrency suggestions based on the user's query from the CoinCap API.

        Args:
            query (str): The search query for cryptocurrency suggestions.

        Returns:
            list: A list of formatted cryptocurrency suggestions in the format "id - name".
        """
        url = "https://api.coincap.io/v2/assets"
        params = {"search": query}

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()  # Raise an error for bad responses
            data = response.json()["data"]
            return [f"{item['id']} - {item['name']}" for item in data]
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching cryptocurrency suggestions: {e}")
            return []

    # Function to fetch stock data from Tiingo API
    @st.cache_data
    def fetch_stock_data(stock_symbol):
        """
        Fetch stock data from the Tiingo API.

        Args:
            stock_symbol (str): The stock symbol to fetch data for.

        Returns:
            dict: A dictionary containing stock data such as last price, volume, high, low, and timestamp.
        """
        url = f"https://api.tiingo.com/tiingo/daily/{stock_symbol}/prices"
        headers = {"Content-Type": "application/json", "Authorization": "Token 33cec2d64e242587073ba2c8f14baa6e7a2e3b8c"}  # Replace with your API key
        
        response = requests.get(url, headers=headers)
        print(response.status_code, response.text)  # Debug response

        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:  # Check if data is not empty
                return data[0]  # Return the first item
        else:
            st.error(f"Failed to fetch stock data: {response.status_code} - {response.text}")
        
        return None

    # Function to fetch historical stock data
    def fetch_stock_historical_data(stock_symbol, start_date, end_date):
        """
        Fetch historical stock data from Tiingo API.

        Args:
            stock_symbol (str): The stock symbol to fetch data for.
            start_date (datetime): The start date for the data range.
            end_date (datetime): The end date for the data range.

        Returns:
            pd.DataFrame: A DataFrame containing the historical stock data.
        """
        url = f"https://api.tiingo.com/tiingo/daily/{stock_symbol}/prices"
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Token 33cec2d64e242587073ba2c8f14baa6e7a2e3b8c"  # Replace with your valid API key
        }
        params = {
            "startDate": start_date.strftime("%Y-%m-%d"),
            "endDate": end_date.strftime("%Y-%m-%d"),
        }

        try:
            response = requests.get(url, headers=headers, params=params)
            print(f"Response Status: {response.status_code}")  # Debugging log
            print(f"Response Content: {response.text}")  # Debugging log
            response.raise_for_status()  # Raise an error for HTTP responses >= 400
            data = response.json()
            if data:
                historical_data = pd.DataFrame(data)
                historical_data["date"] = pd.to_datetime(historical_data["date"])
                return historical_data[["date", "close", "high", "low", "open", "volume"]]
            else:
                st.warning(f"No historical data available for {stock_symbol} in the specified range.")
                return pd.DataFrame()
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching historical data for {stock_symbol}: {e}")
            return pd.DataFrame()

    # Function to fetch historical cryptocurrency data
    def fetch_crypto_historical_data(crypto_id, start_date, end_date):
        # Ensure start_date and end_date are datetime.datetime objects
        if isinstance(start_date, date):  # Check if start_date is a date object
            start_date = datetime.combine(start_date, datetime.min.time())
        if isinstance(end_date, date):  # Check if end_date is a date object
            end_date = datetime.combine(end_date, datetime.min.time())

        url = f"https://api.coincap.io/v2/assets/{crypto_id}/history"
        params = {
            "interval": "d1",  # Daily interval
            "start": int(start_date.timestamp() * 1000),  # Convert to milliseconds
            "end": int(end_date.timestamp() * 1000),      # Convert to milliseconds
        }
        response = requests.get(url, params=params)

        if response.status_code == 200:
            data = response.json()["data"]
            historical_data = pd.DataFrame(data)
            historical_data['date'] = pd.to_datetime(historical_data['time'], unit='ms')
            historical_data.rename(columns={'priceUsd': 'price'}, inplace=True)
            historical_data = historical_data[['date', 'price']]
            return historical_data
        else:
            st.error("Failed to fetch historical cryptocurrency data.")
            return pd.DataFrame()  # Return empty DataFrame on failure

    # Fetch summary data for a stock
    def fetch_stock_summary(stock_symbol):
        url = f"https://api.tiingo.com/iex?tickers={stock_symbol}&token=33cec2d64e242587073ba2c8f14baa6e7a2e3b8c"  # Replace with your API key
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data:
                data = data[0]  # Assuming the response is a list
                summary = {
                    "lastPrice": round(data.get("last", 0), 2),
                    "prevClose": round(data.get("prevClose", 0), 2),
                    "change": round(data.get("last", 0) - data.get("prevClose", 0), 2),
                    "changePercent": round((data.get("last", 0) - data.get("prevClose", 0)) / data.get("prevClose", 1) * 100, 2),
                    "highPrice": round(data.get("high", 0), 2),
                    "lowPrice": round(data.get("low", 0), 2),
                    "volume": data.get("volume", "N/A"),
                    "marketStatus": "Open" if (datetime.utcnow() - parser.isoparse(data.get("timestamp", "")).replace(tzinfo=None)).seconds < 60 else "Closed"
                }
                return summary
        return None

    # Updated function to display stock analysis with summary and historical data
    def display_stock_analysis(stock_symbol):
        if stock_symbol not in st.session_state:
            # Fetch all necessary data at once and store in session state
            st.session_state[stock_symbol] = {
                "real_time_data": fetch_stock_data(stock_symbol),
                "historical_data": fetch_stock_historical_data(
                    stock_symbol, datetime.today() - timedelta(days=365), datetime.today()  
                ),
            }

        stock_info = st.session_state[stock_symbol]["real_time_data"]

        # Buy option
        investment_amount = st.number_input("Enter amount to invest in this stock:", min_value=0.0, step=100.0)
        if st.button("Buy Stock"):
            if investment_amount > 0 and investment_amount <= st.session_state["virtual_balance"]:
                quantity_purchased = investment_amount / stock_info["close"]
                st.session_state["virtual_balance"] -= investment_amount
                st.session_state["portfolio_holdings"].append({
                    "type": "Stock",
                    "name": stock_symbol,
                    "quantity": quantity_purchased,
                    "purchase_price": stock_info["close"],
                    "investment": investment_amount
                })
                st.success(f"Purchased {quantity_purchased:.2f} shares of {stock_symbol}")
            else:
                st.error("Invalid investment amount or insufficient balance.")

        # Sell option
        sell_quantity = st.number_input("Enter quantity to sell:", min_value=0.0, key=f"{stock_symbol}_sell")
        if st.button("Sell Stock"):
            asset = next((item for item in st.session_state["portfolio_holdings"] if item["name"] == stock_symbol), None)
            if asset and sell_quantity <= asset["quantity"]:
                sale_amount = sell_quantity * stock_info["close"]
                asset["quantity"] -= sell_quantity
                asset["investment"] -= sale_amount
                st.session_state["virtual_balance"] += sale_amount
                st.success(f"Sold {sell_quantity} shares of {stock_symbol} for ${sale_amount:.2f}")
            else:
                st.error("Insufficient quantity to sell.")

        # Add to Watchlist option
        if st.button("Add to Watchlist (Stock)"):
            add_stock_to_watchlist(stock_symbol)

        stock_data = st.session_state[stock_symbol]

        # Historical Data
        if st.checkbox("Show Historical Data"):
            historical_data = stock_data["historical_data"]
            if not historical_data.empty:
                fig, ax = plt.subplots()
                ax.plot(historical_data["date"], historical_data["close"], label="Close Price")
                ax.set_xlabel("Date")
                ax.set_ylabel("Price")
                ax.legend()
                st.pyplot(fig)
            else:
                st.warning("No historical data available.")

    # Function to display cryptocurrency analysis with Buy, Sell, and Watchlist options
    def display_crypto_analysis(crypto_id):
        crypto_info = fetch_crypto_data(crypto_id)
        if crypto_info:

            

            # Buy option
            investment_amount = st.number_input("Enter amount to invest in this cryptocurrency:", min_value=0.0, step=100.0)
            if st.button("Buy Crypto"):
                if investment_amount > 0 and investment_amount <= st.session_state["virtual_balance"]:
                    quantity_purchased = investment_amount / crypto_info["usd"]
                    st.session_state["virtual_balance"] -= investment_amount
                    st.session_state["portfolio_holdings"].append({
                        "type": "Crypto",
                        "name": crypto_info["name"],
                        "quantity": quantity_purchased,
                        "purchase_price": crypto_info["usd"],
                        "investment": investment_amount
                    })
                    st.success(f"Purchased {quantity_purchased:.2f} units of {crypto_info['name']}")
                else:
                    st.error("Invalid investment amount or insufficient balance.")

            # Sell option
            sell_quantity = st.number_input("Enter quantity to sell:", min_value=0.0, key=f"{crypto_id}_sell")
            if st.button("Sell Crypto"):
                asset = next((item for item in st.session_state["portfolio_holdings"] if item["name"] == crypto_info["name"]), None)
                if asset and sell_quantity <= asset["quantity"]:
                    sale_amount = sell_quantity * crypto_info["usd"]
                    asset["quantity"] -= sell_quantity
                    asset["investment"] -= sale_amount
                    st.session_state["virtual_balance"] += sale_amount
                    st.success(f"Sold {sell_quantity} units of {crypto_info['name']} for ${sale_amount:.2f}")
                else:
                    st.error("Insufficient quantity to sell.")

            # Add to Watchlist option
            if st.button("Add to Watchlist (Crypto)"):
                add_crypto_to_watchlist(crypto_id)

    # Updated function to fetch cryptocurrency data from CoinCap API
    def fetch_crypto_data(crypto_name):
        crypto_id = st.session_state["crypto_ids"].get(crypto_name.lower())
        if not crypto_id:
            st.error(f"Cryptocurrency ID not found for {crypto_name}.")
            return None

        url = f"https://api.coincap.io/v2/assets/{crypto_id}"
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an error for bad responses
            data = response.json()["data"]
            crypto_data = {
                "name": data["name"],
                "usd": float(data["priceUsd"]),
                "market_cap_usd": data["marketCapUsd"],
                "volumeUsd24Hr": data["volumeUsd24Hr"],
                "changePercent24Hr": data["changePercent24Hr"]
            }
            return crypto_data
        except requests.exceptions.RequestException as e:
            st.error(f"Failed to fetch cryptocurrency data for {crypto_name}: {e}")
            return None

    # Function to render the portfolio page with two separate views for stocks and crypto
    def render_portfolio_page():
        st.title("📊 Portfolio")
        st.write("This is your portfolio.")
        
        # Display virtual balance
        st.subheader("Virtual Balance")
        st.write(f"**Available Balance:** ${st.session_state.get('virtual_balance', 0):,}")
        
        # Toggle views between Stocks and Crypto holdings
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Stock Holdings"):
                st.session_state["portfolio_tab"] = "Stocks"
        with col2:
            if st.button("Crypto Holdings"):
                st.session_state["portfolio_tab"] = "Crypto"

        # Display Stock Holdings
        if st.session_state.get("portfolio_tab", "Stocks") == "Stocks":
            st.subheader("Stock Holdings")
            stocks_df = pd.DataFrame([asset for asset in st.session_state["portfolio_holdings"] if asset["type"] == "Stock"])
            if not stocks_df.empty:
                stocks_df["current_price"] = stocks_df["name"].apply(lambda x: fetch_current_price("Stock", x))
                stocks_df["total_value"] = stocks_df["quantity"] * stocks_df["purchase_price"]
                stocks_df["profit_loss"] = stocks_df["total_value"] - stocks_df["investment"]
                # Reset index to start from 1
                stocks_df.index = range(1, len(stocks_df) + 1)  # Start index from 1
                st.dataframe(stocks_df[["name", "quantity", "purchase_price", "total_value", "profit_loss"]])
            else:
                st.write("No stocks in portfolio.")

        # Display Crypto Holdings
        elif st.session_state.get("portfolio_tab", "Stocks") == "Crypto":
            st.subheader("Crypto Holdings")
            crypto_df = pd.DataFrame([asset for asset in st.session_state["portfolio_holdings"] if asset["type"] == "Crypto"])
            if not crypto_df.empty:
                # Fetch current prices for all crypto assets using the correct IDs
                crypto_df["current_price"] = crypto_df["name"].apply(lambda x: fetch_current_price("Cryptocurrency", x))

                # Filter out rows where current_price is None
                crypto_df = crypto_df[crypto_df["current_price"].notna()]

                # Calculate total value and profit/loss
                crypto_df["total_value"] = crypto_df["quantity"] * crypto_df["current_price"]
                crypto_df["profit_loss"] = crypto_df["total_value"] - crypto_df["investment"]

                # Check for None values and handle them
                crypto_df.fillna({"current_price": 0, "total_value": 0, "profit_loss": 0}, inplace=True)

                # Reset index to start from 1
                crypto_df.index = range(1, len(crypto_df) + 1)  # Start index from 1

                # Display the updated DataFrame
                st.dataframe(crypto_df[["name", "quantity", "purchase_price", "total_value", "profit_loss"]])
            else:
                st.write("No cryptocurrencies in portfolio.")

    # Function to render the watchlist page with side-by-side Stocks and Crypto tabs
    def render_watchlist_page():
        st.title("🔍 Watchlist")

        # Display tabs for Stocks Watchlist and Crypto Watchlist side by side
        col1, col2 = st.columns(2)
        with col1:
            show_stocks_watchlist = st.button("Stocks Watchlist")
        with col2:
            show_crypto_watchlist = st.button("Crypto Watchlist")

        # Display Stocks Watchlist
        if show_stocks_watchlist:
            st.subheader("Stocks Watchlist")
            if st.session_state.get("stock_watchlist"):  # Use get to avoid KeyError
                for stock in st.session_state["stock_watchlist"]:
                    stock_info = fetch_stock_data(stock)
                    if stock_info:
                        st.write(f"**{stock}** - Current Price: ${stock_info['close']:.2f}")
                    else:
                        st.warning(f"Could not fetch data for {stock}.")
            else:
                st.write("Your Stocks Watchlist is empty.")

        # Display Crypto Watchlist
        elif show_crypto_watchlist:
            st.subheader("Crypto Watchlist")
            if st.session_state.get("crypto_watchlist"):  # Use get to avoid KeyError
                for crypto in st.session_state["crypto_watchlist"]:
                    crypto_info = fetch_crypto_data(crypto)
                    if crypto_info:
                        st.write(f"**{crypto_info['name']}** - Current Price: ${crypto_info['usd']:.2f}")
                    else:
                        st.warning(f"Could not fetch data for {crypto}.")
            else:
                st.write("Your Crypto Watchlist is empty.")

    # Function to load user data from CSV
    def load_user_data():
        # Ensure the data directory exists
        os.makedirs(os.path.dirname(USER_DATA_FILE), exist_ok=True)
        
        # Check if the file exists; if not, create it with headers
        if not os.path.exists(USER_DATA_FILE):
            pd.DataFrame(columns=["username", "password"]).to_csv(USER_DATA_FILE, index=False)
        
        return pd.read_csv(USER_DATA_FILE)

    # Function to render collaborative investment page
    def render_collaborative_investment_page():
        st.subheader("Initiate a Collaborative Investment")
        with st.form(key="collab_request_form"):
            # Choose investment type (stock or crypto)
            investment_type = st.selectbox("Investment Type", ["Stock", "Cryptocurrency"])
            
            # Autocomplete field for asset name (stock or crypto symbol)
            asset_query = st.text_input(f"Enter the symbol (e.g., AAPL, BTC)")
            
            # Fetch suggestions based on input
            suggestions = []
            if asset_query:
                if investment_type == "Stock":
                    suggestions = fetch_stock_suggestions(asset_query)
                elif investment_type == "Cryptocurrency":
                    suggestions = fetch_crypto_suggestions(asset_query)

            # Display a selectbox with suggestions if available
            asset_name = st.selectbox("Select a symbol", suggestions) if suggestions else asset_query
            
            # Enter total investment amount and user's contribution
            total_investment = st.number_input("Total Investment Amount", min_value=0.0, step=100.0)
            user_contribution = st.number_input("Your Contribution", min_value=0.0, step=10.0)
            collaborator_contribution = total_investment - user_contribution  # Calculate the collaborator's contribution

            # Enter collaborator's username
            collaborator_username = st.text_input("Enter collaborator's username")

            

            # Submit button
            submit_button = st.form_submit_button(label="Send Request")

            # If form is submitted, save request details
            if submit_button:
                if not asset_name or not collaborator_username:
                    st.error("Please enter both asset name and collaborator's username.")
                elif total_investment <= 0 or user_contribution <= 0:
                    st.error("Investment amount and contribution should be greater than zero.")
                elif user_contribution > total_investment:
                    st.error("Your contribution cannot exceed the total investment amount.")
                else:
                    save_collab_request(
                        st.session_state.get("username"), collaborator_username, 
                        investment_type, asset_name, total_investment, 
                        user_contribution, collaborator_contribution
                    )
                    st.success(f"Request sent to {collaborator_username} for collaborative investment.")

        # Display pending requests
        display_pending_requests(st.session_state.get("username"))

    # Function to save a new collaboration request to the file
    def save_collab_request(requester, collaborator, investment_type, asset_name, total_amount, user_contrib, collab_contrib):
        os.makedirs(os.path.dirname(COLLAB_REQUESTS_FILE), exist_ok=True)
        file_exists = os.path.exists(COLLAB_REQUESTS_FILE)
        with open(COLLAB_REQUESTS_FILE, mode='a', newline='') as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(["requester", "collaborator", "investment_type", "asset_name", "total_amount", "user_contrib", "collab_contrib", "status"])
            writer.writerow([requester, collaborator, investment_type, asset_name, total_amount, user_contrib, collab_contrib, "Pending"])

    # Function to display pending requests for the current user
    def display_pending_requests(username):
        st.subheader("Your Pending Requests")
        if os.path.exists(COLLAB_REQUESTS_FILE):
            with open(COLLAB_REQUESTS_FILE, mode='r') as file:
                reader = csv.DictReader(file)
                pending_requests = [row for row in reader if row["requester"] == username or row["collaborator"] == username]
                if pending_requests:
                    for request in pending_requests:
                        # Extract the contributions from the CSV
                        total_investment = float(request['total_amount'])  # Total investment amount
                        user_contrib = float(request['your_contribution'])  # User's contribution
                        collaborator_contrib = total_investment - user_contrib  # Calculate collaborator's contribution

                        # Display the pending request details
                        st.write(f"**From:** {request['requester']} | **To:** {request['collaborator']}")
                        st.write(f"**Investment Type:** {request['investment_type']} | **Asset:** {request['asset_name']} | **Total Investment:** ${total_investment:.2f}")
                        st.write(f"**Your Contribution:** ${user_contrib:.2f}")
                        st.write(f"**Collaborator Contribution:** ${collaborator_contrib:.2f}")
                        st.write(f"**Status:** {request['status']}")

                        # Only show the button if the status is not "Accepted"
                        if request['status'] != 'Accepted' and request['collaborator'] == username:  # Only show the button to the collaborator
                            unique_key = f"accept_{request['requester']}_{request['collaborator']}_{request['asset_name']}_{request['status']}"
                            if st.button("Accept Investment", key=unique_key):
                                # Check for zero contributions to avoid division by zero
                                total_contribution = user_contrib + collaborator_contrib
                                if total_contribution > 0:
                                    # Add to portfolio using the collaborator's username
                                    add_to_portfolio(request['investment_type'], request['asset_name'].split(" - ")[0], collaborator_contrib / total_contribution if total_contribution > 0 else 0, 1, collaborator_contrib, request['collaborator'])
                                    
                                    # Update the request status to "Accepted"
                                    update_request_status(request['requester'], request['collaborator'], 'Accepted')
                                    
                                    st.success(f"Investment from {request['requester']} accepted!")

                                    # Show Pie chart after acceptance
                                    st.subheader("Investment Breakdown")
                                    pie_data = {
                                        'Your Contribution': user_contrib,
                                        'Collaborator Contribution': collaborator_contrib
                                    }
                                    fig, ax = plt.subplots()
                                    ax.pie(pie_data.values(), labels=pie_data.keys(), autopct='%1.1f%%', startangle=90)
                                    ax.axis('equal')  # Equal aspect ratio ensures the pie chart is circular.
                                    st.pyplot(fig)  # Display the pie chart in Streamlit

                                    # Load the updated portfolio to reflect changes
                                    load_portfolio(request['collaborator'])

                                else:
                                    st.warning("Cannot accept investment: both contributions are zero.")

    # Function to update the status of the request in the CSV file
    def update_request_status(requester, collaborator, new_status):
        # Update the status of the request in the CSV file
        temp_file = 'data/temp_collab_requests.csv'
        with open(COLLAB_REQUESTS_FILE, mode='r') as file, open(temp_file, mode='w', newline='') as temp:
            reader = csv.DictReader(file)
            fieldnames = reader.fieldnames
            writer = csv.DictWriter(temp, fieldnames=fieldnames)
            writer.writeheader()
            
            for row in reader:
                if row['requester'] == requester and row['collaborator'] == collaborator:
                    row['status'] = new_status  # Update the status
                writer.writerow(row)
        
        # Replace the old file with the updated one
        os.replace(temp_file, COLLAB_REQUESTS_FILE)

    # Function to add an asset to the portfolio
    def add_to_portfolio(investment_type, asset_symbol, quantity, purchase_price, investment_amount, username):
        total_value = quantity * purchase_price
        profit_loss = total_value - investment_amount
        os.makedirs(os.path.dirname(PORTFOLIO_FILE), exist_ok=True)
        file_exists = os.path.exists(PORTFOLIO_FILE)
        
        with open(PORTFOLIO_FILE, mode='a', newline='') as file:
            writer = csv.writer(file)
            if not file_exists:
                # Write the header if the file is being created for the first time
                writer.writerow(["username", "type", "name", "quantity", "purchase_price", "investment", "total_value", "profit_loss"])  # Header
            writer.writerow([username, investment_type, asset_symbol, quantity, purchase_price, investment_amount, total_value, profit_loss])

        # Update session state to reflect new portfolio holding
        portfolio_entry = {
            "type": investment_type,
            "name": asset_symbol,
            "quantity": quantity,
            "purchase_price": purchase_price,
            "investment": investment_amount,
            "total_value": total_value,
            "profit_loss": profit_loss
        }
        st.session_state["portfolio_holdings"].append(portfolio_entry)

    # Define the fetch_current_price Function
    def fetch_current_price(investment_type, asset_name):
        if investment_type == "Stock":
            stock_data = fetch_stock_data(asset_name)
            if stock_data:
                return stock_data["close"]
        elif investment_type == "Cryptocurrency":
            crypto_data = fetch_crypto_data(asset_name)
            if crypto_data:
                return crypto_data["usd"]
        return None

    # Load Portfolio Data on Login
    def load_portfolio(username):
        if os.path.exists(PORTFOLIO_FILE):
            portfolio = pd.read_csv(PORTFOLIO_FILE)
            
            # Check if 'username' column exists
            if 'username' in portfolio.columns:
                user_portfolio = portfolio[portfolio["username"] == username].to_dict('records')
                st.session_state["portfolio_holdings"] = user_portfolio
            else:
                st.error("Portfolio file is missing the 'username' column.")
                st.session_state["portfolio_holdings"] = []  # Reset holdings if the structure is incorrect
        else:
            st.error("Portfolio file does not exist. Please ensure it is created properly.")
            st.session_state["portfolio_holdings"] = []

   

    
    # Fetch historical stock data
    def fetch_historical_data(stock_symbol, start_date, end_date):
        url = f"https://api.tiingo.com/tiingo/daily/{stock_symbol}/prices"
        headers = {"Content-Type": "application/json"}
        params = {
            "startDate": start_date.strftime("%Y-%m-%d"),
            "endDate": end_date.strftime("%Y-%m-%d"),
            "token": "33cec2d64e242587073ba2c8f14baa6e7a2e3b8c"  # Replace with your Tiingo API key
        }

        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            if data:
                return pd.DataFrame(data)
        return None

    # Fetch live stock data
    def fetch_live_stock_data(stock_symbol):
        """
        Fetch live stock data from the Tiingo API.

        Args:
            stock_symbol (str): The stock symbol to fetch data for.

        Returns:
            dict: A dictionary containing live stock data such as last price, volume, high, low, and timestamp.
        """
        url = f"https://api.tiingo.com/iex?tickers={stock_symbol}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Token 33cec2d64e242587073ba2c8f14baa6e7a2e3b8c"  # Replace with your API key
        }
        
        response = requests.get(url, headers=headers)
        print(response.status_code, response.text)  # Debug response

        if response.status_code == 200:
            data = response.json()
            if data:
                return {
                    "lastPrice": data[0].get("last", 0),
                    "volume": data[0].get("volume", 0),
                    "high": data[0].get("high", 0),
                    "low": data[0].get("low", 0),
                    "timestamp": data[0].get("timestamp")
                }
        else:
            st.error(f"Failed to fetch live stock data: {response.status_code} - {response.text}")
        
        return None

    # Fetch live cryptocurrency data
    def fetch_live_crypto_data(crypto_id):
        url = f"https://api.coincap.io/v2/assets/{crypto_id}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()["data"]
            if data:
                return {
                    "price": float(data["priceUsd"]),
                    "volume": float(data["volumeUsd24Hr"]),
                    "marketCap": float(data["marketCapUsd"]),
                    "changePercent24Hr": float(data["changePercent24Hr"])
                }
        return None

    # Display real-time stock graph using Plotly
    def display_realtime_stock_chart(stock_symbol):
        st.subheader(f"Real-Time {stock_symbol} Stock Data")
        live_data = fetch_live_stock_data(stock_symbol)

        if live_data:
            st.write(f"**Last Price:** ${live_data['lastPrice']}")
            st.write(f"**High Price:** ${live_data['high']}")
            st.write(f"**Low Price:** ${live_data['low']}")
            st.write(f"**Volume:** {live_data['volume']}")
        else:
            st.error("Failed to fetch live stock data. Please check the stock symbol or API key.")

    # Display real-time cryptocurrency graph using Plotly
    def display_realtime_crypto_chart(crypto_id):
        st.subheader(f"Real-Time {crypto_id.upper()} Data")
        live_data = fetch_live_crypto_data(crypto_id)

        if live_data:
            st.write(f"**Current Price:** ${live_data['price']}")
            st.write(f"**Market Cap:** ${live_data['marketCap']}")
            st.write(f"**24h Volume:** ${live_data['volume']}")
            st.write(f"**24h Change:** {live_data['changePercent24Hr']}%")
        else:
            st.error("Failed to fetch live cryptocurrency data. Please check the crypto ID or API key.")

    # Caching function for historical stock data
    @st.cache_data
    def fetch_historical_data_with_cache(stock_symbol, start_date, end_date):
        """
        Fetch historical stock data with caching to improve efficiency.

        Args:
            stock_symbol (str): The stock symbol to fetch historical data for.
            start_date (datetime): The start date for the historical data.
            end_date (datetime): The end date for the historical data.

        Returns:
            DataFrame: A DataFrame containing historical stock data.
        """
        return fetch_stock_historical_data(stock_symbol, start_date, end_date)

    # Updated function to display historical stock data
    def display_historical_stock_chart_with_indicators(stock_symbol):
        st.subheader(f"{stock_symbol} Historical Data with Technical Indicators")
        end_date = datetime.today().date()
        
        # Add a toggle for selecting the timeframe
        timeframe = st.selectbox("Select Timeframe", ["1 Week", "1 Month", "3 Months", "1 Year"])
        
        # Calculate start date based on selected timeframe
        if timeframe == "1 Week":
            start_date = end_date - timedelta(weeks=1)
        elif timeframe == "1 Month":
            start_date = end_date - timedelta(days=30)
        elif timeframe == "3 Months":
            start_date = end_date - timedelta(days=90)
        else:  # 1 Year
            start_date = end_date - timedelta(days=365)

        if st.button("Show Stock Chart"):
            historical_data = fetch_stock_historical_data(stock_symbol, start_date, end_date)
            
            if not historical_data.empty:
                # Ensure 'close' column is numeric
                historical_data['close'] = pd.to_numeric(historical_data['close'], errors='coerce')
                historical_data.dropna(subset=['close'], inplace=True)

                # Calculate SMA, EMA, and RSI
                historical_data['SMA_20'] = calculate_sma(historical_data, window=20, column='close')
                historical_data['EMA_20'] = calculate_ema(historical_data, window=20, column='close')
                historical_data['RSI'] = calculate_rsi(historical_data, column='close')

                # Plot the main chart with SMA and EMA
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=historical_data['date'], y=historical_data['close'], mode='lines', name='Close Price'))
                fig.add_trace(go.Scatter(x=historical_data['date'], y=historical_data['SMA_20'], mode='lines', name='SMA 20'))
                fig.add_trace(go.Scatter(x=historical_data['date'], y=historical_data['EMA_20'], mode='lines', name='EMA 20'))

                fig.update_layout(title=f"{stock_symbol} Historical Price with SMA and EMA",
                                  xaxis_title="Date", yaxis_title="Price (USD)")
                st.plotly_chart(fig)

                # RSI Chart
                fig_rsi = go.Figure()
                fig_rsi.add_trace(go.Scatter(x=historical_data['date'], y=historical_data['RSI'], mode='lines', name='RSI'))
                fig_rsi.update_layout(title=f"{stock_symbol} RSI", xaxis_title="Date", yaxis_title="RSI")
                st.plotly_chart(fig_rsi)
            else:
                st.error("Failed to fetch historical data.")

    # Caching function for historical cryptocurrency data
    @st.cache_data
    def fetch_historical_crypto_data_with_cache(crypto_id, start_date, end_date):
        """
        Fetch historical cryptocurrency data with caching to improve efficiency.

        Args:
            crypto_id (str): The cryptocurrency ID to fetch historical data for.
            start_date (datetime): The start date for the historical data.
            end_date (datetime): The end date for the historical data.

        Returns:
            DataFrame: A DataFrame containing historical cryptocurrency data.
        """
        return fetch_crypto_historical_data(crypto_id, start_date, end_date)

    # Updated function to display historical cryptocurrency data
    def display_historical_crypto_chart_with_indicators(crypto_id):
        st.subheader(f"{crypto_id.upper()} Historical Data with Technical Indicators")
        end_date = datetime.today().date()
        
        # Add a toggle for selecting the timeframe
        timeframe = st.selectbox("Select Timeframe", ["1 Week", "1 Month", "3 Months", "1 Year"])
        
        # Calculate start date based on selected timeframe
        if timeframe == "1 Week":
            start_date = end_date - timedelta(weeks=1)
        elif timeframe == "1 Month":
            start_date = end_date - timedelta(days=30)
        elif timeframe == "3 Months":
            start_date = end_date - timedelta(days=90)
        else:  # 1 Year
            start_date = end_date - timedelta(days=365)

        if st.button("Show Crypto Chart"):
            historical_data = fetch_crypto_historical_data(crypto_id, start_date, end_date)
            
            if not historical_data.empty:
                # Ensure 'price' column is numeric
                historical_data['price'] = pd.to_numeric(historical_data['price'], errors='coerce')
                historical_data.dropna(subset=['price'], inplace=True)

                # Calculate SMA, EMA, and RSI
                historical_data['SMA_20'] = calculate_sma(historical_data, window=20, column='price')
                historical_data['EMA_20'] = calculate_ema(historical_data, window=20, column='price')
                historical_data['RSI'] = calculate_rsi(historical_data, column='price')

                # Plot the main chart with SMA and EMA
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=historical_data['date'], y=historical_data['price'], mode='lines', name='Price'))
                fig.add_trace(go.Scatter(x=historical_data['date'], y=historical_data['SMA_20'], mode='lines', name='SMA 20'))
                fig.add_trace(go.Scatter(x=historical_data['date'], y=historical_data['EMA_20'], mode='lines', name='EMA 20'))

                fig.update_layout(title=f"{crypto_id.upper()} Historical Price with SMA and EMA",
                                  xaxis_title="Date", yaxis_title="Price (USD)")
                st.plotly_chart(fig)

                # RSI Chart
                fig_rsi = go.Figure()
                fig_rsi.add_trace(go.Scatter(x=historical_data['date'], y=historical_data['RSI'], mode='lines', name='RSI'))
                fig_rsi.update_layout(title=f"{crypto_id.upper()} RSI", xaxis_title="Date", yaxis_title="RSI")
                st.plotly_chart(fig_rsi)
            else:
                st.error("Failed to fetch historical data.")

    # Calculate Simple Moving Average (SMA)
    def calculate_sma(data, window, column='close'):
        """
        Calculate the Simple Moving Average (SMA) for a specified column.
        
        Args:
            data (pd.DataFrame): The historical data.
            window (int): The rolling window for SMA calculation.
            column (str): The column on which to calculate SMA.
        
        Returns:
            pd.Series: The SMA values.
        """
        return data[column].rolling(window=window).mean()

    # Calculate Exponential Moving Average (EMA)
    def calculate_ema(data, window, column='close'):
        """
        Calculate the Exponential Moving Average (EMA) for a specified column.
        
        Args:
            data (pd.DataFrame): The historical data.
            window (int): The rolling window for EMA calculation.
            column (str): The column on which to calculate EMA.
        
        Returns:
            pd.Series: The EMA values.
        """
        return data[column].ewm(span=window, adjust=False).mean()

    # Calculate Relative Strength Index (RSI)
    def calculate_rsi(data, column='close', window=14):
        """
        Calculate the Relative Strength Index (RSI) for a DataFrame.
        
        Args:
            data (pd.DataFrame): DataFrame containing the column for RSI calculation.
            column (str): The column on which to calculate RSI.
            window (int): Lookback window for RSI calculation.
        
        Returns:
            pd.Series: RSI values.
        """
        delta = data[column].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    # Helper Function for News Sentiment
    def fetch_news_sentiment(query):
        """
        Fetch news articles and analyze sentiment for the given query.
        
        Args:
            query (str): The search query (e.g., stock ticker or crypto name).
            
        Returns:
            pd.DataFrame: A DataFrame with article headlines, their sentiment, and publication date.
        """
        # Use the CryptoPanic API with the provided API key
        api_key = "d8d626221d1730e8330e4308c684a8e2283f5a7b"  # Replace with your actual API key
        url = f"https://cryptopanic.com/api/v1/posts/?auth_token={api_key}&currencies={query.lower()}"
        
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)

            # Extract articles
            articles = response.json().get("results", [])
            sentiment_data = []

            for article in articles:
                headline = article.get("title", "")
                # Perform sentiment analysis on the headline
                analysis = TextBlob(headline)
                sentiment = "Positive" if analysis.sentiment.polarity > 0 else "Neutral" if analysis.sentiment.polarity == 0 else "Negative"
                publication_date = article.get("created_at")  # Get the publication date
                sentiment_data.append({"headline": headline, "sentiment": sentiment, "date": publication_date})  # Include date

            # Return as a DataFrame
            return pd.DataFrame(sentiment_data)

        except requests.exceptions.RequestException as e:
            st.error(f"Failed to fetch news articles: {e}")
            return pd.DataFrame()

    # Updated display_news_sentiment Function
    def display_news_sentiment(query):
        st.subheader(f"News Sentiment for {query.upper()}")
        
        if st.button("Analyze News Sentiment"):
            sentiment_df = fetch_news_sentiment(query)
            
            if not sentiment_df.empty:
                # Only keep the pie chart of sentiment distribution
                sentiment_counts = sentiment_df["sentiment"].value_counts()
                
                # Display pie chart of sentiment distribution
                st.write("### Sentiment Distribution:")
                fig, ax = plt.subplots()
                ax.pie(
                    sentiment_counts,
                    labels=sentiment_counts.index,
                    autopct='%1.1f%%',
                    startangle=140
                )
                ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
                st.pyplot(fig)


    def display_sentiment_distribution(sentiment_df):
        """
        Display the sentiment distribution as a pie chart.

        Args:
            sentiment_df (pd.DataFrame): DataFrame containing 'sentiment' column.
        """
        if not sentiment_df.empty:
            # Count sentiments
            sentiment_counts = sentiment_df["sentiment"].value_counts()

            # Plot pie chart
            st.subheader("Sentiment Distribution")
            fig, ax = plt.subplots()
            ax.pie(
                sentiment_counts.values,
                labels=sentiment_counts.index,
                autopct="%1.1f%%",
                startangle=140,
            )
            ax.axis("equal")  # Equal aspect ratio ensures that pie is drawn as a circle
            st.pyplot(fig)
        else:
            st.warning("No sentiment data available to visualize.")

    
            

    def fetch_all_cryptos():
        url = "https://api.coincap.io/v2/assets"
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an error for bad responses
            data = response.json()["data"]
            return {item["name"].lower(): item["id"] for item in data}  # Create a mapping of name to ID
        except requests.exceptions.RequestException as e:
            st.error(f"Failed to fetch cryptocurrency list: {e}")
            return {}

    # Fetch all cryptocurrencies and store in session state
    if "crypto_ids" not in st.session_state:
        st.session_state["crypto_ids"] = fetch_all_cryptos()

    if __name__ == "__main__":
        main()
