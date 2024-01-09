import pandas as pd
import numpy as np
import os
import datetime


class prepareAsset:

    def __init__(self, name, storage_flag=False):

        assert isinstance(name, str), f"name '{name}' is not a string"
        for file in os.listdir(os.path.join("data","assets_raw")):
            if file.startswith(name):
                self.__full_name = os.path.join(os.path.join("data","assets_raw"), file)
                self.__currency  = self.__full_name.split("_")[-1].split(".")[0]
                df_data = pd.read_csv(self.__full_name, usecols=[1,2])
                df_date = pd.DataFrame(index=pd.date_range(start=df_data.iloc[0]["date"], end="2023-12-31"))

                ###############################################################################
                # for now to prevent the bug DMark-EUR
                if name == "UB1_Comdty":
                    df_date = pd.DataFrame(index=pd.date_range(start="1999-01-01", end="2023-12-31"))
                ###############################################################################

                df_data["date"] = pd.to_datetime(df_data["date"])
                df = df_date.merge(df_data, how="left", left_index=True, right_on="date").reset_index(drop=True)
                df.insert(1, "weekday", df["date"].dt.day_name())
                df = df.rename(columns={"PX_LAST": f"{name}_PX-LAST"})
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
                        if new_i_start < len(df.index):
                            df.iloc[new_i_start, df.columns.get_loc(f"{name}_start")] = ""
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
                    if manipulate_next_start:
                        if new_i_start < len(df.index):
                            df.iloc[new_i_start, df.columns.get_loc(f"{name}_start")] = ""
                        manipulate_next_start = False
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
                # Convert currencies
                if self.__currency == "CHF":
                    df = df.rename(columns={f"{name}_PX-LAST": f"{name}_PX-LAST-CHF"})
                else:
                    for file in os.listdir(os.path.join("data","support")):
                        if file.startswith(self.__currency):
                            df_currency = pd.read_csv(os.path.join("data","support", file), usecols=[1,2])
                            df_currency["date"] = pd.to_datetime(df_currency["date"])
                            df[f"{name}_CURRENCY-{self.__currency}"] = df["date"].map(df_currency.set_index("date")["PX_LAST"])
                            assert all((df.loc[df[f"{name}_PX-LAST"].notna(), f"{name}_CURRENCY-{self.__currency}"].notna())), \
                                f"Not all non-NaN {name}_PX-LAST entries have a corresponding non-NaN {name}_CURRENCY-{self.__currency} entry."
                            if self.__currency in ("JPY", "KRW"):
                                df[f"{name}_PX-LAST-CHF"] = df[f"{name}_PX-LAST"] * df[f"{name}_CURRENCY-{self.__currency}"] / 100
                            else:
                                df[f"{name}_PX-LAST-CHF"] = df[f"{name}_PX-LAST"] * df[f"{name}_CURRENCY-{self.__currency}"]
                            column_order = df.columns.tolist()
                            column_order.insert(3, column_order.pop(column_order.index(f"{name}_CURRENCY-{self.__currency}")))
                            column_order.insert(4, column_order.pop(column_order.index(f"{name}_PX-LAST-CHF")))
                            df = df[column_order]
                # Done
                if storage_flag:
                    df.to_csv(os.path.join("data", "assets", name + ".csv"))
                self.__prices = df
                print("success", self.__full_name)

    def get_attributes(self):
        return self.__full_name, self.__currency, self.__prices


all_assets = [prepareAsset(x, False) for x in ['FB1_Comdty', 'TU1_Comdty', 'FV1_Comdty', 'TY1_Comdty',
                                                                        'WN1_Comdty', 'CV1_Comdty', 'XQ1_Comdty', 'CN1_Comdty',
                                                                        'LGB1_Comdty', 'WB1_Comdty', 'WX1_Comdty', 'G 1_Comdty',
                                                                        'UGL1_Comdty', 'DU1_Comdty', 'OE1_Comdty', 'RX1_Comdty',
                                                                        'UB1_Comdty', 'IK1_Comdty', 'OAT1_Comdty', 'XM1_Comdty',
                                                                        'JB1_Comdty', 'KAA1_Comdty', 'TFT1_Comdty', 'SM1_Index',
                                                                        'ES1_Index', 'PT1_Index', 'VG1_Index', 'Z 1_Index', 'GX1_Index',
                                                                        'ST1_Index', 'CF1_Index', 'OI1_Index', 'QC1_Index', 'ATT1_Index',
                                                                        'BE1_Index', 'EO1_Index', 'OT1_Index', 'XP1_Index', 'TP1_Index',
                                                                        'NI1_Index', 'HI1_Index', 'IH1_Index', 'MES1_Index', 'BZ1_Index',
                                                                        'CL1_Comdty', 'QS1_Comdty', 'XB1_Comdty', 'HO1_Comdty',
                                                                        'NG1_Comdty', 'LMAHDS03 LME_Comdty', 'LMCADS03_Comdty',
                                                                        'LMNIDS03_Comdty', 'GC1_Comdty', 'SI1_Comdty', 'LC1_Comdty',
                                                                        'KC1_Comdty', 'C 1_Comdty', 'CT1_Comdty', 'S 1_Comdty', 'SB1_Comdty',
                                                                        'W 1_Comdty']]

all_assets[0].get_attributes()
