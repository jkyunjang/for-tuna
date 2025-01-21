import time
from selenium import webdriver
from selenium.webdriver.common.by import By

'''
필독
- 크롬 remote-debugging 모드에서 mexc에 로그인(수동으로 로그인 해야함)
- 매매 단위를 USDT가 아닌 코인으로 설정, margin 모드 및 레버리지는 입맛에 맞게 지정
- 설정에서 거래에서 발생하는 모든 팝업 끄기, 이벤트 팝업 끄기
- 이 API를 사용할 때, 증거금이 충분한지 확인하는 로직 필요
'''
class MexcFuture:
    def __init__(self, pair: str) -> None:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument(r'user-data-dir=D:\chrome-debug')
        chrome_options.add_argument(f'remote-debugging-port=9222')
        chrome_options.add_experimental_option('detach', True)
        self.__driver = webdriver.Chrome(options=chrome_options)
        self.__driver.get(f'https://futures.testnet.mexc.com/exchange/{pair}')
        # wait for page rendering
        time.sleep(10)
        if self.__driver.current_url != f'https://futures.testnet.mexc.com/exchange/{pair}':
            raise ValueError(f'{pair} is invalid coin')
        self.__mexc_elem = _MexcHtmlElement(self.__driver)
        # eliminate event popup 
        if self.__mexc_elem.event_popup_close_button != None:
            self.__mexc_elem.event_popup_close_button.click()

    '''
    parameters \n
    side: "long" or "short"
    order_type: currently only supports market order type
    quantity: contract quantity to buy
    '''
    def open_position(self, side: str, quantity: float, order_type='market') -> None:
        self.__mexc_elem.open_span.click()
        if order_type == 'market':
            self.__mexc_elem.open_market_span.click()
        else:
            raise NotImplementedError()
        self.__mexc_elem.open_quantity_input.send_keys(str(quantity))
        if side == "long":
            self.__mexc_elem.open_long_button.click()
        elif side == "short":
            self.__mexc_elem.open_short_button.click()
        else:
            ValueError(f'{side} is invalid position side')

    '''
    parameters \n
    side: "long" or "short"
    order_type: currently only supports market order type
    quantity: contract quantity to sell
    '''
    def close_position(self, side: str, quantity: float, order_type='market') -> None:
        self.__mexc_elem.close_span.click()
        if order_type == 'market':
            self.__mexc_elem.close_market_span.click()
        else:
            raise NotImplementedError()
        self.__mexc_elem.close_quantity_input.send_keys(str(quantity))
        if side == "long":
            self.__mexc_elem.close_long_button.click()
        elif side == "short":
            self.__mexc_elem.close_short_button.click()
        else:
            ValueError(f'{side} is invalid position side')

    def __str_with_unit_to_float(self, text):
        if not isinstance(text, str):
            raise ValueError("parameter must be string")
        try: 
            number = text.replace(',', '')
            return float(number)
        except ValueError:
            number = number.strip().upper()
            if number.endswith('K'):
                return float(number[:-1]) * 1_000
            elif number.endswith('M'):
                return float(number[:-1]) * 1_000_000
            elif number.endswith('B'):
                return float(number[:-1]) * 1_000_000_000
            elif number.endswith('T'):
                return float(number[:-1]) * 1_000_000_000_000
            else:
                raise NotImplementedError

    def get_orderbook(self):
        orderbook = {}
        for i in range(1, self.__mexc_elem.bid_ask_num + 1):
            orderbook[f'bid_{i}'] = (
                self.__str_with_unit_to_float(getattr(self.__mexc_elem, f'bid_price_span_{i}').text),
                self.__str_with_unit_to_float(getattr(self.__mexc_elem, f'bid_quantity_span_{i}').text)
            )
        for i in range(1, self.__mexc_elem.bid_ask_num + 1):
            orderbook[f'ask_{i}'] = (
                self.__str_with_unit_to_float(getattr(self.__mexc_elem, f'ask_price_span_{i}').text),
                self.__str_with_unit_to_float(getattr(self.__mexc_elem, f'ask_quantity_span_{i}').text)
            )
        return orderbook

