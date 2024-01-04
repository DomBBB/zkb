import pandas as pd
import numpy as np
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
                df_date = pd.DataFrame(index=pd.date_range(start="2023-01-01", end="2023-12-31"))
                df_data = pd.read_csv(self.__full_name, usecols=[1,2])
                df_data["date"] = pd.to_datetime(df_data["date"])
                df = df_date.merge(df_data, how="left", left_index=True, right_on="date").reset_index(drop=True)
                df.insert(1, "weekday", df["date"].dt.day_name())
                df = df.rename(columns={"PX_LAST": f"{name}_PX-LAST"})
                df[f"{name}_start"] = ""
                df[f"{name}_end"] = ""
                df[f"{name}_return"] = ""
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
                # Calculate returns
                start_index = None
                for index, row in df.iterrows():
                    if row[f"{name}_start"] == "start" and start_index is None:
                        start_index = index
                    elif row[f"{name}_end"] == "end" and start_index is not None:
                        start_price = df.at[start_index, f"{name}_PX-LAST"]
                        end_price = row[f"{name}_PX-LAST"]
                        df.at[index, f"{name}_return"] = (end_price - start_price) / start_price * 100 #in %
                        start_index = None
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
                                                'TP1_Index', 'NI1_Index', 'HI1_Index', 'MES1_Index',
                                                'BZ1_Index']) # 'IH1_Index' ends in june 23

commodity_energy = Category("Commodity_Energy", ['CL1_Comdty', 'QS1_Comdty', 'XB1_Comdty',
                                                                                           'HO1_Comdty', 'NG1_Comdty'])

commodity_metal = Category("Commodity_Metal", ['LMAHDS03 LME_Comdty', 'LMCADS03_Comdty',
                                                                                    'LMNIDS03_Comdty', 'GC1_Comdty', 'SI1_Comdty'])

commodity_agriculture= Category("Commodity_Agriculture", ['LC1_Comdty', 'KC1_Comdty', 'C 1_Comdty',
                                                                                                        'S 1_Comdty', 'SB1_Comdty',
                                                                                                        'W 1_Comdty']) # 'CT1_Comdty' missing



equity.get_assets()[0].get_prices().head(50)


