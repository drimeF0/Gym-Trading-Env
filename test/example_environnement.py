import sys  
sys.path.append("./")

import pandas as pd
import numpy as np
import time
from src.gym_trading_env.environments import TradingEnv
from src.gym_trading_env.renderer import Renderer

# Import your datas
df = pd.read_csv("test/data/BTC_USD-Hourly.csv", parse_dates=["date"], index_col= "date")
df.sort_index(inplace= True)
df.dropna(inplace= True)
df.drop_duplicates(inplace=True)

# Generating features
# WARNING : the column names need to contain keyword 'feature' !
df["feature_close"] = df["close"].pct_change()
df["feature_open"] = df["open"]/df["close"]
df["feature_high"] = df["high"]/df["close"]
df["feature_low"] = df["low"]/df["close"]
df["feature_volume"] = df["Volume USD"] / df["Volume USD"].rolling(7*24).max()
df.dropna(inplace= True)


# Create your own reward function with the history object
def reward_function(history):
    print(history.columns)
    return np.log(history["portfolio_valuation", -1] / history["portfolio_valuation", -2]) #log (p_t / p_t-1 )

env = TradingEnv(
        name= "BTCUSD",
        df = df,
        windows= 5,
        positions = [ -1, -0.5, 0, 0.5, 1, 1.5, 2], # From -1 (=full SHORT), to +1 (=full LONG) with 0 = no position
        initial_position = 0, #Initial position
        trading_fees = 0.01/100, # 0.01% per stock buy / sell
        borrow_interest_rate= 0.0003/100, #per timestep (= 1h here)
        reward_function = reward_function,
        portfolio_initial_value = 1000, # in FIAT (here, USD)
    )

# Run the simulation
truncated = False
observation, info = env.reset()
while not truncated:
    action = env.action_space.sample() #OR manually : action = int(input("Action : ")) 
    observation, reward, done, truncated, info = env.step(action)

# Render
env.save_for_render()