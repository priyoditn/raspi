from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import numpy as np
import argparse
import datetime
import pickle
import csv

X, y = [], []

def load_dataset(infile):
    global X, y
    with open(infile) as fp:
        reader = csv.DictReader(fp)
        for each_line in reader:
            X.append(np.array([
                float(each_line["light luminosity"]), 
                float(each_line["time of the day"].replace(":","")), 
                float(each_line["proximity"])
                ]))
            y.append(each_line["predicted light luminosity"])
    X = np.array(X)


def train(outfile):
    x_train, x_test,y_train,y_test = train_test_split(X,y,test_size=0.2)
    reg = LinearRegression().fit(x_train, y_train)
    preds = reg.predict(x_test)
    # R-Squared is a statistical measure of fit that indicates how much 
    # variation of a dependent variable is explained by the independent 
    # variable(s) in a regression model.
    r2score = r2_score(y_test, preds)
    root_mean_sqerror = np.sqrt(mean_squared_error(y_test, preds))
    print("R squared score: ", r2score)
    pickle.dump(reg, open(outfile, 'wb'))
    print("Training complete and the model is stored at %s" % outfile)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str)
    parser.add_argument("--output", type=str)
    args = parser.parse_args()
    print(args.input, args.output)
    load_dataset(args.input)
    train(args.output)
