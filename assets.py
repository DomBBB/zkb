import pandas as pd
import numpy as np
import os
import datetime


class Asset:

    def __init__(self, name, category):

        assert isinstance(name, str), f"name '{name}' is not a string"
        assert isinstance(category, str), f"category '{category}' is not a string"
        self.__name = name
        self.__category = category

        for file in os.listdir(os.path.join("data","assets")):
            if file.startswith(name):
                self.__full_name = os.path.join(os.path.join("data","assets"), file)
                self.__currency  = self.__full_name.split("_")[-1].split(".")[0]
                df = pd.read_csv(self.__full_name)
                df = df.fillna("") # optional for better readability

                """
                # Calculate returns
                df[f"{name}_return"] = ""
                start_index = None
                for index, row in df.iterrows():
                    if row[f"{name}_start"] == "start" and start_index is None:
                        start_index = index
                    elif row[f"{name}_end"] == "end" and start_index is not None:
                        start_price = df.at[start_index, f"{name}_PX-LAST"]
                        end_price = row[f"{name}_PX-LAST"]
                        df.at[index, f"{name}_return"] = (end_price - start_price) / start_price * 100 #in %
                        start_index = None
                """

                print("success", self.__full_name)
                self.__prices = df

    def get_name(self):
        return self.__name

    def get_category(self):
        return self.__category

    def get_full_name(self):
        return self.__full_name

    def get_currency(self):
        return self.__currency

    def get_prices(self):
        return self.__prices


bonds = [Asset(x, "bonds") for x in ['FB1_Comdty', 'TU1_Comdty', 'FV1_Comdty', 'TY1_Comdty',
                                                        'WN1_Comdty', 'CV1_Comdty', 'XQ1_Comdty', 'CN1_Comdty',
                                                        'LGB1_Comdty', 'WB1_Comdty', 'WX1_Comdty', 'G 1_Comdty',
                                                        'UGL1_Comdty', 'DU1_Comdty', 'OE1_Comdty', 'RX1_Comdty',
                                                        'UB1_Comdty', 'IK1_Comdty', 'OAT1_Comdty', 'XM1_Comdty',
                                                        'JB1_Comdty', 'KAA1_Comdty', 'TFT1_Comdty']]

equity = [Asset(x, "equity") for x in ['SM1_Index', 'ES1_Index', 'PT1_Index', 'VG1_Index', 'Z 1_Index',
                                                            'GX1_Index', 'ST1_Index', 'CF1_Index', 'OI1_Index', 'QC1_Index',
                                                            'ATT1_Index', 'BE1_Index', 'EO1_Index', 'OT1_Index', 'XP1_Index',
                                                            'TP1_Index', 'NI1_Index', 'HI1_Index', 'IH1_Index', 'MES1_Index',
                                                            'BZ1_Index']]

commodity_energy =  [Asset(x, "commodity_energy") for x in ['CL1_Comdty', 'QS1_Comdty', 'XB1_Comdty',
                                                                                                        'HO1_Comdty', 'NG1_Comdty']]

commodity_metal = [Asset(x, "commodity_metal") for x in ['LMAHDS03 LME_Comdty', 'LMCADS03_Comdty',
                                                                                                    'LMNIDS03_Comdty', 'GC1_Comdty', 'SI1_Comdty']]

commodity_agriculture = [Asset(x, "commodity_agriculture") for x in ['LC1_Comdty', 'KC1_Comdty', 'C 1_Comdty',
                                                                                                                    'CT1_Comdty', 'S 1_Comdty', 'SB1_Comdty',
                                                                                                                    'W 1_Comdty']]

equity[0].get_prices().head(50)
