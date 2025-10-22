# QuickBite Express - Data Quality Report

**Date:** October 22, 2025  
**Analysis Period:** January - September 2025

---

## 📊 Dataset Overview

### Dimension Tables (Master Data)
| Table | Records | Status |
|-------|---------|--------|
| `dim_customer` | 107,776 | ✅ No issues |
| `dim_restaurant` | 19,995 | ✅ No issues |
| `dim_delivery_partner_` | 15,000 | ✅ No issues |
| `dim_menu_item` | 342,671 | ✅ No issues |

### Fact Tables (Transaction Data)
| Table | Records | Status |
|-------|---------|--------|
| `fact_orders` | 149,166 | ⚠️ 3.78% missing delivery_partner_id |
| `fact_order_items` | 342,994 | ✅ No issues |
| `fact_delivery_performance` | 149,166 | ✅ No issues |
| `fact_ratings` | 68,842 | ⚠️ 17 rows with nulls, 16 duplicates |

---

## 🔍 Data Quality Findings

### ✅ POSITIVE FINDINGS

1. **Complete Data Coverage**
   - All dimension tables have zero missing values
   - Most fact tables are complete with no duplicates
   - Data types are appropriate for each column

2. **Time Period Validation**
   - ✅ **Pre-Crisis Period (Jan-May 2025):** 113,806 orders
   - ✅ **Crisis Period (Jun-Sep 2025):** 35,360 orders
   - Dataset covers the full required timeframe (272 days)

3. **Comprehensive Coverage**
   - 107,776 unique customers
   - 19,995 restaurants across 8 cities
   - 15,000 delivery partners
   - 342,671 menu items

### ⚠️ DATA QUALITY ISSUES IDENTIFIED

#### 1. Missing Values in `fact_orders`
- **Issue:** 5,635 orders (3.78%) have missing `delivery_partner_id`
- **Impact:** These orders may be cancelled orders or pickup orders without delivery partners
- **Recommendation:** Investigate if these are cancelled orders or self-pickups

#### 2. Missing Values in `fact_ratings`
- **Issue:** 17 rows (0.02%) have null values across all columns
- **Impact:** Minimal - affects only 0.02% of ratings data
- **Recommendation:** Remove or impute these rows

#### 3. Duplicate Records in `fact_ratings`
- **Issue:** 16 duplicate rows (0.02%) detected
- **Impact:** Could skew rating analysis if not handled
- **Recommendation:** Deduplicate based on business logic (keep latest review_timestamp)

#### 4. City Name Consistency (Potential Issue)
- **Cities Present:** Ahmedabad, Bengaluru, Chennai, Delhi, Hyderabad, Kolkata, Mumbai, Pune
- **Status:** ✅ Consistent naming across all tables
- **Note:** Names like "Bengaluru", "Delhi", and "Mumbai" flagged for potential variations but currently consistent

---

## 📅 Time Period Analysis

### Order Distribution by Month (2025)

| Month | Orders | Period |
|-------|--------|--------|
| January | 23,539 | Pre-Crisis |
| February | 22,667 | Pre-Crisis |
| March | 23,543 | Pre-Crisis |
| April | 21,466 | Pre-Crisis |
| May | 22,591 | Pre-Crisis |
| **June** | **9,293** | **Crisis Start** ⚠️ |
| **July** | **8,818** | **Crisis** ⚠️ |
| **August** | **8,555** | **Crisis** ⚠️ |
| **September** | **8,694** | **Crisis** ⚠️ |

**Key Observation:** Sharp 59% decline in orders from May (22,591) to June (9,293) - clear crisis impact visible.

---

## 🎯 Business Metrics

### Order Performance
- **Total Orders:** 149,166
- **Cancelled Orders:** 11,112 (7.45%)
- **Average Items per Order:** 2.30 items
- **Rating Coverage:** 46.15% of orders have ratings

### Geographic Distribution
**Top 3 Cities by Customer Base:**
1. Bengaluru: 30,281 customers (28.1%)
2. Mumbai: 17,317 customers (16.1%)
3. Delhi: 15,090 customers (14.0%)

---

## 🛠️ Recommended Data Cleaning Actions

### Priority 1 (High)
1. **Investigate Missing `delivery_partner_id`**
   ```python
   # Check if missing delivery_partner_id correlates with cancellations
   missing_partner = fact_orders[fact_orders['delivery_partner_id'].isna()]
   cancellation_rate = missing_partner['is_cancelled'].value_counts()
   ```

2. **Remove Duplicate Ratings**
   ```python
   # Keep most recent rating per order
   fact_ratings_clean = fact_ratings.sort_values('review_timestamp').drop_duplicates(
       subset=['order_id'], keep='last'
   )
   ```

### Priority 2 (Medium)
3. **Handle Null Ratings Records**
   ```python
   # Remove 17 rows with all nulls
   fact_ratings_clean = fact_ratings.dropna(subset=['order_id', 'rating'])
   ```

### Priority 3 (Low)
4. **Standardize Date Formats**
   - Ensure all timestamps are in consistent datetime format
   - Convert `signup_date` from DD-MM-YYYY to datetime objects

5. **Validate Business Logic**
   - Confirm cancelled orders have no delivery_partner_id
   - Validate that all order_ids in fact_order_items exist in fact_orders
   - Check referential integrity across all foreign keys

---

## ✅ Data Readiness Assessment

| Criteria | Status | Notes |
|----------|--------|-------|
| Completeness | ✅ 98% | Only minor missing values |
| Consistency | ✅ Pass | City names are standardized |
| Accuracy | ⚠️ Needs validation | Investigate missing partners |
| Timeliness | ✅ Pass | Covers full analysis period |
| Validity | ✅ Pass | Data types appropriate |
| Uniqueness | ⚠️ Minor issues | 16 duplicate ratings |

**Overall Assessment:** Dataset is **READY FOR ANALYSIS** with minor cleaning required.

---

## 📋 Next Steps

1. ✅ **COMPLETED:** Initial data exploration and quality checks
2. 🔄 **IN PROGRESS:** Document findings in this report
3. ⏭️ **NEXT:** Perform data cleaning (handle duplicates, missing values)
4. ⏭️ **THEN:** Begin exploratory data analysis (EDA)
5. ⏭️ **THEN:** Develop pre-crisis vs crisis comparison analysis

---

*Report generated on October 22, 2025*  
*Script: `data_exploration.py`*
