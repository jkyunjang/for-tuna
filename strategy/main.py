import schedule
import time
from datetime import datetime, timedelta
from strategy.trend_following.bb_breakout import BollingerbandBreakout
from strategy.arb.etf_disparity import DisparityArbitragy

if __name__ == '__main__':
    bb_breakout_4h = BollingerbandBreakout('BTC', 'USDT', prio=2, interval='4h', max_position_count=2, leverage=1)
    # kodex nasdaq 100(H), kodex nasdaq 100 inverse
    disparity_arb = DisparityArbitragy('304940', '409810', base_disparity=-0.15, min_cash=0, max_cash=2_000_000)
    
    schedule.every().day.at("01:00").do(bb_breakout_4h.on_trading_iteration)
    schedule.every().day.at("05:00").do(bb_breakout_4h.on_trading_iteration)
    schedule.every().day.at("09:00").do(bb_breakout_4h.on_trading_iteration)
    schedule.every().day.at("13:00").do(bb_breakout_4h.on_trading_iteration)
    schedule.every().day.at("17:00").do(bb_breakout_4h.on_trading_iteration)
    schedule.every().day.at("21:00").do(bb_breakout_4h.on_trading_iteration)
    start_time = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
    end_time = datetime.now().replace(hour=15, minute=20, second=0, microsecond=0)
    current_time = start_time
    while current_time <= end_time:
        schedule.every().day.at(current_time.strftime("%H:%M")).do(disparity_arb.on_trading_iteration)
        current_time += timedelta(minutes=10)
    while True:
        schedule.run_pending()
        time.sleep(1)