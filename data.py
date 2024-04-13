import pandas as pd

data = {
    "date": ["2022-01-01", "2022-01-02", "2022-01-03", "2022-01-04", "2022-01-05"],
    "value": [1, 2, 3, 4, 5],
}

pd.DataFrame(data).to_csv("data.csv", index=False)
