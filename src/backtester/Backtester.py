import backtrader as bt, pandas as pd
from ..engines.StrategyEngine import StrategyEngine
import vectorbt as vbt

class AVWAPStrategy(bt.Strategy):
    params = dict(engine=None)

    def __init__(self):
        self.engine: StrategyEngine = self.params.engine

    def next(self):
        df = pd.DataFrame({
            "close": [self.data.close[0]],
            "low": [self.data.low[0]],
            "high": [self.data.high[0]],
            "volume": [self.data.volume[0]],
        }, index=[self.data.datetime.datetime(0)])
        sig = self.engine.generate_signal(df)
        if sig["action"] == "BUY":
            self.buy()
        elif sig["action"] == "SELL":
            self.sell()

def run_backtest(csv_path: str):
    cerebro = bt.Cerebro()
    data = bt.feeds.GenericCSVData(dataname=csv_path,
                                   dtformat=("%Y-%m-%d"),
                                   datetime=0, open=1, high=2, low=3, close=4, volume=5, openinterest=-1)
    cerebro.adddata(data)
    cerebro.addstrategy(AVWAPStrategy, engine=StrategyEngine({}))
    cerebro.run()
    cerebro.plot()

def vectorbt_backtest(df: pd.DataFrame, engine: StrategyEngine):
    """
    Quick vectorbt wrapper around StrategyEngine.generate_signal.
    """
    entries = df['close'].rolling(1).apply(lambda x: engine.generate_signal(df.loc[[x.index[0]]])["action"]=="BUY")
    exits   = df['close'].rolling(1).apply(lambda x: engine.generate_signal(df.loc[[x.index[0]]])["action"]=="SELL")
    pf = vbt.Portfolio.from_signals(df['close'], entries.astype(bool), exits.astype(bool))
    return pf.stats()