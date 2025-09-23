from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys # enter키 등을 입력하기 위해서
from bs4 import BeautifulSoup
from db_chan import get_connection
import pymysql
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

def crawl_data():
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    all_data = []
    for tr in soup.select('#mainTable > tbody > tr'):
        row_data = [td.text.strip() for td in tr.select('td')]
        if row_data:
            all_data.append(row_data)

    dim_data = []
    for i, row in enumerate(all_data):
        if len(row) > 0:
            date_str = row[0]
        
        if '.' in date_str:
            # "2019.01" -> ["2019", "01"]
            year_str, month_str = date_str.split('.')
            year = int(year_str)  # 2019
            month = int(month_str)
            date_int = year*100 + month  # 201901
              # 1 (01 -> 1로 자동 변환)

        dim_data.append([date_int, year, month])
        # print(f"{date_int}, {year}, {month}")

    eco_data = []
    for i, row in enumerate(all_data):
        if len(row) > 10:  # 인덱스 10까지 존재하는지 확인
            # null, 빈 문자열, '-' 등을 0으로 처리
            ev = row[6] if row[6] and row[6].strip() not in ['', '-', 'null', 'NULL', 'None'] else '0'
            cng = row[7] if row[7] and row[7].strip() not in ['', '-', 'null', 'NULL', 'None'] else '0'
            hev = row[8] if row[8] and row[8].strip() not in ['', '-', 'null', 'NULL', 'None'] else '0'
            fcev = row[9] if row[9] and row[9].strip() not in ['', '-', 'null', 'NULL', 'None'] else '0'
            etc = row[10] if row[10] and row[10].strip() not in ['', '-', 'null', 'NULL', 'None'] else '0'

        eco_data.append([ev, cng, hev, fcev, etc])
        print(f"{ev}, {cng}, {hev}, {fcev}, {etc}")

    ice_data = []
    for i, row in enumerate(all_data):
        if len(row) > 5:
            gasoline = row[3] if row[3] and row[3].strip() not in ['', '-', 'null', 'NULL', 'None'] else '0'
            desel = row[4] if row[4] and row[4].strip() not in ['', '-', 'null', 'NULL', 'None'] else '0'
            lpg = row[5] if row[5] and row[5].strip() not in ['', '-', 'null', 'NULL', 'None'] else '0'

        ice_data.append([gasoline, desel, lpg])
        print(f"{gasoline}, {desel}, {lpg}")


    
    

    # td_span = soup.select('#mainTable > tbody > tr')
    # test = td_span[0].text.strip()
    # print(len(td_span))

    # with get_connection() as conn:
    #     with conn.cursor() as cur:
    #         try:
    #             sql = 'insert into shop_base2_tbl values(%s, %s, %s, %s, %s)'
    #             cur.execute(sql, (data[0], data[1], data[2], data[3], data[4]))
    #         except pymysql.err.IntegrityError:
    #             sql = '''update shop_base2_tbl
    #                         set shop_state=%s, shop_addr=%s, shop_phone_number=%s
    #                     where area=%s and shop_name=%s
    #             '''
    #             cur.execute(sql, (data[2], data[3], data[4], data[0], data[1]))
    #         conn.commit()

start_dynamic_option_setting()
# 행렬전환 클릭 함수
def click_matrix_element(driver, xpath, wait_time=1):
    element = driver.find_element(By.XPATH, xpath)
    element.click()
    time.sleep(wait_time)

# 행렬전환 순서
matrix_steps = [
    ('//*[@id="ico_swap"]/a', 5),  # 매트릭스 버튼 (5초 대기)
    ('//*[@id="Ri0"]', 1),  # 시점 선택
    ('//*[@id="pop_pivotfunc2"]/div[2]/div[1]/div[2]/p/a[2]/img', 1),  # 시점 추가
    ('//*[@id="Le0"]', 1),  # 차종 선택  
    ('//*[@id="pop_pivotfunc2"]/div[2]/div[1]/div[1]/div/span/a[2]/img', 1),  # 차종 이동
    ('//*[@id="pop_pivotfunc2"]/div[2]/div[2]/span/a', 1)  # 적용 버튼
]
# 행렬전환 작업 실행
for xpath, wait_time in matrix_steps:
    click_matrix_element(driver, xpath, wait_time)


time.sleep(30)

crawl_data()
time.sleep(10)
driver.quit()

    