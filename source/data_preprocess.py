#DATA SPLIT AND PREPROCESSING
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split


#DATA PREPROCESSING
def preprocess_data(file_path, output_path):
    # Load data
    data = pd.read_csv(file_path)

    # Normalize features
    scaler = MinMaxScaler()
    scaled_features = scaler.fit_transform(data[['distance', 'angle', 'speed', 'chang_angle']])
    data[['distance', 'angle', 'speed', 'chang_angle']] = scaled_features

    # One-hot encode categorical features
    categorical_features = ['shotType', 'lastEvent', 'period', 'non_gardiens_amicaux', 'non_gardiens_adverses']
    data = pd.get_dummies(data, columns=categorical_features, drop_first=True, dtype=int)

    # Save preprocessed data
    data.to_csv(f"{output_path}.csv", index=False)
    print(f"Preprocessed data saved to {output_path}.csv")

    return data

#FEATURE SELECTION AND DATA SPLIT

def data_split(data, features, target):
    X = data[features]
    y = data[target]

    # Split data
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)
    return X_train, X_val, y_train, y_val
