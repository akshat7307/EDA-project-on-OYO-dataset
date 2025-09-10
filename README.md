# EDA-project-on-OYO-dataset

📝 Problem Statement

OYO wants to understand how their hotels are performing across different cities. They want insights about hotel ratings, prices, discounts, and amenities so that they can improve customer satisfaction and pricing strategy.

# 🎯 Task

Clean and prepare hotel data (ratings, prices, room size, amenities, location).

Build an interactive dashboard to analyze:

Rating distribution (quality of hotels).

Base vs Final price comparison (discounting strategy).

Discount percentage patterns.

Top hotels and city-wise performance.

Popular amenities and categories.

# 🔑 What We Have Done in This Project

Data Loading & Cleaning

Imported raw OYO hotel dataset (JSON format).

Cleaned messy columns (ratings, prices, room sizes, amenities, addresses).

Converted values like “4.5 stars” → numeric rating, “₹1,200” → number.

Extracted city names from addresses and converted amenities into lists.

Calculated new columns like Discount Value and Discount %.

Data Manipulation & Preparation

Removed null/irrelevant values.

Created structured dataset with hotels, ratings, prices, discounts, amenities, and city.

Made dataset analysis-ready.

Exploratory Data Analysis (EDA)

Checked Rating distribution to understand hotel quality.

Compared Base vs Final prices to study discounting.

Analyzed Discount % distribution.

Identified Top 10 Hotels by ratings.

Found Top Cities, Popular Categories, and Most Common Amenities.

Explored correlation between price, rating, discount, and room size.

Dashboard Building (with Streamlit + Plotly)

Created interactive filters (City, Rating range, Amenities).

# Built 2 pages:

Overview → KPIs + Charts on Ratings, Prices, Discounts, Top Hotels.

Deep Dive → City wise, Category wise, Amenities frequency, Correlation heatmap.

All charts are interactive, responsive, and consistent in size.

Added key insights that explain customer satisfaction and pricing strategy.

# 📊 What We Get After Analysis

Majority of hotels are rated between 3.5 – 4.2, showing they are good but not premium.

Final prices are much lower than base prices, meaning OYO uses heavy discounting to attract customers.

Most hotels give 20–40% discounts, but some go beyond 60%, showing aggressive pricing in some cases.

Top 10 hotels with best ratings stand out as premium options.

Some cities have more hotels, while in others OYO’s presence is limited.

Amenities like WiFi, AC, TV are most common, meaning they are customer essentials.
