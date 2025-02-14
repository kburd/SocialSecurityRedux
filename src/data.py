
import os, requests
import pandas as pd
import numpy as np

def getPopulationData():

    # Fetch and Save Data
    base_url = "https://www.populationpyramid.net/api/pp/840/"
    output_dir = "tmp"
    os.makedirs(output_dir, exist_ok=True)
    
    years = list(range(1950, 1960))
    for year in years:
        response = requests.get(f"{base_url}{year}/?csv=true")
        file_path = os.path.join(output_dir, f"{year}.csv")
        with open(file_path, "wb") as file:
            file.write(response.content)

    # Combine All Years
    dfs = []
    for year in years:
        file_path = f"tmp/{year}.csv"
        df = pd.read_csv(file_path)
        
        df["total"] = df["M"] + df["F"]
        df['year'] = year
        df_pivot = df.pivot(index='year', columns='Age', values='total').reset_index()
        dfs.append(df_pivot)

        os.remove(file_path)

    combined = pd.concat(dfs, ignore_index=True)
    combined.to_csv("tmp/combined.csv", index=False)

    # Extrapolate Years to Months
    expanded = pd.read_csv("tmp/combined.csv")
    expanded["date"] = expanded["year"].astype(str) + "-12"
    dates = pd.date_range(start="1950-12-01", end="2100-12-01", freq="MS").strftime("%Y-%m")
    expanded.set_index("date", inplace=True)
    expanded = expanded.reindex(dates)
    expanded.drop(columns="year", inplace=True)
    expanded.interpolate(method="linear", axis=0, limit_direction="forward", inplace=True)

    # Extrapolate Age Buckets to Singular Ages
    ageGroups = list(expanded.columns)
    for ageGroup in ageGroups:
        if ageGroup == "100+":
            continue
        midpoint = int(ageGroup.split("-")[0]) + 2
        expanded[midpoint] = expanded[ageGroup] // 5
        expanded.drop(columns=ageGroup, inplace=True)
    
    newColumns = {}
    for i in range(100):
        if i not in expanded.columns:
            newColumns[i] =  np.nan    
    expanded = expanded.join(pd.DataFrame(newColumns, index=expanded.index))

    ordered_columns = sorted(expanded.columns, key=lambda x: int(x) if type(x) is not str else float('inf'))
    expanded = expanded[ordered_columns]
    expanded.interpolate(method="linear", axis=1, limit_direction="forward", inplace=True)

    expanded[0] = 2 * expanded[2] - expanded[4]
    expanded[1] = 2 * expanded[2] - expanded[3]

    # Clean up and Save
    expanded = expanded.round(0)
    expanded = expanded.astype(int)
    expanded.index.name = "date"
    os.remove("tmp/combined.csv")
    expanded.to_csv("data/population.csv")

def manipulateFundBalance():

    file_path = f"tmp/fundBalance.csv"
    df = pd.read_csv(file_path)

    df["balance"] = 1_000_000 * df["reserves"]
    df["date"] = df["year"].astype(str) + "-12"
    df.drop(columns=["year", "income", "expenses", "net", "reserves"], inplace=True)


    df.loc[len(df)] = [2025, np.nan]
    df["balance"] = df["balance"].shift(1)
    df.dropna(inplace=True)

    dates = pd.date_range(start=df.loc[1, "date"], end=df.loc[len(df), "date"], freq="MS").strftime("%Y-%m")
    df.set_index("date", inplace=True)
    df = df.reindex(dates)
    df.index.name = "date"
    df.interpolate(method="linear", axis=0, limit_direction="forward", inplace=True)

    os.remove("tmp/fundBalance.csv")       
    df.to_csv("data/fund.csv")

manipulateFundBalance()