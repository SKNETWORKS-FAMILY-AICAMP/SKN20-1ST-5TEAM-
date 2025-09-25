from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from code.db.db_connect import get_connection
import time

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)
URL = 'https://stat.eseoul.go.kr/statHtml/statHtml.do?orgId=201&tblId=DT_201004_I020004&conn_path=I2&obj_var_id=&up_itm_id='

def start_dynamic_option_setting():
    driver.get(URL)
    driver.maximize_window() 
    time.sleep(1)   
    setting_btn = driver.find_element(By.CSS_SELECTOR, "#header > div > div.titleRight > a.btnStaSet")
    setting_btn.click()
    time.sleep(3)
    
    # iframe 전환
    iframe = driver.find_element(By.ID, "ifrSearchDetail")
    driver.switch_to.frame(iframe)

    # 종류 삭제
    car_variable_delete_btn = driver.find_element(By.XPATH, '//*[@id="ifr_pop_selectAll2"]/div/div/div[3]/div[1]/div[2]/ul[2]/li[2]/img[2]')
    car_variable_delete_btn.click()
    time.sleep(3)
    
    # 종류 전체 선택
    car_all_select = driver.find_element(By.ID, 'selectLeft_1')
    car_all_selected = Select(car_all_select)
    all = '001@1'
    car_all_selected.select_by_value(all)
    time.sleep(3)

    # 종류 전체 추가
    car_add_btn = driver.find_element(By.XPATH, '//*[@id="ifr_pop_selectAll2"]/div/div/div[3]/div[1]/div[2]/ul[2]/li[1]/img[2]')
    car_add_btn.click()
    time.sleep(3)

    # 기간 전체 선택
    period_all_add_btn = driver.find_element(By.XPATH, '//*[@id="ifr_pop_selectAll2"]/div/div/div[3]/div[3]/div/div[2]/ul[3]/li[1]/img[1]')
    period_all_add_btn.click()
    time.sleep(3)
    
    # 적용 버튼
    apply_btn = driver.find_element(By.XPATH, '//*[@id="ifr_pop_selectAll2"]/div/div/div[4]/span/a')
    driver.execute_script("arguments[0].click();", apply_btn)
    driver.switch_to.default_content()
    time.sleep(3)

def run_matrix_steps(driver):
    #행렬전환 실행
    steps = [
        ('//*[@id="ico_swap"]/a', 5),  # 매트릭스 버튼
        ('//*[@id="Ri0"]', 1),  # 시점 선택
        ('//*[@id="pop_pivotfunc2"]/div[2]/div[1]/div[2]/p/a[2]/img', 1),  # 시점 추가
        ('//*[@id="Le0"]', 1),  # 차종 선택
        ('//*[@id="pop_pivotfunc2"]/div[2]/div[1]/div[1]/div/span/a[2]/img', 1),  # 차종 이동
        ('//*[@id="pop_pivotfunc2"]/div[2]/div[2]/span/a', 1)  # 적용 버튼
    ]

    for xpath, wait_time in steps:
        element = driver.find_element(By.XPATH, xpath)
        element.click()
        time.sleep(wait_time)

def insert_dim_month(cur, int_date, year, month):
    # sql = "INSERT INTO dim_month VALUES (%s, %s, %s)"
    sql = """
        INSERT INTO dim_monthly (date_key, year, month)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE
            year = VALUES(year),
            month = VALUES(month)
    """
    cur.execute(sql, (int_date, year, month))

def insert_eco_monthly(cur, int_date, electric, hybrid, hydrogen, etc, cng):
    sql = "INSERT INTO eco_monthly (date_key, ev, hev, fcev, etc, cng) VALUES (%s, %s, %s, %s, %s, %s)"
    cur.execute(sql, (int_date, electric, hybrid, hydrogen, etc, cng))

def insert_ice_monthly(cur, int_date, gasoline, diesel, lpg):
    sql = "INSERT INTO ice_monthly (date_key, gasoline, diesel, lpg) VALUES (%s, %s, %s, %s)"
    cur.execute(sql, (int_date, gasoline, diesel, lpg))


def crawl_data():
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    selected_tr = soup.select('#mainTable > tbody > tr')

    for tr in selected_tr:
        tds = tr.select('td')
        date = tds[0].get('title').strip()
        year, month = [x.strip() for x in date.split('.')]
        int_date = int(year) * 100 + int(month)

        gasoline = int(tds[3].get('title').replace(",", ""))
        diesel = int(tds[4].get('title').replace(",", ""))
        lpg = int(tds[5].get('title').replace(",", ""))
        electric = int(tds[6].get('title').replace(",", ""))
        cng = int(tds[7].get('title').replace(",", ""))
        hybrid = int(tds[8].get('title').replace(",", ""))
        hydrogen = 0 if tds[9].get('title') == "-" else int(tds[9].get('title').replace(",", ""))
        etc = int(tds[10].get('title').replace(",", ""))

        with get_connection() as conn:
            with conn.cursor() as cur:
                try:
                    insert_dim_month(cur, int_date, year, month)
                    insert_eco_monthly(cur, int_date, electric, hybrid, hydrogen, etc, cng)
                    insert_ice_monthly(cur,int_date, gasoline, diesel, lpg)
                except Exception as e:
                    print(f'e: {e}')
                conn.commit()


start_dynamic_option_setting()
run_matrix_steps(driver)
time.sleep(3)
crawl_data()
time.sleep(10)
driver.quit()

    