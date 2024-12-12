import logging
from datetime import datetime as dt
from .. import PROJECT_ROOT_PATH
from ..module.koreainvestment import KoreaInvestment

POSITIVE_ETF_CODE = '304940'  # kodex nasdaq 100(H)
INVERSE_ETF_CODE = '409810'  # kodex nasdaq 100 inverse
DISPARITY_SUM = -0.15
MIN_CASH = 0
MAX_CASH = 2_000_000


# 괴리율 직접 계산
# 호가 불러와서 평단가 괴리율 계산
class DisparityArbitragy:
    def __init__(self, positive_etf_code, inverse_etf_code, disparity_sum, min_cash, max_cash) -> None:
        self._positive_etf_code = positive_etf_code
        self._inverse_etf_code = inverse_etf_code
        self._disparity_sum = disparity_sum
        self._min_cash = min_cash
        self._max_cash = max_cash
        self.logger = logging.getLogger('EtfDisparity')
        logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s',
            filename=f'{PROJECT_ROOT_PATH}/log/etf_disparity_{self._positive_etf_code}.log',
            level=logging.INFO)
        self._broker = KoreaInvestment()
        self._diff = 0

    def on_trading_iteration(self):
        self._positive_etf_position = self._broker.get_open_position(POSITIVE_ETF_CODE)
        self._inverse_etf_position = self._broker.get_open_position(INVERSE_ETF_CODE)
        
        disparity_sum = self._positive_etf_info.disparity_rate + self._inverse_etf_info.disparity_rate
        self.logger.info(f'Sum of disparity rate: {disparity_sum}')
        
        # buy signal
        if self._positive_etf_position == None \
            and self._is_time_near_market_closing() \
            and disparity_sum <= -0.15:  
                print(f'[DisparityArbitragy] buy signal is up')
                positive_order_size, inverse_order_size, self._diff = self._calculate_order_size(
                    self._positive_etf_info.current_price,
                    self._inverse_etf_info.current_price,
                    MIN_CASH,
                    MAX_CASH)
                self._buy_etf_pair(positive_order_size, inverse_order_size)
        elif self._positive_etf_position != None and self._positive_etf_position.size > 0:
            if self._positive_etf_info.disparity_rate + self._inverse_etf_info.disparity_rate > 0:  # sell signal
                print(f'[DisparityArbitragy] sell signal is up')
                self._sell_etf_pair(
                    self._positive_etf_position.size, self._inverse_etf_position.size)
            elif self._is_time_near_market_closing():
                total_amount = self._positive_etf_position.size * self._positive_etf_position.current_price + \
                    self._inverse_etf_position.size * self._inverse_etf_position.current_price
                positive_order_size, inverse_order_size, self._diff = self._calculate_order_size(
                    self._positive_etf_info.current_price,
                    self._inverse_etf_info.current_price,
                    min_cash=total_amount,
                    max_cash=MAX_CASH)
                if positive_order_size == 0:
                    print(
                        f'[DisparityArbitragy] cannot buy more etf pair for rebalancing')
                    self._sell_etf_pair(
                        self._positive_etf_position.size, self._inverse_etf_position.size)
                else:
                    print(f'[DisparityArbitragy] buy more etf pair for rebalancing')
                    self._buy_etf_pair(
                        positive_order_size - self._positive_etf_position.size,
                        inverse_order_size - self._inverse_etf_position.size)

    def _buy_etf_pair(self, positive_order_size, inverse_order_size):
        current_cash = self._broker.get_account_cash()
        if current_cash < 0:
            print(f'Not enough cash: currnet={current_cash}')
            return
        buy_order_positive = {
            "code": POSITIVE_ETF_CODE,
            "side": "buy",
            "size": str(positive_order_size),
            "price": str(self._positive_etf_info.current_price),
            "type": "market"
        }
        buy_order_inverse = {
            "code": INVERSE_ETF_CODE,
            "side": "buy",
            "size": str(inverse_order_size),
            "price": str(self._positive_etf_info.current_price),
            "type": "market"
        }
        print(
            f'DisparityArbitragy excute buy orders: pos_size={positive_order_size} inverse_size={inverse_order_size}')

        self._broker.submit_order(buy_order_positive)
        self._broker.submit_order(buy_order_inverse)

    def _sell_etf_pair(self, positive_order_size, inverse_order_size):
        sell_order_positive = {
            "code": POSITIVE_ETF_CODE,
            "side": "sell",
            "size": str(positive_order_size),
            "price": str(self._positive_etf_info.current_price),
            "type": "market"
        }
        sell_order_inverse = {
            "code": INVERSE_ETF_CODE,
            "side": "sell",
            "size": str(inverse_order_size),
            "price": str(self._positive_etf_info.current_price),
            "type": "market"
        }
        print(
            f'DisparityArbitragy excute sell orders: pos_size={positive_order_size} inverse_size={inverse_order_size}')
        self._broker.submit_order(sell_order_positive)
        self._broker.submit_order(sell_order_inverse)

    def _calculate_disparity(self):
        pass

    def _calculate_order_size(self, positive_price: int, inverse_price: int, min_cash: int, max_cash=3_000_000) -> tuple:
        optimal_positive_size = 0
        optimal_reverse_size = 0
        total_cost_positive = 0
        total_cost_inverse = 0

        min_difference = float('inf')
        max_positive_size = int((max_cash / 2) / positive_price)
        max_inverse_size = int((max_cash / 2) / inverse_price)
        for positive_size in range(1, max_positive_size):
            reverse_size = round(
                positive_price / inverse_price * positive_size)
            for delta in [0, 1]:
                current_reverse_size = reverse_size + delta
                if current_reverse_size <= 0 or reverse_size > max_inverse_size:
                    continue
                positive_cost = positive_price * positive_size
                inverse_cost = inverse_price * current_reverse_size
                if positive_cost + inverse_cost < min_cash:
                    continue
                difference = abs(positive_cost - inverse_cost)
                if difference < min_difference:
                    min_difference = difference
                    optimal_positive_size = positive_size
                    optimal_reverse_size = current_reverse_size
                    total_cost_positive = positive_cost
                    total_cost_inverse = inverse_cost
        print(optimal_positive_size, optimal_reverse_size,
              abs(total_cost_positive - total_cost_inverse))
        return optimal_positive_size, optimal_reverse_size, abs(total_cost_positive - total_cost_inverse)

    def _is_time_near_market_closing(self):
        return dt.strptime('15:00', '%H:%M').time() < dt.now().time() < dt.strptime('15:20', '%H:%M').time()
