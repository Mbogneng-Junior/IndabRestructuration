import pandas as pd


df = pd.read_csv("processed_data.csv", on_bad_lines='skip')

print(df.columns)