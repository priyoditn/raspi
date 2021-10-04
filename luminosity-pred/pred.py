import numpy as np
import pickle
import argparse

lr_model = None

# load model
def load_model(model_path):
    global lr_model
    lr_model = pickle.load(open(model_path, 'rb'))


def infer(light_luminosity, ir_status, ultra_sonic_status, time_of_day):
    prediction = lr_model.predict(np.array([np.array([float(light_luminosity), 
                                                      float(ir_status),
                                                      float(ultra_sonic_status),
                                                      float(time_of_day.replace(":","")), 
                                                      ])]))
    return prediction.tolist()[0]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str)
    args = parser.parse_args()
    print(args.model)
    load_model(args.model)
    print(infer(36, 1, 2345, "07:00:00"))

