
import time

import ccxt
import structlog

class DefaultBehaviour():
    def __init__(self, behaviour_config, exchange_interface, strategy_analyzer, notifier):
        self.behaviour_config = behaviour_config
        self.exchange_interface = exchange_interface
        self.strategy_analyzer = strategy_analyzer
        self.notifier = notifier

    def run(self, market_pairs):
        if market_pairs:
            market_data = self.exchange_interface.get_symbol_markets(market_pairs)
        else:
            market_data = self.exchange_interface.get_exchange_markets()

        self.test_strategies(market_data)

    def test_strategies(self, market_data):
        for exchange in market_data:
            for market_pair in market_data[exchange]:

                try:
                    one_day_historical_data = self.strategy_analyzer.get_historical_data(
                        market_data[exchange][market_pair]['symbol'],
                        exchange,
                        '1d'
                    )

                    five_minute_historical_data = self.strategy_analyzer.get_historical_data(
                        market_data[exchange][market_pair]['symbol'],
                        exchange,
                        '5m'
                    )

                    rsi_data = self.strategy_analyzer.analyze_rsi(
                        one_day_historical_data
                    )

                    sma_data = self.strategy_analyzer.analyze_sma(
                        one_day_historical_data
                    )

                    ema_data = self.strategy_analyzer.analyze_ema(
                        one_day_historical_data
                    )

                    breakout_data = self.strategy_analyzer.analyze_breakout(
                        five_minute_historical_data
                    )

                    ichimoku_data = self.strategy_analyzer.analyze_ichimoku_cloud(
                        one_day_historical_data
                    )

                    macd_data = self.strategy_analyzer.analyze_macd(
                        one_day_historical_data
                    )

                # bandaid fixes
                except ccxt.errors.RequestTimeout:
                    continue

                if breakout_data['is_hot']:
                    self.notifier.notify_all(
                        message="{} is breaking out!".format(market_pair)
                    )

                if rsi_data['is_cold']:
                    self.notifier.notify_all(
                        message="{} is over bought!".format(market_pair)
                    )

                elif rsi_data['is_hot']:
                    self.notifier.notify_all(
                        message="{} is over sold!".format(market_pair)
                    )

                if sma_data['is_hot']:
                    self.notifier.notify_all(
                        message="{} is trending well according to SMA!".format(market_pair)
                    )

                if ema_data['is_hot']:
                    self.notifier.notify_all(
                        message="{} is trending well according to EMA!".format(market_pair)
                    )

                if ichimoku_data['is_hot']:
                    self.notifier.notify_all(
                        message="{} is trending well according to Ichimoku!".format(
                            market_pair
                            )
                        )

                print("{}: \tBreakout: {} \tRSI: {} \tSMA: {} \tEMA: {} \tIMC: {} \tMACD: {}".format(
                    market_pair,
                    breakout_data['values'][0],
                    format(rsi_data['values'][0], '.2f'),
                    format(sma_data['values'][0], '.7f'),
                    format(ema_data['values'][0], '.7f'),
                    format(ichimoku_data['values'][0], '.7f') + "/" + format(ichimoku_data['values'][1], '.7f'),
                    format(macd_data['values'][0], '.7f')))
