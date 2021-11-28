"""
Settings that are particular to my own trend following strategy
"""
from investmentstk.data_feeds.data_feed import TimeResolution
from investmentstk.models.source import Source

PERIODICITY_PER_BROKER = {
    # Stocks: monthly
    Source.Degiro: TimeResolution.month,
    Source.Avanza: TimeResolution.month,
    Source.Nordnet: TimeResolution.month,
    # Commodities and crypto: weekly
    Source.CMC: TimeResolution.week,
    Source.Kraken: TimeResolution.week,
}

"""
The assets where I use a monthly strategy (stocks) usually have smoother trends
and can afford a lower multiplier. The assets where I use a weekly strategy (commodities, cryptos)
usually have shorter and not so smooth trends, and I have a larger multiplier to compensate.
The main consequence is that my stop loss becomes further away and has more room to accommodate
false trend reversals.
"""
ATR_MULTIPLIER_PER_PERIODICITY = {TimeResolution.month: 2.5, TimeResolution.week: 3}

ATR_PERIOD = 21
