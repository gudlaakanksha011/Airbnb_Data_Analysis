# -*- coding: utf-8 -*-
"""Airbnb_Data_Analysis.ipynb

Original file is located at
    https://colab.research.google.com/drive/1sSM44bTSTrI2m-AsAaDw-cho_B5EhjDX
"""

import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

# Load the datasets verbatim
listings = pd.read_csv('listings.csv')
calendar = pd.read_csv('calendar.csv')
reviews = pd.read_csv('reviews.csv')

# --- DATA CLEANING ---
# Convert prices from strings ($1,234.00) to floats
def clean_price(price_str):
    if pd.isna(price_str):
        return np.nan
    return float(price_str.replace('$', '').replace(',', ''))

listings['price'] = listings['price'].apply(clean_price)
calendar['price'] = calendar['price'].apply(clean_price)

# Convert date columns
calendar['date'] = pd.to_datetime(calendar['date'])

# --- SQL SETUP ---
conn = sqlite3.connect(':memory:')
listings.to_sql('listings', conn, index=False)
calendar.to_sql('calendar', conn, index=False)

# --- ANALYSIS 1: Seasonal Price Trends ---
seasonal_prices = pd.read_sql("""
    SELECT
        strftime('%m', date) as month,
        AVG(price) as avg_price
    FROM calendar
    WHERE price IS NOT NULL
    GROUP BY month
    ORDER BY month
""", conn)

# --- ANALYSIS 2: Neighborhood Price Differences ---
neighborhood_prices = pd.read_sql("""
    SELECT
        neighbourhood_cleansed,
        AVG(price) as avg_price,
        COUNT(*) as listing_count
    FROM listings
    GROUP BY neighbourhood_cleansed
    ORDER BY avg_price DESC
    LIMIT 10
""", conn)

# --- VISUALIZATION ---
plt.figure(figsize=(15, 6))

# Plot 1: Seasonal Trends
plt.subplot(1, 2, 1)
sns.lineplot(data=seasonal_prices, x='month', y='avg_price', marker='o', color='red')
plt.title('Average Reservation Price by Month')
plt.xlabel('Month')
plt.ylabel('Average Price ($)')
plt.grid(True, linestyle='--', alpha=0.6)

# --- DATA CLEANING ---
def clean_price(price_str):
    if pd.isna(price_str): return 0
    return float(str(price_str).replace('$', '').replace(',', ''))

listings['price'] = listings['price'].apply(clean_price)

# --- 1. AMENITY ANALYSIS ---
# Let's see how common amenities affect price
listings['has_wifi'] = listings['amenities'].str.contains('Wireless Internet', case=False, na=False)
listings['has_parking'] = listings['amenities'].str.contains('Free Parking', case=False, na=False)

amenity_impact = listings.groupby('has_wifi')['price'].mean().reset_index()
parking_impact = listings.groupby('has_parking')['price'].mean().reset_index()

# --- 2. HOST SUPERHOST STATUS vs RATING ---
# Does being a superhost lead to better reviews?
superhost_ratings = listings.groupby('host_is_superhost')['review_scores_rating'].mean().reset_index()

# --- 3. CORRELATION OF PROPERTY TYPE ---
property_prices = listings.groupby('property_type')['price'].mean().sort_values(ascending=False).head(10).reset_index()

# --- VISUALIZATION ---
plt.figure(figsize=(15, 10))

# Plot 1: Amenity Impact
plt.subplot(2, 2, 1)
sns.barplot(x=['No Wifi', 'Wifi'], y=amenity_impact['price'], palette='coolwarm')
plt.title('Impact of Wifi on Price')
plt.ylabel('Avg Price ($)')

plt.subplot(2, 2, 2)
sns.barplot(x=['No Free Parking', 'Free Parking'], y=parking_impact['price'], palette='viridis')
plt.title('Impact of Free Parking on Price')
plt.ylabel('Avg Price ($)')

# Plot 2: Top 10 Most Expensive Neighborhoods
plt.subplot(2, 2, 3)
sns.barplot(data=neighborhood_prices, x='avg_price', y='neighbourhood_cleansed', palette='magma')
plt.title('Top 10 Most Expensive Neighborhoods')
plt.xlabel('Average Price ($)')
plt.ylabel('Neighborhood')

plt.tight_layout()
plt.savefig('seattle_airbnb_trends.png')
plt.show()

print("Seasonal Price Summary:")
print(seasonal_prices)
print("\nTop 5 Expensive Neighborhoods:")
print(neighborhood_prices.head())