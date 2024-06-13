import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor,ExtraTreesRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error
import numpy as np

# Load the dataset
data = pd.read_csv('data/Generated.csv')

# Preprocess the dataset
data = data[data['Gender_Female'] != data['Gender_Male']]
data = data[data['Monthly Total Income'] >= 0]
data = data[data['Monthly Total Expense'] >= 0]
data = data[data['Monthly Total Income'] >= data['Monthly Total Expense']]

# Winsorize - capping outliers to the lower and upper bounds
def percentile_capping(df, cols, from_low_end, from_high_end):
    for col in cols:
        df[col] = np.clip(df[col], df[col].quantile(from_low_end), df[col].quantile(from_high_end))

numeric_columns = ["Monthly Total Income", "Monthly Total Expense"]
percentile_capping(data, numeric_columns, 0.05, 0.05)

# Separate features and target variable
target_column = 'Monthly Total Expense'
X = data.drop(columns=[target_column])
y = data[target_column]

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Feature scaling - Standardization
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)
X_scaled = scaler.transform(X)

# Train the model
model = ExtraTreesRegressor()
model.fit(X_scaled, y)

# Serialize the model and scaler
joblib.dump(model, 'models/expense_forecasting_model.pkl')
joblib.dump(scaler, 'models/scaler.pkl')

# Evaluate the model
y_pred = model.predict(X_test_scaled)
mse = mean_squared_error(y_test, y_pred)
mae = mean_absolute_error(y_test, y_pred)
correlation = np.corrcoef(y_test, y_pred)[0, 1]

print(f"Mean Squared Error (MSE): {mse}")
print(f"Mean Absolute Error (MAE): {mae}")
print(f"Correlation coefficient: {correlation}")
