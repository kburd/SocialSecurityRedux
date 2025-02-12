
import os, requests
import pandas as pd
import numpy as np

def getPopulationData():

    # Fetch and Save Data
    base_url = "https://www.populationpyramid.net/api/pp/840/"
    output_dir = "tmp"
    os.makedirs(output_dir, exist_ok=True)
    
    years = list(range(1950, 2101))
    # for year in years:
    #     response = requests.get(f"{base_url}{year}/?csv=true")
    #     file_path = os.path.join(output_dir, f"{year}.csv")
    #     with open(file_path, "wb") as file:
    #         file.write(response.content)

    # # Combine All Years
    # dfs = []
    # for year in years:
    #     file_path = f"tmp/{year}.csv"
    #     df = pd.read_csv(file_path)
        
    #     df["total"] = df["M"] + df["F"]
    #     df['year'] = year
    #     df_pivot = df.pivot(index='year', columns='Age', values='total').reset_index()
    #     dfs.append(df_pivot)

    #     os.remove(file_path)

    # combined = pd.concat(dfs, ignore_index=True)
    # combined.to_csv("tmp/combined.csv", index=False)

    # Extrapolate Years to Months
    expanded = pd.read_csv("tmp/combined.csv")
    expanded["dates"] = expanded["year"].astype(str) + "-12"
    dates = pd.date_range(start="1950-12-01", end="2100-12-01", freq="MS").strftime("%Y-%m")
    expanded.set_index("dates", inplace=True)
    expanded = expanded.reindex(dates)
    expanded.drop(columns="year", inplace=True)

    # Extrapolate Age Buckets to Singular Ages
    ageGroups = list(expanded.columns)
    for ageGroup in ageGroups:
        if ageGroup == "100+":
            continue
        midpoint = int(ageGroup.split("-")[0]) + 2
        expanded[midpoint] = expanded[ageGroup] // 5
        expanded.drop(columns=ageGroup, inplace=True)

    for i in range(101):  # 0 to 100
        column_name = str(i)
        if column_name not in expanded.columns:
            expanded[column_name] = np.nan

    ordered_columns = sorted(expanded.columns, key=lambda x: int(x) if type(x) is not str else float('inf'))
    expanded = expanded[ordered_columns]


    print(list(expanded.columns))


getPopulationData()