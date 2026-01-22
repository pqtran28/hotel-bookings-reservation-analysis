# Hotel Booking Reservation Analysis & Cancellation Prediction

## Project Overview

This project focuses on analyzing hotel booking data and conduct predictive analysis by building machine learning models to predict booking cancellations. The goal is to understand customer booking behavior, identify key factors that lead to cancellations, and provide a predictive system that can assist hotels in improving revenue management and operational planning.

The project covers the **full data analysis workflow**, including:

* Data cleaning
* Exploratory Data Analysis (EDA)
* Data preprocessing, feature engineering and feature selection
* Training and evaluating multiple machine learning models
* Saving trained models for reuse
* Building an interactive dashboard using **Streamlit**

---

## Project Structure

```
HOTEL-BOOKINGS-RESERVATION-ANALYSIS/
│
├── .streamlit/
│   └── config.toml              # Streamlit configuration
│
├── data/                         # Raw data and data for training and testing models
│
├── preprocessing-and-eda/
│   ├── EDA_insight.ipynb         # Exploratory data analysis & insights
│   └── preprocessing.ipynb      # Data cleaning & preprocessing
│
├── models/
│   ├── LogisticRegression.ipynb  # Logistic Regression training
│   ├── RandomForest.ipynb        # Random Forest training
│   ├── XGBoost.ipynb             # XGBoost training
│   ├── evaluations-on-testset.ipynb # Model evaluation & comparison
│   ├── model_logreg.pkl          # Saved Logistic Regression model
│   ├── model_randomforest.pkl    # Saved Random Forest model
│   └── XGBoost_model.pkl         # Saved XGBoost model
|
├── dashboard.py                  # Streamlit dashboard application
├── data_processed_for_analysis.csv # Data for analysis and dashboard
├── requirements.txt              # Python dependencies
├── README.md                     # Project documentation
└── .gitignore                    # Git ignore rules
```

---

## Exploratory Data Analysis (EDA)

The EDA phase explores:

* Distribution of bookings and cancellations
* Relationship between groups of related features
* Seasonal and temporal booking patterns
* Key features that influence cancellation behavior

Insights from EDA are documented in **`EDA_insight.ipynb`** and guide feature selection for modeling.

---

## Data Preprocessing

Data preprocessing steps include:

* Handling missing values
* Handling outliers and noises
* Encoding categorical variables
* Feature transformation
* Feature engineering
* Removing irrelevant or redundant features (feature selection)

The full preprocessing pipeline is implemented in **`preprocessing.ipynb`**, and the cleaned dataset is saved as:

```
data_processed_for_analysis.csv # for dashboard and exploring insights
# data/ # data for models
```

---

## Machine Learning Models

Multiple models are trained and compared:

* **Logistic Regression** – baseline, interpretable model
* **Random Forest** – ensemble model capturing non-linear relationships
* **XGBoost** – gradient boosting model with high predictive performance

Each model is trained in its own notebook and saved as a `.pkl` file for reuse.

Model evaluation includes:

* Accuracy
* Precision, Recall, F1-score
* ROC-AUC (if applicable)
* Model explainability (SHAP / feature importance visualization / log-odds)

Final comparisons are available in **`evaluations-on-testset.ipynb`**.

---

## Interactive Dashboard

The project includes an interactive **Streamlit dashboard** (`dashboard.py`) that allows users to:

* Explore booking data
* Visualize key metrics
* Here is the link to the dashboard: [Dashboard](https://hotel-bookings-reservation-analysis-ds111.streamlit.app/)
---

## Key Outcomes

* Identified critical factors influencing hotel booking cancellations
* Built and compared multiple ML models
* Deployed a reusable and interactive dashboard
* Established a clean, reproducible ML project structure

---

## Future Improvements

* Handling class imbalance more robustly
* Deployment to cloud platforms (e.g., Streamlit Cloud, Docker)

---

