import pandas as pd
import numpy as np

name = "abc"

df = pd.DataFrame(pd.date_range(start="2000-01-06", end="2000-02-04"), columns=["date"])
df.insert(1, "weekday", df["date"].dt.day_name())
df[f"{name}_PX-LAST"] = [20, 20, np.nan, np.nan,
                                                20, 20, 20, 20, 20, np.nan, np.nan,
                                                20, 20, 20, 20, 20, np.nan, np.nan,
                                                20, 20, 20, 20, 20, np.nan, np.nan,
                                                20, 20, 20, 20, 20]
df[f"{name}_start"] = ""
df[f"{name}_end"] = ""

start_check = int(df[(df["weekday"] == "Friday") & (df[f"{name}_PX-LAST"].notnull())].first_valid_index())
df.iloc[start_check, df.columns.get_loc(f"{name}_start")] = "start"
new_i_end = "initial"
manipulate_next_start = False

while start_check != "end of backtest period reached":
    # I look for the next Friday after start_check
    if start_check + 7 < len(df.index):
        for i in range(start_check+1, start_check+8):
            if df.iloc[i]["weekday"] == "Friday":
                break
    elif start_check + 1 == len(df.index):
        i = "end of backtest period reached"
    else:
        for i in range(start_check+1, len(df.index)):
            if df.iloc[i]["weekday"] == "Friday":
                break
            elif i == len(df.index)-1:
                i = "end of backtest period reached"
                break
    if isinstance(i, str):
        break
    # I check if I can trade on that Friday, else I look forward to the next tradeable day
    if manipulate_next_start:
        df.iloc[manipulate_next_start, df.columns.get_loc(f"{name}_end")] = ""
        df.iloc[new_i_start, df.columns.get_loc(f"{name}_start")] = ""
        manipulate_next_start = False
    if pd.notnull(df.iloc[i][f"{name}_PX-LAST"]):
        df.iloc[i, df.columns.get_loc(f"{name}_start")] = "start"
        new_i_start = i
    else:
        new_i_start = i+1
        while new_i_start < len(df.index):
            if pd.notnull(df.iloc[new_i_start][f"{name}_PX-LAST"]):
                break
            new_i_start += 1
        if new_i_start < len(df.index):
            df.iloc[new_i_start, df.columns.get_loc(f"{name}_start")] = "start"
    # I start from that Friday and look back to the last tradeable day (i.e. DO, MI, DI, MO)
    previous_i_end = new_i_end
    for new_i_end in range(i-1, start_check-1, -1):
        if (df.iloc[new_i_end][f"{name}_start"] == "start") & (pd.notnull(df.iloc[new_i_end][f"{name}_PX-LAST"])) & (previous_i_end != "initial"):
            if ((new_i_end - previous_i_end) > 1):
                df.iloc[new_i_end, df.columns.get_loc(f"{name}_start")] = ""
                limited_df = df.iloc[0:new_i_end]
                end_indices = limited_df.index[limited_df[f"{name}_end"] == "end"].tolist()
                next_smaller_index = max(end_indices)
                df.iloc[next_smaller_index, df.columns.get_loc(f"{name}_end")] = ""
            else:
                manipulate_next_start = new_i_end
        if pd.notnull(df.iloc[new_i_end][f"{name}_PX-LAST"]):
            df.iloc[new_i_end, df.columns.get_loc(f"{name}_end")] = "end"
            break
    # Increase counter
    start_check = i




df
