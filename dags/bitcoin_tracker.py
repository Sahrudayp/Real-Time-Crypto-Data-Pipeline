from airflow import DAG
from airflow.decorators import task
from datetime import datetime, timedelta
import requests
import pandas as pd
import os
import logging
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Structured Logging Setup
logger = logging.getLogger("airflow.task")

default_args = {
    'owner': 'sahru',
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='bitcoin_price_tracker',
    default_args=default_args,
    start_date=datetime(2026, 1, 1),
    schedule_interval='@hourly',
    catchup=False
) as dag:

    @task
    def extract_bitcoin_price():
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
        logger.info("Fetching data from CoinGecko API...")
        response = requests.get(url)
        response.raise_for_status()
        price = response.json()['bitcoin']['usd']
        
        # Schema Validation: Ensure price is a valid number
        if not isinstance(price, (int, float)):
            raise ValueError(f"Schema Validation Failed: Expected number, got {type(price)}")
        
        logger.info(f"Successfully extracted price: ${price}")
        return price

    @task
    def load_to_parquet(price):
        # Using Parquet for the Data Lake (Industry Standard)
        file_path = '/home/sahru/airflow_project/bitcoin_data.parquet'
        new_data = pd.DataFrame([{
            'timestamp': datetime.now(),
            'price_usd': float(price),
            'currency': 'USD'
        }])

        if os.path.exists(file_path):
            existing_df = pd.read_parquet(file_path)
            df = pd.concat([existing_df, new_data], ignore_index=True)
            logger.info("Appending to existing Parquet data lake.")
        else:
            df = new_data
            logger.info("Creating new Parquet data lake.")

        # Incremental Loading
        df.to_parquet(file_path, index=False)
        return file_path

    @task
    def generate_visualizations(parquet_path):
        df = pd.read_parquet(parquet_path)
        
        # Analysis & Visualization
        plt.figure(figsize=(10, 5))
        plt.plot(df['timestamp'], df['price_usd'], marker='o', color='tab:blue')
        plt.title('Bitcoin Real-Time Price Analytics')
        plt.grid(True, linestyle='--', alpha=0.7)
        
        output_image = '/home/sahru/airflow_project/btc_trend.png'
        plt.savefig(output_image)
        logger.info(f"Visualization updated at {output_image}")

    # Orchestrated Workflow
    raw_price = extract_bitcoin_price()
    data_lake_path = load_to_parquet(raw_price)
    generate_visualizations(data_lake_path)
