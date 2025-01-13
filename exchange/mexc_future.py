from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

class MexcFuture:
    def __init__(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument(r'user-data-dir=D:\chrome-debug')
        chrome_options.add_argument(f'remote-debugging-port=9222')
        chrome_options.add_experimental_option('detach', True)
        self.__driver = webdriver.Chrome(options=chrome_options)
        self.__open_long_button = self.__driver.find_element(By.XPATH, '/html/body/div[3]/section/div[3]/div[7]/section/div[2]/div[2]/div[1]/div/div/div[4]/div[4]/section/div/div[1]/button[1]')
        self.__open_short_button = self.__driver.find_element(By.XPATH, '/html/body/div[3]/section/div[3]/div[7]/section/div[2]/div[2]/div[1]/div/div/div[4]/div[4]/section/div/div[1]/button[2]')
        self.__close_short_button = self.__driver.find_element(By.XPATH, '/html/body/div[3]/section/div[3]/div[7]/section/div[2]/div[2]/div[2]/div/div/div[3]/div[3]/section/div/div[1]/button[1]')
        self.__close_long_button = self.__driver.find_element(By.XPATH, '/html/body/div[3]/section/div[3]/div[7]/section/div[2]/div[2]/div[2]/div/div/div[3]/div[3]/section/div/div[1]/button[2]')
        self.__market_span = self.__driver.find_element(By.XPATH, '/html/body/div[3]/section/div[2]/div[7]/section/div[2]/div[2]/div[2]/div/div/div[1]/div/span[2]')
        self.__quantity_input = self.__driver.find_element(By.XPATH, '/html/body/div[3]/section/div[3]/div[7]/section/div[2]/div[2]/div[1]/div/div/div[4]/div[1]/div/div[2]/div/div/input')
        self.__open_span = self.__driver.find_element(By.XPATH, '/html/body/div[3]/section/div[3]/div[7]/section/div[1]/div[1]/span[1]')
        self.__close_span = self.__driver.find_element(By.XPATH, '/html/body/div[3]/section/div[3]/div[7]/section/div[1]/div[1]/span[2]')        

    def open_long_position(self, coin, order_type, quantity):
        self.__open_span.click()
        if order_type == 'market':
            self.__market_span.click()
        else:
            raise NotImplementedError()