# Imports
# ===================================
import pandas as pd
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
END_DATE = "2025-01"
STARTING_FUND_SIZE = 162_968_000_000.00

# Load Data
# ===================================
cpi = pd.read_csv("../data/cpi.csv", index_col="date")
market = pd.read_csv("../data/sp500.csv", index_col="date")
market["return"] = market["price"].pct_change().shift(-1)
population = pd.read_csv("../data/population.csv", index_col="date")
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
fund_model["real"] = STARTING_FUND_SIZE

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
fund_model["real_fund_ratio"] = fund_model["real"] / (fund_model["cpi"] * fund_model["retirees"])
fund_model["principal_ratio"] = fund_model["principal"] / fund_model["bau"]

# Graph
# ===================================
fig, axes = plt.subplots(2, 2)

axes[0][0].plot(fund_model.index, fund_model["real"], label="Real")
axes[0][0].plot(fund_model.index, fund_model["target"], label="Target")
axes[0][0].set_xlabel("Date")
axes[0][0].set_ylabel("Fund Value")
axes[0][0].yaxis.set_major_formatter(FuncFormatter(lambda x, pos : f"{x / 1e12:.1f}T"))

axes[0][1].plot(fund_model.index, fund_model["distribution"], label="Distribution")
axes[0][1].plot(fund_model.index, fund_model["principal"], label="Principal")
axes[0][1].plot(fund_model.index, fund_model["bau"], label="BAU")
axes[0][1].set_xlabel("Date")
axes[0][1].set_ylabel("Payment")

axes[1][0].plot(fund_model.index, fund_model["fund_ratio"], label="Fund to Target Ratio")

axes[1][1].plot(fund_model.index, fund_model["principal_ratio"], label="Principal to BAU ratio")

for i, ax in enumerate(axes.flat):
    ax.xaxis.set_major_locator(MaxNLocator(5)) 
    ax.legend()

plt.tight_layout()
plt.show()
