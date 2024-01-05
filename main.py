"""
LOAD DATA:
javac -cp ".;C:\Program Files (x86)\blp\dapi\blpapi3.jar" GetData.java
java -cp ".;C:\Program Files (x86)\blp\dapi\blpapi3.jar" GetData

HAVE:
1) All assets ('IH1_Index' ends in june 23 - downloaded but excluded from assets -> look for continuance?)
2) VIX Index

NEED:
Währungsviews



Transaktionskosten:
    VIX Index / 20 * 0.03% => e.g. 13.34 / 20 =
    → Transaktionskosten evtl. auch vola-basiert anschauen (TK * VIX) „hoch in Corona → genau dort holen wir return

######
STEPS
######
1)
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
