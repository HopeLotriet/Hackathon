# accounts/utils.py

from statsmodels.tsa.holtwinters import ExponentialSmoothing
import pandas as pd

# accounts/utils.py

import pandas as pd

def perform_forecasting_analysis(sales_data):
    # Assuming sales_data is a DataFrame with columns like 'Product', 'quantity_sold', and 'Last Sale Date'

    if sales_data.empty:
        return None  # or handle the case when sales_data is empty

    # Convert 'Last Sale Date' to datetime
    sales_data['Last Sale Date'] = pd.to_datetime(sales_data['Last Sale Date'])

    # Set 'Last Sale Date' as the index
    sales_data.set_index('Last Sale Date', inplace=True)

    # Sort the DataFrame by date (if it's not already sorted)
    sales_data.sort_index(inplace=True)

    # Convert 'quantity_sold' to numeric (if not already)
    sales_data['quantity_sold'] = pd.to_numeric(sales_data['quantity_sold'], errors='coerce')

    # Drop rows with NaN values in 'quantity_sold'
    sales_data.dropna(subset=['quantity_sold'], inplace=True)

    # Calculate the simple moving average for 'quantity_sold'
    sales_data['moving_avg'] = sales_data['quantity_sold'].rolling(window=3).mean()

    # Your forecast is the last observed moving average value
    forecast = sales_data['moving_avg'].iloc[-1]

    # Return the forecast data or any relevant information
    return forecast
