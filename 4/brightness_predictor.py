from sklearn.linear_model import LinearRegression
import numpy as np
import pandas as pd

test_df = pd.read_csv(r"Z:\OneDrive\interesting project\raspi\log_samples\2021-10-17.log", sep='\t', header=0)


row_num = 484

test_df1 = test_df[["Internal Incident Radiation", "Ultrasonic Status", "IR Status"]]

row = test_df1.iloc[row_num, :]

print(row)

external_luminosity = row["Internal Incident Radiation"]
external_luminosity_level = 0

if external_luminosity <= 10:
    external_luminosity_level = 0 # something like pitch black night
elif external_luminosity <= 20:
    external_luminosity_level = 1 # 4 - 6 AM
elif external_luminosity <= 40:
    external_luminosity_level = 2 # 6 - 8 AM
elif external_luminosity <= 60:
    external_luminosity_level = 3 # 8 - 10 AM
elif external_luminosity <= 80:
    external_luminosity_level = 4 # 10 - 12 A/PM
else:
    external_luminosity_level = 5 # 12 - 2 PM
    
distance = row["Ultrasonic Status"]
distance_level = 0

if distance <= 200:
    distance_level = 0
elif distance <= 300:
    distance_level = 1
elif distance <= 400:
    distance_level = 2
elif distance <= 500:
    distance_level = 3
elif distance <= 600:
    distance_level = 4
else:
    distance_level = 5
    
test_row = [external_luminosity_level, distance_level, row["IR Status"]]
test_row = np.array(test_row)
test_row = test_row.reshape(1, -1)

y = model.predict(test_row)
print(f"y from regressor = {y}")
#y = int(round(y[0]))
#print(f"y after rounding = {y}")
output = 10

if y <= 1:
    output = 10
else:
    output = y[0] * 20
# elif y == 2:
#     output = 40
# elif y == 3:
#     output = 60
# elif y == 4:
#     output = 80
# else:
#     output = 100

#output += 20

output = int(round(output))

if output > 100:
    output = 100
elif output < 0:
    output = 0

print(output)