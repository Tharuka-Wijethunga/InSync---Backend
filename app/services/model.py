import pandas as pd
from scipy import stats
from sklearn.ensemble import GradientBoostingRegressor, ExtraTreesRegressor, RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.model_selection import GridSearchCV
from sklearn.preprocessing import StandardScaler
import numpy as np
from math import sqrt
from app.database.database import userCollection
import asyncio

async def get_data_from_db():
    cursor = userCollection.find()
    data = await cursor.to_list(length=None)
    df = pd.DataFrame(data)
    df = data.drop('_id', axis=1)  # Drop the MongoDB ID column
    return data

def preprocess_data(data):
    data = data[data['Gender_Female'] != data['Gender_Male']]
    data = data[data['Monthly_Total_Income'] >= 0]
    data = data[data['Monthly_Total_Expense'] >= 0]
    data = data[data['Monthly_Total_Income'] >= data['Monthly_Total_Expense']]

    def percentile_capping(df, cols, from_low_end, from_high_end):
        for col in cols:
            stats.mstats.winsorize(a=df[col], limits=(from_low_end, from_high_end), inplace=True)

    numeric_columns = ["Monthly_Total_Income", "Monthly_Total_Expense"]
    percentile_capping(data, numeric_columns, 0.05, 0.05)

    target_column = 'Monthly_Total_Expense'
    x = data.drop(columns=[target_column])
    y = data[target_column]

    return x, y

async def train_model():
    data = get_data_from_db()
    x, y = preprocess_data(data)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(x)

    # Hyperparameter tuning for GradientBoost
    gb_param_grid = {
        'n_estimators': [100, 200, 300],
        'learning_rate': [0.01, 0.05, 0.1, 0.2],
        'max_depth': [3, 5, 7],
        'min_samples_split': [2, 5, 10],
        'min_samples_leaf': [1, 2, 4]
    }
    # Hyperparameter tuning for ExtraTreesRegressor
    et_param_grid = {
        'n_estimators': [100, 200, 300],
        'max_features': ['auto', 'sqrt', 'log2'],
        'max_depth': [None, 10, 20, 30],
        'min_samples_split': [2, 5, 10],
        'min_samples_leaf': [1, 2, 4]
    }
    # Hyperparameter tuning for RandomForestRegressor
    rf_param_grid = {
        'n_estimators': [100, 200, 300],
        'max_features': ['auto', 'sqrt', 'log2'],
        'max_depth': [None, 10, 20, 30],
        'min_samples_split': [2, 5, 10],
        'min_samples_leaf': [1, 2, 4]
    }

    et_grid_search = GridSearchCV(estimator=ExtraTreesRegressor(), param_grid=et_param_grid, cv=5, n_jobs=-1, verbose=2)
    et_grid_search.fit(X_scaled, y)

    best_et_model = et_grid_search.best_estimator_
    return best_et_model, scaler

# Initialize model and scaler with default values
model, scaler = None, None

async def initialize_model():
    global model, scaler
    model, scaler = await train_model()

# Initialize model at startup
asyncio.create_task(initialize_model())

def make_prediction(input_data):
    input_df = pd.DataFrame(input_data)
    input_scaled = scaler.transform(input_df)
    prediction = model.predict(input_scaled)
    return prediction
