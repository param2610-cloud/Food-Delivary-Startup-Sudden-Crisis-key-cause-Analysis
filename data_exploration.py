"""
QuickBite Express - Data Exploration and Quality Checks
========================================================
This script loads all CSV files and performs comprehensive data quality checks.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Define data directory
DATA_DIR = Path('/home/parambrata-ghosh/Development/Personal/Projects/Food_Delivery_Startup/input/RPC_18_Datasets')

print("=" * 80)
print("QUICKBITE EXPRESS - DATA EXPLORATION & QUALITY CHECKS")
print("=" * 80)
print()

# ============================================================================
# 1. LOAD ALL DATASETS
# ============================================================================
print("📁 LOADING DATASETS...")
print("-" * 80)

datasets = {}
file_names = [
    'dim_customer.csv',
    'dim_delivery_partner_.csv',
    'dim_menu_item.csv',
    'dim_restaurant.csv',
    'fact_delivery_performance.csv',
    'fact_order_items.csv',
    'fact_orders.csv',
    'fact_ratings.csv'
]

for file_name in file_names:
    file_path = DATA_DIR / file_name
    table_name = file_name.replace('.csv', '').replace('_', ' ').title()
    try:
        df = pd.read_csv(file_path)
        datasets[file_name.replace('.csv', '')] = df
        print(f"✅ {table_name}: {len(df):,} rows loaded")
    except FileNotFoundError:
        print(f"❌ {table_name}: File not found")
    except Exception as e:
        print(f"❌ {table_name}: Error - {str(e)}")

print()

# ============================================================================
# 2. BASIC DATA CHECKS - SHAPE, COLUMNS, DTYPES
# ============================================================================
print("=" * 80)
print("📊 BASIC DATA CHECKS")
print("=" * 80)
print()

for table_name, df in datasets.items():
    print(f"\n{'=' * 80}")
    print(f"TABLE: {table_name.upper()}")
    print(f"{'=' * 80}")
    print(f"Shape: {df.shape[0]:,} rows × {df.shape[1]} columns")
    print(f"\nColumn Information:")
    print("-" * 80)
    
    # Create info dataframe
    info_df = pd.DataFrame({
        'Column': df.columns,
        'Data Type': df.dtypes.values,
        'Non-Null Count': [df[col].notna().sum() for col in df.columns],
        'Null Count': [df[col].isna().sum() for col in df.columns],
        'Null %': [f"{(df[col].isna().sum() / len(df) * 100):.2f}%" for col in df.columns]
    })
    print(info_df.to_string(index=False))
    
    print(f"\nMemory Usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")

print()

# ============================================================================
# 3. DATA QUALITY CHECKS
# ============================================================================
print("\n" + "=" * 80)
print("🔍 DATA QUALITY CHECKS")
print("=" * 80)

for table_name, df in datasets.items():
    print(f"\n{'=' * 80}")
    print(f"TABLE: {table_name.upper()}")
    print(f"{'=' * 80}")
    
    # Missing Values Summary
    missing_summary = df.isnull().sum()
    missing_summary = missing_summary[missing_summary > 0].sort_values(ascending=False)
    
    if len(missing_summary) > 0:
        print(f"\n⚠️  MISSING VALUES DETECTED:")
        print("-" * 80)
        for col, count in missing_summary.items():
            pct = (count / len(df)) * 100
            print(f"  • {col}: {count:,} missing ({pct:.2f}%)")
    else:
        print(f"\n✅ NO MISSING VALUES")
    
    # Duplicate Records
    duplicates = df.duplicated().sum()
    print(f"\n🔄 DUPLICATE ROWS: {duplicates:,}")
    
    if duplicates > 0:
        print(f"   ⚠️  {duplicates:,} duplicate rows found ({(duplicates/len(df)*100):.2f}%)")

print()

# ============================================================================
# 4. INCONSISTENT ENTRIES CHECK (Focus on City columns)
# ============================================================================
print("\n" + "=" * 80)
print("🏙️  CITY COLUMN CONSISTENCY CHECK")
print("=" * 80)

tables_with_city = ['dim_customer', 'dim_restaurant', 'dim_delivery_partner_']

for table_name in tables_with_city:
    if table_name in datasets:
        df = datasets[table_name]
        if 'city' in df.columns:
            print(f"\n{table_name.upper()}:")
            print("-" * 80)
            city_values = df['city'].value_counts().sort_index()
            print(city_values.to_string())
            print(f"\nUnique cities: {df['city'].nunique()}")
            
            # Check for potential inconsistencies
            city_list = df['city'].dropna().unique()
            potential_issues = []
            for city in city_list:
                city_lower = str(city).lower().strip()
                if 'bangalore' in city_lower or 'bengaluru' in city_lower or 'blr' in city_lower:
                    potential_issues.append(city)
                elif 'mumbai' in city_lower or 'bombay' in city_lower:
                    potential_issues.append(city)
                elif 'delhi' in city_lower or 'new delhi' in city_lower:
                    potential_issues.append(city)
            
            if potential_issues:
                print(f"\n⚠️  POTENTIAL CITY NAME VARIATIONS DETECTED:")
                for city in set(potential_issues):
                    print(f"   • {city}")

print()

# ============================================================================
# 5. TIME PERIOD VALIDATION
# ============================================================================
print("\n" + "=" * 80)
print("📅 TIME PERIOD VALIDATION")
print("=" * 80)

# Check fact_orders for order_timestamp
if 'fact_orders' in datasets:
    df = datasets['fact_orders']
    print(f"\nFACT_ORDERS - ORDER_TIMESTAMP:")
    print("-" * 80)
    
    if 'order_timestamp' in df.columns:
        # Convert to datetime
        df['order_timestamp'] = pd.to_datetime(df['order_timestamp'], errors='coerce')
        
        print(f"Date Range: {df['order_timestamp'].min()} to {df['order_timestamp'].max()}")
        print(f"Total Days Covered: {(df['order_timestamp'].max() - df['order_timestamp'].min()).days} days")
        
        # Extract month-year
        df['year_month'] = df['order_timestamp'].dt.to_period('M')
        monthly_orders = df['year_month'].value_counts().sort_index()
        
        print(f"\nMonthly Order Distribution:")
        print("-" * 80)
        print(monthly_orders.to_string())
        
        # Check for pre-crisis and crisis periods
        df['month'] = df['order_timestamp'].dt.month
        df['year'] = df['order_timestamp'].dt.year
        
        pre_crisis = df[(df['year'] == 2025) & (df['month'].between(1, 5))]
        crisis = df[(df['year'] == 2025) & (df['month'].between(6, 9))]
        
        print(f"\n📊 PERIOD ANALYSIS (2025):")
        print("-" * 80)
        print(f"Pre-Crisis Period (Jan-May 2025): {len(pre_crisis):,} orders")
        print(f"Crisis Period (Jun-Sep 2025): {len(crisis):,} orders")
        
        if len(pre_crisis) > 0 and len(crisis) > 0:
            print(f"\n✅ Dataset covers both pre-crisis and crisis periods")
        else:
            print(f"\n⚠️  Dataset may not cover all required periods")

# Check dim_customer for signup_date
if 'dim_customer' in datasets:
    df = datasets['dim_customer']
    print(f"\n\nDIM_CUSTOMER - SIGNUP_DATE:")
    print("-" * 80)
    
    if 'signup_date' in df.columns:
        # Try multiple date formats
        df['signup_date'] = pd.to_datetime(df['signup_date'], format='%d-%m-%Y', errors='coerce')
        
        print(f"Date Range: {df['signup_date'].min()} to {df['signup_date'].max()}")
        print(f"Total Days Covered: {(df['signup_date'].max() - df['signup_date'].min()).days} days")

# Check fact_ratings for review_timestamp
if 'fact_ratings' in datasets:
    df = datasets['fact_ratings']
    print(f"\n\nFACT_RATINGS - REVIEW_TIMESTAMP:")
    print("-" * 80)
    
    if 'review_timestamp' in df.columns:
        df['review_timestamp'] = pd.to_datetime(df['review_timestamp'], errors='coerce')
        
        print(f"Date Range: {df['review_timestamp'].min()} to {df['review_timestamp'].max()}")
        print(f"Total Days Covered: {(df['review_timestamp'].max() - df['review_timestamp'].min()).days} days")

print()

# ============================================================================
# 6. KEY STATISTICS SUMMARY
# ============================================================================
print("\n" + "=" * 80)
print("📈 KEY STATISTICS SUMMARY")
print("=" * 80)

print(f"\n🎯 DIMENSION TABLES:")
print("-" * 80)
if 'dim_customer' in datasets:
    print(f"Total Customers: {len(datasets['dim_customer']):,}")
if 'dim_restaurant' in datasets:
    print(f"Total Restaurants: {len(datasets['dim_restaurant']):,}")
if 'dim_delivery_partner_' in datasets:
    print(f"Total Delivery Partners: {len(datasets['dim_delivery_partner_']):,}")
if 'dim_menu_item' in datasets:
    print(f"Total Menu Items: {len(datasets['dim_menu_item']):,}")

print(f"\n🎯 FACT TABLES:")
print("-" * 80)
if 'fact_orders' in datasets:
    orders_df = datasets['fact_orders']
    print(f"Total Orders: {len(orders_df):,}")
    if 'is_cancelled' in orders_df.columns:
        cancelled = orders_df['is_cancelled'].value_counts().get('Y', 0)
        print(f"Cancelled Orders: {cancelled:,} ({(cancelled/len(orders_df)*100):.2f}%)")
if 'fact_order_items' in datasets:
    print(f"Total Order Items: {len(datasets['fact_order_items']):,}")
if 'fact_ratings' in datasets:
    print(f"Total Ratings: {len(datasets['fact_ratings']):,}")
if 'fact_delivery_performance' in datasets:
    print(f"Total Delivery Records: {len(datasets['fact_delivery_performance']):,}")

print()
print("=" * 80)
print("✅ DATA EXPLORATION COMPLETE")
print("=" * 80)
