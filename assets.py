import pandas as pd
import os
import datetime


class Asset:

    def __init__(self, name, category):

        assert isinstance(name, str), f"name '{name}' is not a string"
        self.__name = name

        assert isinstance(category, str), f"category '{category}' is not a string"
        self.__category = category

        for file in os.listdir("data"):
            if file.startswith(name):
                self.__full_name = os.path.join("data", file)
                self.__currency  = self.__full_name.split("_")[-1].split(".")[0]
                df_date = pd.DataFrame(index=pd.date_range(start="2001-09-08", end="2023-12-31"))
                df_data = pd.read_csv(self.__full_name, usecols=[1,2])
                df_data["date"] = pd.to_datetime(df_data["date"])
                df_merged = df_date.merge(df_data, how="left", left_index=True, right_on="date").set_index("date")
                df_merged.insert(0, "weekday", df_merged.index.day_name())
                df_merged = df_merged.rename(columns={"PX_LAST": f"{name}_PX-LAST"})
                df_merged[f"{name}_return"] = None
                self.__prices = df_merged

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

    def __repr__(self):
        return f"{self.get_name()} in {self.get_currency()}"


class Category:

    def __init__(self, category, assets):

        assert isinstance(category, str), f"category '{category}' is not a string"
        self.__category = category

        assert isinstance(assets, list), f"assets '{assets}' is not a list"
        self.__assets = [Asset(x, category) for x in assets]

    def get_category(self):
        return self.__category

    def get_assets(self):
        return self.__assets

    def __repr__(self):
        return f"{self.get_category()}, {self.get_assets()}, ..."


bonds = Category("Bonds", ['FB1_Comdty', 'TU1_Comdty', 'FV1_Comdty', 'TY1_Comdty',
                                                'WN1_Comdty', 'CV1_Comdty', 'XQ1_Comdty', 'CN1_Comdty',
                                                'LGB1_Comdty', 'WB1_Comdty', 'WX1_Comdty', 'G 1_Comdty',
                                                'UGL1_Comdty', 'DU1_Comdty', 'OE1_Comdty', 'RX1_Comdty',
                                                'UB1_Comdty', 'IK1_Comdty', 'OAT1_Comdty', 'XM1_Comdty',
                                                'JB1_Comdty', 'KAA1_Comdty', 'TFT1_Comdty'])

equity = Category("Equity", ['SM1_Index', 'ES1_Index', 'PT1_Index', 'VG1_Index', 'Z 1_Index',
                                                'GX1_Index', 'ST1_Index', 'CF1_Index', 'OI1_Index', 'QC1_Index',
                                                'ATT1_Index', 'BE1_Index', 'EO1_Index', 'OT1_Index', 'XP1_Index',
                                                'TP1_Index', 'NI1_Index', 'HI1_Index', 'IH1_Index', 'MES1_Index',
                                                'BZ1_Index'])

commodity_energy = Category("Commodity_Energy", ['CL1_Comdty', 'QS1_Comdty', 'XB1_Comdty',
                                                                                           'HO1_Comdty', 'NG1_Comdty'])

commodity_metal = Category("Commodity_Metal", ['LMAHDS03 LME_Comdty', 'LMCADS03_Comdty',
                                                                                    'LMNIDS03_Comdty', 'GC1_Comdty', 'SI1_Comdty'])

commodity_agriculture= Category("Commodity_Agriculture", ['LC1_Comdty', 'KC1_Comdty', 'C 1_Comdty',
                                                                                                        'S 1_Comdty', 'SB1_Comdty',
                                                                                                        'W 1_Comdty']) # 'CT1_Comdty' missing



equity.get_assets()[0].get_prices()
