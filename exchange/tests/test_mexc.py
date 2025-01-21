import pytest
from exchange.mexc_future import MexcFuture

@pytest.fixture
def mexc():
    mexc = MexcFuture('BTC_USDT')
    return mexc
    
def test_open_long_position(mexc):
    # 증거금은 충분하다고 가정
    assert mexc.open_position('long', 0.001) == None

def test_close_position(mexc):
    assert mexc.close_position('long', 0.001) == None
    
def test_open_short_position(mexc):
    assert mexc.open_position('short', 0.001) == None

def test_close_short_position(mexc):
    assert mexc.close_position('short', 0.001) == None
    
def test_get_orderbook(mexc):
    print(mexc.get_orderbook())