class _MexcHtmlElement:
    def __init__(self, driver):
        self.open_long_button = driver.find_element(
            By.XPATH, '//*[@id="mexc_contract_v_open_position"]/div/div[4]/div[4]/section/div/div[1]/button[1]')
        self.open_short_button = driver.find_element(
            By.XPATH, '//*[@id="mexc_contract_v_open_position"]/div/div[4]/div[4]/section/div/div[1]/button[2]')
        self.close_short_button = driver.find_element(
            By.XPATH, '//*[@id="mexc-web-inspection-futures-exchange-orderForm"]/div[2]/div[2]/div[2]/div/div/div[3]/div[3]/section/div/div[1]/button[1]')
        self.close_long_button = driver.find_element(
            By.XPATH, '//*[@id="mexc-web-inspection-futures-exchange-orderForm"]/div[2]/div[2]/div[2]/div/div/div[3]/div[3]/section/div/div[1]/button[2]')
        self.open_market_span = driver.find_element(
            By.XPATH, '//*[@id="mexc_contract_v_open_position"]/div/div[1]/div/span[2]')
        self.close_market_span = driver.find_element(
            By.XPATH, '//*[@id="mexc-web-inspection-futures-exchange-orderForm"]/div[2]/div[2]/div[2]/div/div/div[1]/div/span[2]')
        self.open_quantity_input = driver.find_element(
            By.XPATH, '//*[@id="mexc_contract_v_open_position"]/div/div[4]/div[1]/div/div[2]/div/div/input')
        self.close_quantity_input = driver.find_element(
            By.XPATH, '//*[@id="mexc-web-inspection-futures-exchange-orderForm"]/div[2]/div[2]/div[2]/div/div/div[3]/div[1]/div/div[2]/div/div/input')
        self.open_span = driver.find_element(
            By.XPATH, '//*[@id="mexc-web-inspection-futures-exchange-orderForm"]/div[1]/div[1]/span[1]')
        self.close_span = driver.find_element(
            By.XPATH, '//*[@id="mexc-web-inspection-futures-exchange-orderForm"]/div[1]/div[1]/span[2]')
        self.bid_div = driver.find_element(
            By.XPATH, '//*[@id="mexc-web-inspection-futures-exchange-orderbook"]/div[2]/div[2]/div[1]/div[1]')
        self.bid_ask_num = len(self.bid_div.find_elements(By.TAG_NAME, 'span'))
        
        for i in range(self.bid_ask_num, 0, -1):
            setattr(self, f'bid_price_span_{i}', driver.find_element(
                By.XPATH, f'//*[@id="mexc-web-inspection-futures-exchange-orderbook"]/div[2]/div[2]/div[3]/div[1]/div[{i}]/div[1]/span'))
            setattr(self, f'bid_quantity_span_{i}', driver.find_element(
                By.XPATH, f'//*[@id="mexc-web-inspection-futures-exchange-orderbook"]/div[2]/div[2]/div[3]/div[1]/div[{i}]/div[2]'))
        
        self.ask_div = driver.find_element(
            By.XPATH, '//*[@id="mexc-web-inspection-futures-exchange-orderbook"]/div[2]/div[2]/div[1]/div[1]')
        for i in range(self.bid_ask_num, 0, -1):
            setattr(self, f'ask_price_span_{i}', driver.find_element(
                By.XPATH, f'//*[@id="mexc-web-inspection-futures-exchange-orderbook"]/div[2]/div[2]/div[1]/div[1]/div[{i}]/div[1]/span'))
            setattr(self, f'ask_quantity_span_{i}', driver.find_element(
                By.XPATH, f'//*[@id="mexc-web-inspection-futures-exchange-orderbook"]/div[2]/div[2]/div[1]/div[1]/div[{i}]/div[2]'))
       
        self.event_popup_close_button = None
        try:
            self.event_popup_close_button = driver.find_element(By.XPATH, '/div/div/div[2]/div/div[2]/button')
        except Exception:
            pass
        # self.open_position_available_span = driver.find_element(
        #     By.XPATH, '//*[@id="mexc_contract_v_open_position"]/div/div[2]/div[1]/span[2]')
        # self.margin_mode_span = driver.find_element(
        #     By.XPATH, '//*[@id="mexc-web-inspection-futures-exchange-orderForm"]/div[2]/div[1]/section/div[1]/span')
        # self.leverage_span = driver.find_element(
        #     By.XPATH, '//*[@id="mexc-web-inspection-futures-exchange-orderForm"]/div[2]/div[1]/section/div[2]/span')
        # self.quantity_unit_span = driver.find_element(
        #     By.XPATH, '//*[@id="mexc_contract_v_open_position"]/div/div[4]/div[1]/div/div[1]/span/span/span[2]/div/span')