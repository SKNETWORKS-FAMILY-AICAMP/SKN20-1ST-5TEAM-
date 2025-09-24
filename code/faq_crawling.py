from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from db_connect import get_connection
import time

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)
HYUNDAI_URL = 'https://www.hyundai.com/kr/ko/faq.html'
GENESIS_URL = 'https://www.genesis.com/content/genesis-p2/kr/ko/support/faq.html?kw='

def set_hyundai_dynamic_crawling_option():
    driver.get(HYUNDAI_URL)
    driver.maximize_window() 
    time.sleep(2)   
    dl_elements = driver.find_elements(By.CSS_SELECTOR, "#contents > div.faq > div > div.section_white > div > div.result_area > div.ui_accordion.acc_01 > dl")
    for dl in dl_elements:
        try:
            button = dl.find_element(By.CSS_SELECTOR, "dt > button")
            driver.execute_script("arguments[0].scrollIntoView(true);", button)
            driver.execute_script("arguments[0].click();", button)
            time.sleep(0.5)

        except Exception as e:
            print(f"클릭 실패: {e}")
    time.sleep(2)

def crawl_hyundai_faq():
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    selected_dl_list = soup.select('#contents > div.faq > div > div.section_white > div > div.result_area > div.ui_accordion.acc_01 > dl')
    COMPANY = 'hyundai'

    for dl in selected_dl_list:
        question = dl.select_one('dt > b').text
        answer = dl.select_one('dd > .exp').text
        
        with get_connection() as conn:
            with conn.cursor() as cur:
                try:
                    sql = '''
                        INSERT INTO faq (idfaq, company, question, answer)
                        VALUES (%s, %s, %s, %s)
                    '''
                    cur.execute(sql, (None, COMPANY, question, answer))
                except Exception as e:
                    print(f'e: {e}')
                conn.commit()

def crawl_genesis_faq():
    driver.get(GENESIS_URL)
    driver.maximize_window() 
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    selected_div_list = soup.select('#faq_tab > div > div.cp-faq__content > div.cp-faq__panel > div.cp-faq__panel-list > div > div > div > .cp-faq__accordion-item')
    COMPANY = 'genesis'

    for div in selected_div_list:
        # print(div)
        category = div.select_one('div > a > strong').text
        title = div.select_one('div > a').get('title')
        question = f"{category} {title}"
        answer = div.select_one('div > .accordion-panel').text
        with get_connection() as conn:
            with conn.cursor() as cur:
                try:
                    sql = '''
                        INSERT INTO faq (idfaq, company, question, answer)
                        VALUES (%s, %s, %s, %s)
                    '''
                    cur.execute(sql, (None, COMPANY, question, answer))
                except Exception as e:
                    print(f'e: {e}')
                conn.commit()
        # print(category, question)
        # print(answer)
        # answer = dl.select_one('dd > .exp').text
        
    time.sleep(10)

set_hyundai_dynamic_crawling_option()
crawl_hyundai_faq()
crawl_genesis_faq()