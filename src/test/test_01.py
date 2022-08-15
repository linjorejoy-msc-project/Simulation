import json
import os
import pandas as pd


json_file_path = os.path.join(
    os.path.abspath("."), "src/data/version_01/motion_data.json"
)
csv_file_path = os.path.join(
    os.path.abspath("."), "src/data/version_02/motion_data_1.csv"
)


with open(json_file_path, mode="r") as json_file:
    json_data = json.load(json_file)
    df = pd.DataFrame.from_dict(json_data, orient="index")
    df.to_csv(
        path_or_buf=csv_file_path,
    )
