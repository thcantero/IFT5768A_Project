#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler

def preprocess_data(file_path):
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
    data.to_csv("data/preprocessed_data.csv", index=False)
    print("Preprocessed data saved to preprocessed_data.csv")

# Run preprocessing
if __name__ == "__main__":
    preprocess_data('../data/Milestone2_data/Q4_train.csv')