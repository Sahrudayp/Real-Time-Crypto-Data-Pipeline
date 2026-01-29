import matplotlib
matplotlib.use('Agg') # This tells Python to run without a GUI window
import pandas as pd
import matplotlib.pyplot as plt

# Load the data
df = pd.read_csv('/home/sahru/airflow_project/bitcoin_prices.csv')
df['Timestamp'] = pd.to_datetime(df['Timestamp'])

# --- Statistics ---
print("--- BITCOIN DATA REPORT ---")
print(f"Total Data Points: {len(df)}")
print(f"Average Price: ${df['Price_USD'].mean():,.2f}")

# --- Visualization ---
plt.figure(figsize=(10, 5))
plt.plot(df['Timestamp'], df['Price_USD'], marker='o', color='b')
plt.title('Bitcoin Price Trend')
plt.xticks(rotation=45)
plt.tight_layout()

# Save the plot
plt.savefig('/home/sahru/airflow_project/btc_trend.png')
print("✅ Success! Check for btc_trend.png now.")
