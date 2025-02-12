# Imports
# ===================================
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MaxNLocator

def graphPopulation():

    WORK_START_AGE = "20"
    WORK_END_AGE = "64"
    RETIREMENT_START_AGE = "65"
    RETIREMENT_END_AGE = "100"

    population = pd.read_csv("../data/population.csv", index_col="date")
    population["workers"] = population.loc[:,WORK_START_AGE:WORK_END_AGE].sum(axis=1)
    population["retirees"] = population.loc[:, RETIREMENT_START_AGE:RETIREMENT_END_AGE].sum(axis=1)
    population["ratio"] = population["workers"]/population["retirees"]

    fig, axes = plt.subplots(1, 2, figsize=(10, 4))  # Adjust figure size

    # Left Plot: Workers vs Retirees
    axes[0].plot(population["workers"], label="Workers")
    axes[0].plot(population["retirees"], label="Retirees")

    axes[0].set_title("Number of Workers vs Retirees")  # Title
    axes[0].set_ylabel("Population (millions)")  # Y-axis label
    axes[0].yaxis.set_major_formatter(FuncFormatter(lambda x, pos: f"{x / 1e6:.0f}"))

    # Right Plot: Worker-to-Retiree Ratio
    axes[1].plot(population.index, population["ratio"], color="tab:green")

    axes[1].set_title("Worker-to-Retiree Ratio")  # Title
    axes[1].set_ylabel("Ratio")  # Y-axis label

    # Shared X-Axis Formatting
    for i, ax in enumerate(axes.flat):
        
        tick_indices = np.linspace(0, len(population.index) - 1, 7, dtype=int)
        xTicks = [population.index[i] for i in tick_indices]

        ax.set_xticks(xTicks)
        ax.set_xticklabels([label[:4] for label in xTicks])
        ax.set_xlabel("Year")  # X-axis label for both
        ax.legend()  # Add legend for clarity
        ax.grid(True, linestyle="--", alpha=0.5)  # Light grid for better readability


    plt.tight_layout()
    # plt.savefig('graphs/populationGraph.png') 
    plt.show()

def graphCpi():

    cpi = pd.read_csv("../data/cpi.csv", index_col="date")
    INITIAL_FUND_SIZE = 1_000
    cpi["fund"] = INITIAL_FUND_SIZE * cpi["price"][0] / cpi["price"]


    fig, axes = plt.subplots(1, 2, figsize=(10, 4))  # Adjust figure size for readability

    # Left Plot: CPI Price Trend
    axes[0].plot(cpi["price"], label="CPI Price", color="tab:blue")
    axes[0].set_title("CPI Price Over Time")
    axes[0].set_ylabel("Price Index")  # Y-axis label

    # Right Plot: CPI Fund Trend
    axes[1].plot(cpi["fund"], label="CPI Fund", color="tab:green")
    axes[1].set_title("Purchasing Power ($1000) Over Time")
    axes[1].set_ylabel("Purchasing Power")  # Y-axis label


    # Shared X-Axis Formatting
    tick_indices = np.linspace(0, len(cpi.index) - 1, 7, dtype=int)  # 7 evenly spaced ticks
    xTicks = [cpi.index[i] for i in tick_indices]

    for ax in axes.flat:
        ax.set_xticks(xTicks)
        ax.set_xticklabels([label[:4] for label in xTicks])  # Show only the year
        ax.set_xlabel("Year")
        ax.grid(True, linestyle="--", alpha=0.5)  # Light grid for better readability

    plt.tight_layout()
    plt.savefig('graphs/cpiGraph.png') 
    # plt.show()

def graphMarket():

    START_DATE = "1990-01"
    END_DATE = "2025-01"
    RETIREMENT_START_AGE = "65"
    RETIREMENT_END_AGE = "100"

    population = pd.read_csv("../data/population.csv", index_col="date")
    population = population.loc[START_DATE:END_DATE, :]

    population["retirees"] = population.loc[:, RETIREMENT_START_AGE:RETIREMENT_END_AGE].sum(axis=1)
    population["growth"] = population["retirees"]/population["retirees"][0]

    cpi = pd.read_csv("../data/cpi.csv", index_col="date")
    cpi = cpi.loc[START_DATE:END_DATE, :]
    cpi["growth"] = cpi["price"]/cpi["price"][0]

    market = pd.read_csv("../data/sp500.csv", index_col="date")
    market["growth"] = market["price"]/market["price"][0]    

    market["return"] = market["price"].pct_change().shift(-1)
    print(market["return"].mean() * 12)

    fig, ax = plt.subplots(1, 1, figsize=(8, 4))  # Single subplot

    # Plot different growth metrics
    ax.plot(market["growth"], label="Relative Market Growth", color="tab:blue")
    ax.plot(population["growth"], label="Relative Population Growth", color="tab:orange")
    ax.plot(cpi["growth"], label="Relative CPI Growth", color="tab:green")
    ax.plot(population["growth"] * cpi["growth"], label="Combined CPI & Population Growth", color="tab:red")

    # Formatting
    ax.set_title("Relative Growth Over Time")
    ax.set_ylabel("Growth Factor")

    tick_indices = np.linspace(0, len(cpi.index) - 1, 7, dtype=int)  # 7 evenly spaced ticks
    xTicks = [cpi.index[i] for i in tick_indices]
    ax.set_xticks(xTicks)
    ax.set_xticklabels([label[:4] for label in xTicks])  # Show only the year
    ax.set_xlabel("Year")

    ax.legend()  # Add legend for clarity
    ax.grid(True, linestyle="--", alpha=0.5)  # Light grid for better readability

    plt.tight_layout()
    plt.savefig('graphs/marketGraph.png') 
    plt.show()