"""
Bonds:
    'FB1 Comdty',
    'TU1 Comdty',
    'FV1 Comdty',
    'TY1 Comdty',
    'WN1 Comdty',
    'CV1 Comdty',
    'XQ1 Comdty',
    'CN1 Comdty',
    'LGB1 Comdty',
    'WB1 Comdty',
    'WX1 Comdty',
    'G 1 Comdty',
    'UGL1 Comdty',
    'DU1 Comdty',
    'OE1 Comdty',
    'RX1 Comdty',
    'UB1 Comdty',
    'IK1 Comdty',
    'OAT1 Comdty',
    'XM1 Comdty',
    'JB1 Comdty',
    'KAA1 Comdty',
    'TFT1 Comdty'

Equity
    'SM1 Index',
    'ES1 Index',
    'PT1 Index',
    'VG1 Index',
    'Z 1 Index',
    'GX1 Index',
    'ST1 Index',
    'CF1 Index',
    'OI1 Index',
    'QC1 Index',
    'ATT1 Index',
    'BE1 Index',
    'EO1 Index',
    'OT1 Index',
    'XP1 Index',
    'TP1 Index',
    'NI1 Index',
    'HI1 Index',
    'IH1 Index',
    'MES1 Index',
    'BZ1 Index'

Commodity:
Energy:
    'CL1 Comdty',
    'QS1 Comdty',
    'XB1 Comdty',
    'HO1 Comdty',
    'NG1 Comdty'
Metals:
    'LMAHDS03 LME Comdty',
    'LMCADS03 Comdty',
    'LMNIDS03 Comdty',
    'GC1 Comdty',
    'SI1 Comdty'
Agri
    'LC1 Comdty',
    'KC1 Comdty',
    'C 1 Comdty',
    'CT1 Comdty',
    'S 1 Comdty',
    'SB1 Comdty',
    'W 1 Comdty'


Transaktionskosten:
    VIX Index / 20 * 0.03% => e.g. 13.34 / 20 =
    → Transaktionskosten evtl. auch vola-basiert anschauen (TK * VIX) „hoch in Corona → genau dort holen wir return

######
STEPS
######
1)
Download Data > CDEF in Bloomberg 2 Days to First Notice + "Relative" Roll (???relative to first notice; 2 days; ratio???) >
Wie sehen die Daten aus, machen sie Sinn? Was ist das bestmögliche Zeitfenster, sollen wir auf gewisse Futures von oben verzichten?
"Ausreisser unbedingt drinlassen"
Auch View auf den wichtigsten Währungen bilden. Portfolio Return ist Underlying+Währungsreturns.

2)
    -> Examine momentum and value strategies in a multi-asset portfolio with a given set of futures (stocks, bonds, commodities, and gold)
         1x wöchentliche Momentum Strategie & 1x wöchentliche Value Strategie. KRITERIEN: Performance + möglichst einfach (complex/performance tradeoff)
    -> Momentum klar Zeitserien Returns.
    -> Value sehr unklar v.a. im Multiasset Kontext. Basierend auf verschiedenen Kennzahlen -> Kurvensteigung Gold Futures (Cont./Backwardation).
         Sie schauen eigtl. nur Gold & Öl an -> price return reicht für Value. Wir sollen Value Mass suchen NUR auf Zeitserien (NUR basierend auf Returns (?); Neue
         Kennzahl brauch mehr Zeitserien). Andere HF schauen nur auf Preisentwicklung (Annahme langfristige Sharpe Ratio = darunter Value, darüber Growth).
    -> SIGNALE zuständig für Allokation oder nur in den Stocks?
    -> Generate a back test that analyses the two strategies for different time periods in the past. Is it optimal to separately combine the
         two strategies, to combine the signals or to switch between them? Describe your approach and explain why you have chosen your
         strategy and why it is optimal from your point of view.
Construct risk weighted ["auch Anlagestrategien innerhalb der Aktien"] (out-of-sample risk measure e.g. 1/vol) backtests with Long and Short (5 Long 5 Short)
on WEEKLY bases (e.g. Friday to Friday with data up to Thursday) INCLUDING Transaction Costs:
a.    Bonds Value and Momentum Strategy (Long and Short Leg)
b.    Equities Value and Momentum Strategy (Long and Short Leg)
c.     Commodities Value and Momentum Strategy (Long and Short Leg)
d.    All together Value and Momentum Strategy (Long and Short Leg) > how is the weight of the different asset classes over time?
Macht der Backtest Sinn? Haben wir keinen in-sample bias? Was sind die Turnover der Strategien?
Check what drives performance of Value and Momentum Strategy in a. to d ?
Gibt es ein Muster, das man ausnützen könnte im Vergleich zu 50% 50% weighted aus a. bis d. ["Strategie bauen, die switchen kann"]?
-> Kombinierung: 2 separate Strategien die Long-Short Portfolio kreieren.
    Wie wäre es, wenn 50-50 in die beiden Strategien. Wie könnte man Momentum & Value Strategien
    gewichten, in welchen Perioden performed was besser („value funktioniert oft nicht, aber wenn sie
    funktioniert wär sie besser gewesen“, „momentum funktioniert stabil“, „wann ist breakpoint zum
    wecheln“→eher interessant aus marketing perspektive, aber schwierig out-of-sample).
    Er würde switch versuchen („genaue entscheidung“, mit % hat man weder-noch“; regime switching
    probability wird nie 0-100% sein), daher wenn wir einen switch haben, dann 100% wechseln, da man
    dann auch mit abgeschwächter Form von Switch performed „Marktsituation, wo etwas besser ist“ →
    können wir noch ein Timing reinbringen, i.e. wann ist welcher Markt (timing der beiden)?
    Why strategy? Einfach (wenig Transaktionskosten) + outperformed. Evtl. schauen, ob wir timing noch
    hinkriegen.


First: (Referenz-)Benchmark entwickeln, der alle Asset-Klassen enthält. Am liebsten market-cap weighted, aber fragt er ob wir das hinkriegen,
weil Future kein market-cap hat. Dann vielleicht lieber risk-weighted / equal-weighted index/benchmark.
Oder Long/Short, immer 5 Assets insgesamt jede Woche? Passive Strategie als Benchmark
Problem: wie fangen wir an → Oder sollen wir wegkommen von long-only und immer gleich viel risiko long wie short;
backtest so definieren, dass wir in den besten Aktien Regionen long gehen (risiko basiert für die Exposure) und vergleichen
dann Long gegen Short ➔ Rendite von beiden Trades wäre dann Rendite der Faktoren?

Wir brauchen in unserem Modell die Trades für Long/Short; jede Woche die 5 Futures (als Abbildung des
Aktienindex) in die man long gehen soll und die 5 Futures in die man shorted. E.g. S&P hat 15% Vola
und wir gehen gleich in die entsprechenden Märkte rein um das Risiko zu adjusten. Z.B. investieren
wir 1/Vola. 15% vola ist 6.66% und 20% vola ist nur 5% → Ausgleich der Übergewichtung der Higher
Vola Märkte. Beides versuchen. Behauptung: Momentum funktioniert, weil sie immer in höhere Vola-
Märkte reingehen und nicht weil es risiko-adjustiert besser ist. Wenn wir Backtest schon
risikoadjustiert bauen, hält das.

Jede Woche per Freitag ins Close entscheiden, was wir für nächste Woche traden. Wir haben je ein
long- & ein short-portfolio mit unseren Assets und schauen dann die beiden legs an, die wir
risikoadjusted investieren → Differenz der beiden anschauen. Modell = Long/Short + Gewichtung.
Muss Long = Short in der Risikogewichtung sein, oder gibt es die Möglichkeit, das anders zu
gewichten: 1 Backtest nur innerhalb von jeder Assetklasse. 1 Strategie, wo man switchen kann i.e.
long bonds vs. short aktien, etc. „timing auf anlageklassen und nicht nur auf den futures innerhalb
der Anlageklassen“.

Fokus auf Generation Backtest? Gesamtresultat ist interessant, aber ihn interessiert auch das „wie“ / „generation“ und das sauber zu
machen, ob es konkretes Resultat gibt, ist dann zweitrangig für „real life“.
Value Strategy vs. Strategy mit Machine Learning.
Oder Momentum von Momentum (Paper) und bestes Momentum der Vergangenheit benutzt; z.B.
könnte man versuchen den out-of-sample backtest’s optimum nochmal zu backtesten);
Interessant wäre auch Daten runterzuladen und dann eine Periode gar nicht anschaut & die ausgewählte Strategie dann basierend
auf den Daten testen → Kollegen von ihm haben 2 Jahre research reingesteckt in verschiedene Strategien, aber hatten in ihrem
Backtest nie Drawdown von über 15% → Backtest hat grosses Overfitting Problem, daher lieber in einfach Strategie.
MÖGLICHST EINFACHE STRATEGIEN ZU VERWENDEN. Period aus Train rausnehmen und darauf testen.
Machine Learning Strategie fände er super interessant, z.B. auf den Daten bis vor 5 Jahren. Test.




KERN:
Interessant wie einfache Strategien funktioniert hätten auf time-series (wöchentlich rebalancing)
[WIE] & erklären was Differenz der beiden treibt/trieb (unabhängig) [WAS].
Alles andere ist Zusatz!

"""
