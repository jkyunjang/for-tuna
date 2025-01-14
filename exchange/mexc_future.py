import time
from selenium import webdriver
from selenium.webdriver.common.by import By

'''
크롬 remote-debugging 모드에서 mexc에 로그인
선물 단위(USDT가 아닌 코인으로) 설정, margin 모드 및 레버리지는 입맛에 맞게 지정
거래에서 발생하는 모든 팝업 끄기
이 API를 사용할 때, 증거금이 충분한지 확인하는 로직 필요
'''
class MexcFuture:
    '''
    parameters \n
    coin - just write base coin name (ex. BTC)
    '''
    def __init__(self, coin: str) -> None:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument(r'user-data-dir=D:\chrome-debug')
        chrome_options.add_argument(f'remote-debugging-port=9222')
        chrome_options.add_experimental_option('detach', True)
        self.__driver = webdriver.Chrome(options=chrome_options)
        self.__driver.get(f'https://futures.testnet.mexc.com/exchange/{coin}_USDT')
        # wait for page rendering
        time.sleep(10)
        if self.__driver.current_url != f'https://futures.testnet.mexc.com/exchange/{coin}_USDT':
            raise ValueError(f'{coin} is invalid coin')
        self.__mexc_elem = __MexcHttpElement(self.__driver)
        
    '''
    parameters \n
    side: "long" or "short"
    order_type: currently only supports market
    quantity: contract quantity to buy
    '''
    def open_position(self, side: str, quantity: str, order_type='market') -> None:
        self.__mexc_elem.open_span.click()
        if order_type == 'market':
            self.__mexc_elem.market_span.click()
        else:
            raise NotImplementedError()
        self.__mexc_elem.quantity_input.send_keys(str(quantity))
        if side == "long":
            self.__mexc_elem.open_long_button.click()
        elif side == "short":
            self.__mexc_elem.open_short_button.click()
        else:
            ValueError(f'{side} is invalid position side')

    '''
    parameters \n
    side: "long" or "short"
    order_type: currently only supports market
    quantity: contract quantity to sell
    '''
    def close_position(self, side: str, quantity: str, order_type='market') -> None:
        self.__mexc_elem.close_span.click()
        if order_type == 'market':
            self.__mexc_elem.market_span.click()
        else:
            raise NotImplementedError()
        self.__mexc_elem.quantity_input.send_keys(str(quantity))
        if side == "long":
            self.__mexc_elem.close_long_button.click()
        elif side == "short":
            self.__mexc_elem.close_short_button.click()
        else:
            ValueError(f'{side} is invalid position side')

class __MexcHttpElement:
    def __init__(self, driver):
        self.open_long_button = driver.find_element(
            By.XPATH, '/html/body/div[3]/section/div[3]/div[7]/section/div[2]/div[2]/div[1]/div/div/div[4]/div[4]/section/div/div[1]/button[1]')
        self.open_short_button = driver.find_element(
            By.XPATH, '/html/body/div[3]/section/div[3]/div[7]/section/div[2]/div[2]/div[1]/div/div/div[4]/div[4]/section/div/div[1]/button[2]')
        self.close_short_button = driver.find_element(
            By.XPATH, '/html/body/div[3]/section/div[3]/div[7]/section/div[2]/div[2]/div[2]/div/div/div[3]/div[3]/section/div/div[1]/button[1]')
        self.close_long_button = driver.find_element(
            By.XPATH, '/html/body/div[3]/section/div[3]/div[7]/section/div[2]/div[2]/div[2]/div/div/div[3]/div[3]/section/div/div[1]/button[2]')
        self.market_span = driver.find_element(
            By.XPATH, '/html/body/div[3]/section/div[2]/div[7]/section/div[2]/div[2]/div[2]/div/div/div[1]/div/span[2]')
        self.quantity_input = driver.find_element(
            By.XPATH, '/html/body/div[3]/section/div[3]/div[7]/section/div[2]/div[2]/div[1]/div/div/div[4]/div[1]/div/div[2]/div/div/input')
        self.open_span = driver.find_element(
            By.XPATH, '/html/body/div[3]/section/div[3]/div[7]/section/div[1]/div[1]/span[1]')
        self.close_span = driver.find_element(
            By.XPATH, '/html/body/div[3]/section/div[3]/div[7]/section/div[1]/div[1]/span[2]')
