from sklearn.linear_model import LinearRegression
import numpy as np
import pandas as pd

df = pd.read_csv(r"Z:\OneDrive\interesting project\data\data1.csv", header = 0)

X = df.iloc[:, 0:3]
y = df['Level']

regressor = LinearRegression()
model = regressor.fit(X, y)
