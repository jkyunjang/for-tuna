from dotenv import load_dotenv
import os
import pandas as pd
import numpy as np
import pandas_ta as ta
import ccxt
import logging

MAX_POSITION_COUNT = 3

class BollingerbandBreakout():
    def __init__(self, base, quote):
        self.base = base
        self.quote = quote
        self.logger = logging.getLogger('BollingerbandBreakout')
        logging.basicConfig(
            format='%(asctime)s %(levelname)s:%(message)s',
            filename=f'./log/bb_breakout_{self.base}.log',
            level=logging.INFO)
        load_dotenv()
        api_key = os.getenv('BINANCE_ACCESS_KEY')
        api_secret = os.getenv('BINANCE_SECRET_KEY')
        self.exchange = ccxt.binance(config={
            'apiKey': api_key,
            'secret': api_secret,
            'options': {
                'defaultType': 'future',
            }})
        self.asset = f'{self.base}/{self.quote}'
        self.interval = '4h'
        balance = self.exchange.fetch_balance()
        self.cash = balance[self.quote]['total']
        self.leverage = 5
        self.long_position_count = 0
        self.short_position_count = 0

    def on_trading_iteration(self):
        self.logger.info('Start trading iteration')
        ohlcv_df = self._fetch_ohlcv(self.asset, self.interval)
        sma_long = ohlcv_df.ta.sma(length=200)
        bbands = ohlcv_df.ta.bbands(length=20, std=2).iloc[-1]
        atr = ohlcv_df.ta.atr(length=14).iloc[-1]
        volume_threshold = ohlcv_df['volume'].rolling(6 * 7).mean().iloc[-1]
        qty = self.cash * 0.01 / atr

        # open long position
        if self.short_position_count == 0 and self.long_position_count <= MAX_POSITION_COUNT \
                and ohlcv_df['close'].iloc[-1] > bbands['BBU_20_2.0'] \
                and sma_long.iloc[-1] > sma_long.iloc[-2] \
                and ohlcv_df['volume'].iloc[-1] > volume_threshold * 3:
            order = self.exchange.create_market_buy_order(self.asset, qty)
            self.long_position_count += 1
            self.logger.info(order)
            # self.logger.info(
            #     f'Open long position; symbol:{self.asset}, 
            #         order_id:{order["id"]}, 
            #         price:{order["cost"]}, 
            #         avg_price:{order["average"]}, 
            #         qty: {qty}, 
            #         fee:{order["fee"]["cost"]}{order["fee"]["currency"]}, 
            #         position_count: {self.long_position_count}')

        # open short position
        if self.long_position_count == 0 and self.short_position_count <= MAX_POSITION_COUNT \
                and ohlcv_df['close'].iloc[-1] < bbands['BBL_20_2.0'] \
                and sma_long.iloc[-1] < sma_long.iloc[-2] \
                and ohlcv_df['volume'].iloc[-1] > volume_threshold * 3:
            order = self.exchange.create_market_sell_order(self.asset, qty)
            self.short_position_count += 1
            self.logger.info(order)
            # self.logger.info(
            #     f'Open short position; symbol:{self.asset}, 
            #         order_id:{order["id"]}, 
            #         price:{order["cost"]}, 
            #         avg_price:{order["average"]}, 
            #         qty: {qty}, 
            #         fee:{order["fee"]["cost"]}{order["fee"]["currency"]}, 
            #         position_count: {self.short_position_count}')

        # close long position
        if self.long_position_count > 0 and ohlcv_df['close'].iloc[-1] <= bbands['BBM_20_2.0']:
            balance = self.exchange.fetch_balance()
            open_position = self._get_base_position(
                self.base, balance['positions'])
            if open_position == None:
                self.logger.error(f'cannot find {self.base} positions')
            qty = open_position['positionAmt']
            order = self.exchange.create_market_sell_order(self.asset, qty)
            self.long_position_count = 0
            self.logger.info(order)
            # self.logger.info(
            #     f'Close long position; symbol:{self.asset},
            #         price:{order["cost"]}, 
            #         avg_price:{order["average"]}, 
            #         qty: {qty}, 
            #         fee:{order["fee"]["cost"]}{order["fee"]["currency"]},
            #         realized_pnl:{order["info"]["realizedPnl"]}')

        # close short position
        if self.short_position_count > 0 and ohlcv_df['close'].iloc[-1] >= bbands['BBM_20_2.0']:
            balance = self.exchange.fetch_balance()
            open_position = self._get_base_position(
                self.base, balance['positions'])
            if open_position == None:
                self.logger.error(f'cannot find {self.base} positions')
            qty = open_position['positionAmt']
            order = self.exchange.create_market_buy_order(self.asset, qty)
            self.short_position_count = 0
            self.logger.info(order)
            # self.logger.info(
            #     f'Close short position; symbol:{self.asset},
            #         price:{order["cost"]}, 
            #         avg_price:{order["average"]}, 
            #         qty: {qty}, 
            #         fee:{order["fee"]["cost"]}{order["fee"]["currency"]},
            #         realized_pnl:{order["info"]["realizedPnl"]}')
        self.logger.info('End trading iteration')

    def _fetch_ohlcv(self, asset, interval):
        ohlcv = self.exchange.fetch_ohlcv(asset, interval)
        df = pd.DataFrame(
            ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

        return df

    def _get_base_position(self, base, positions):
        for p in positions:
            if p['symbol'] == base:
                return p
        return None

if __name__ == '__main__':
    strategy = BollingerbandBreakout('ETH', 'USDT')
    strategy.on_trading_iteration()
