from dotenv import load_dotenv
import os
import pandas as pd
import numpy as np
import pandas_ta as ta
import ccxt
import logging
from strategy import PROJECT_ROOT_PATH
from pprint import pprint

class BollingerbandBreakout():
    def __init__(self, base, quote, prio, max_position_count=2, interval='4h', leverage=1):
        self.base = base
        self.quote = quote
        self.prio = prio
        self.max_position_count = max_position_count
        self.interval = interval
        # self.execution_times = ['01:00', '05:00', '09:00', '13:00', '17:00', '21:00']
        self.leverage = leverage
        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.INFO)
        file_handler = logging.FileHandler(f'{PROJECT_ROOT_PATH}/log/bb_breakout_{self.base}.log')
        formatter = logging.Formatter(f"%(asctime)s [BollingerbandBreakout] %(levelname)s: %(message)s")
        file_handler.setFormatter(formatter)
        self._logger.addHandler(file_handler)

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
        balance = self.exchange.fetch_balance()
        self._total_cash = balance[self.quote]['total']
        self._long_position_count = 0
        self._short_position_count = 0

    def on_trading_iteration(self):
        self._logger.info(f'Start trading iteration: exchange=Binance, symbol={self.base}/{self.quote}, interval={self.interval}, leverage={self.leverage}')
        ohlcv_df = self._fetch_ohlcv(self.asset, self.interval)
        sma_200 = ohlcv_df.ta.sma(length=200)
        bbands = ohlcv_df.ta.bbands(length=20, std=2).iloc[-1]
        atr = ohlcv_df.ta.atr(length=14).iloc[-1]
        volume_threshold = 3 * ohlcv_df['volume'].rolling(6 * 7).mean().iloc[-1] # 6 * 7 = (1 week in 4h timeframe)
        qty = self._total_cash * 0.01 / atr
        self._logger.info(f'close: {ohlcv_df["close"].iloc[-1]}, \
sma_200: {sma_200.iloc[-2]} {sma_200.iloc[-1]}, \
bbands_upper: {bbands["BBU_20_2.0"]}, \
bbands_mid: {bbands["BBM_20_2.0"]}, \
bbands_lower: {bbands["BBL_20_2.0"]}, \
1 tick before volume: {ohlcv_df["volume"].iloc[-2]}, \
volume_threshold: {volume_threshold}')

        # open long position
        if self._short_position_count == 0 and self._long_position_count <= self.max_position_count \
                and ohlcv_df['close'].iloc[-1] > bbands['BBU_20_2.0'] \
                and sma_200.iloc[-1] > sma_200.iloc[-2] \
                and ohlcv_df['volume'].iloc[-2] > volume_threshold:
            order = self.exchange.create_market_buy_order(self.asset, qty)
            self._long_position_count += 1
            self._logger.info(
                f'Open long position; \
symbol:{self.asset}, \
order_id:{order["id"]}, \
type:{order["type"]}, \
side:{order["side"]}, \
price:{order["price"]}, \
avg_price:{order["average"]}, \
cost:{order["cost"]}, \
amount: {order["amount"]}, \
filled:{order["filled"]}, \
remaining:{order["remaining"]}, \
status:{order["status"]}, \
position_count: {self._long_position_count}')

        # open short position
        if self._long_position_count == 0 and self._short_position_count <= self.max_position_count \
                and ohlcv_df['close'].iloc[-1] < bbands['BBL_20_2.0'] \
                and sma_200.iloc[-1] < sma_200.iloc[-2] \
                and ohlcv_df['volume'].iloc[-2] > volume_threshold:
            order = self.exchange.create_market_sell_order(self.asset, qty)
            self._short_position_count += 1
            self._logger.info(
                f'Open short position; \
symbol:{self.asset}, \
order_id:{order["id"]}, \
type:{order["type"]}, \
side:{order["side"]}, \
price:{order["price"]}, \
avg_price:{order["average"]}, \
cost:{order["cost"]}, \
amount: {order["amount"]}, \
filled:{order["filled"]}, \
remaining:{order["remaining"]}, \
status:{order["status"]}, \
position_count: {self._short_position_count}')

        # close long position
        if self._long_position_count > 0 and ohlcv_df['close'].iloc[-1] <= bbands['BBM_20_2.0']:
            balance = self.exchange.fetch_balance()
            open_position = self._get_base_position(
                self.base, balance['positions'])
            if open_position == None:
                self._logger.error(f'cannot find {self.base} positions')
            qty = open_position['positionAmt']
            order = self.exchange.create_market_sell_order(self.asset, qty)
            self._long_position_count = 0
            self._logger.info(
                f'Close long position; \
symbol:{self.asset}, \
order_id:{order["id"]}, \
type:{order["type"]}, \
side:{order["side"]}, \
price:{order["price"]}, \
avg_price:{order["average"]}, \
cost:{order["cost"]}, \
amount: {order["amount"]}, \
filled:{order["filled"]}, \
remaining:{order["remaining"]}, \
status:{order["status"]}')

        # close short position
        if self._short_position_count > 0 and ohlcv_df['close'].iloc[-1] >= bbands['BBM_20_2.0']:
            balance = self.exchange.fetch_balance()
            open_position = self._get_base_position(
                self.base, balance['positions'])
            if open_position == None:
                self._logger.error(f'cannot find {self.base} positions')
            qty = open_position['positionAmt']
            order = self.exchange.create_market_buy_order(self.asset, qty)
            self._short_position_count = 0
            self._logger.info(
                f'Close short position; \
symbol:{self.asset}, \
order_id:{order["id"]}, \
type:{order["type"]}, \
side:{order["side"]}, \
price:{order["price"]}, \
avg_price:{order["average"]}, \
cost:{order["cost"]}, \
amount: {order["amount"]}, \
filled:{order["filled"]}, \
remaining:{order["remaining"]}, \
status:{order["status"]}')
        
        self._logger.info(f'End trading iteration: exchange=Binance, symbol={self.base}/{self.quote}, interval={self.interval}, leverage={self.leverage}')

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