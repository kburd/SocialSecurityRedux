# Imports
# ===================================
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MaxNLocator
import math

# Constants
# ===================================
AVG_RETURN = .095
AVG_INFLATION = .03
AVG_POP_GROWTH = .015
AVG_VOLATILITY = .18
MARGIN_OF_SAFETY = .00
CPI_MULTIPLIER = 6
REPAYMENT_TIMELINE = 30
WORK_START_AGE = "20"
WORK_END_AGE = "64"
RETIREMENT_START_AGE = "65"
RETIREMENT_END_AGE = "100+"
START_DATE = "1990-01"
END_DATE = "2025-02"

# Load Data
# ===================================
cpi = pd.read_csv("data/cpi.csv", index_col="date")
market = pd.read_csv("data/sp500.csv", index_col="date")
population = pd.read_csv("data/population.csv", index_col="date")
fund = pd.read_csv("data/fund.csv", index_col="date")

# Project Future CPI Data
# ===================================
projection_start_date = cpi.index[-1]
future_dates = pd.date_range(start=cpi.index[-1], end=END_DATE, freq="MS").strftime("%Y-%m")[1:]
future = pd.DataFrame({
    'date': future_dates,
    'cpi': np.zeros(len(future_dates))
}).set_index('date')
future["cpi"] = cpi['cpi'].loc[projection_start_date] * ((1 + AVG_INFLATION/12) ** np.arange(1, len(future_dates)+1))
cpi = pd.concat([cpi, future])

# Project Future Market Data
# ===================================
projection_start_date = market.index[-1]
future_dates = pd.date_range(start=market.index[-1], end=END_DATE, freq="MS").strftime("%Y-%m")[1:]
future = pd.DataFrame({
    'date': future_dates,
    'price': np.zeros(len(future_dates))
}).set_index('date')
adjustedAvgGrowth = AVG_RETURN - (AVG_VOLATILITY ** 2) / 2
future["price"] = market['price'].loc[projection_start_date] * ((1 + adjustedAvgGrowth/12) ** np.arange(1, len(future_dates)+1))
market = pd.concat([market, future])

# Additional Data Processing
# ===================================
market["return"] = market["price"].pct_change().shift(-1)
population["workers"] = population.loc[:,WORK_START_AGE:WORK_END_AGE].sum(axis=1)
population["retirees"] = population.loc[:, RETIREMENT_START_AGE:RETIREMENT_END_AGE].sum(axis=1)

# Initialize Model
# ===================================
TARGET_WITHDRAW_RATE = AVG_RETURN - AVG_INFLATION - AVG_POP_GROWTH - (AVG_VOLATILITY**2)/2 - MARGIN_OF_SAFETY

fund_model = pd.concat([market[["return"]], population[["workers", "retirees"]], cpi], axis=1)
fund_model.sort_index(ascending=True, inplace=True)

fund_model["distribution"] = CPI_MULTIPLIER * fund_model["cpi"]
fund_model["target"] = 12 * fund_model["distribution"] * fund_model["retirees"]/TARGET_WITHDRAW_RATE
fund_model["bau"] = fund_model["distribution"] * fund_model["retirees"] / fund_model["workers"]
fund_model["target_fund_ratio"] = fund_model["target"] / (fund_model["cpi"] * fund_model["retirees"])
fund_model["real"] = fund["balance"]

fund_model = fund_model[START_DATE:END_DATE]

# Simulate Fund Performance
# ===================================

for i, date in enumerate(fund_model.index[:-1]):

    # Calculator Principal
    # ===================================
    totalDistribution = fund_model["distribution"][date] * fund_model["retirees"][date]
    shortfall = max(fund_model["target"][date] - fund_model["real"][date] , 0)   
    principalProposed = (TARGET_WITHDRAW_RATE * shortfall / 12) + shortfall/(REPAYMENT_TIMELINE * 12)

    fund_model.loc[date, "principal"] = min(principalProposed, totalDistribution) / fund_model["workers"][date]

    # Update Fund Real Value
    # ===================================   
    fund_model.loc[fund_model.index[i+1], "real"] = fund_model["real"][date] * (1 + fund_model["return"][date]) - fund_model["distribution"][date] * fund_model["retirees"][date] + fund_model["principal"][date] * fund_model["workers"][date]

fund_model["fund_ratio"] = fund_model["real"] / fund_model["target"]
fund_model["principal_ratio"] = fund_model["principal"] / fund_model["bau"]

# Graph
# ===================================
fig, axes = plt.subplots(2, 2)

axes[0][0].set_title("Fund Balance")
axes[0][0].plot(fund_model.index, fund_model["real"], label="Fund")
axes[0][0].plot(fund_model.index, fund_model["target"], label="Target")
axes[0][0].set_ylabel("Value")
axes[0][0].yaxis.set_major_formatter(FuncFormatter(lambda x, pos : f"{x / 1e12:.1f}T"))

axes[0][1].set_title("Cash Flow")
axes[0][1].plot(fund_model.index, fund_model["distribution"], label="Distribution")
axes[0][1].plot(fund_model.index, fund_model["principal"], label="Principal")
axes[0][1].plot(fund_model.index, fund_model["bau"], label="BAU")
axes[0][1].set_ylabel("Payment Amount")

axes[1][0].set_title("Fund to Target Ratio")
axes[1][0].plot(fund_model.index, fund_model["fund_ratio"], label="Ratio")
axes[1][0].set_ylabel("Ratio")

axes[1][1].set_title("Principle to BAU Ratio")
axes[1][1].plot(fund_model.index, fund_model["principal_ratio"], label="Ratio")
axes[1][1].set_ylabel("Ratio")

for i, ax in enumerate(axes.flat):
    tick_indices = np.linspace(0, len(fund_model.index) - 1, 6, dtype=int) 
    xTicks = [fund_model.index[i] for i in tick_indices]
    ax.set_xticks(xTicks)
    ax.set_xticklabels([label[:4] for label in xTicks]) 
    ax.set_xlabel("Year")
    ax.grid(True, linestyle="--", alpha=0.5) 
    ax.legend()

plt.tight_layout()
# plt.savefig('graphs/output.png') 
plt.show()
