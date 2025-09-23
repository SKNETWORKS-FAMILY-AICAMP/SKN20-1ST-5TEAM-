from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys  # enter키 등을 입력하기위해서
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

url = 'https://stat.eseoul.go.kr/statHtml/statHtml.do?orgId=201&tblId=DT_201004_I020004&conn_path=I2&obj_var_id=&up_itm_id='
#웹 드라이버를 자동으로 설치하고 최신버전을 유지
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

# 사이트 접속
driver.get(url)
driver.maximize_window() # 전체 화면으로 실행  옵션
print('사이트 접속했습니다.')
# 사이트가 로드될때까지 기다린다.
time.sleep(1)
#################################


# 시점 클릭
view_point= driver.find_element(By.XPATH,'//*[@id="tabTimeText"]/a')
view_point.click()
time.sleep(2)


checkbox_month = driver.find_element(By.XPATH, '//*[@id="checkM"]')
if checkbox_month.is_selected():  # 체크되어 있으면
    checkbox_month.click()        # 체크 해제
    time.sleep(2)
else:
    print("이미 체크 해제 상태, 그대로 둠")

checkbox_year = driver.find_element(By.XPATH,'//*[@id="checkY"]')
if not checkbox_year.is_selected():   # 체크가 안되어 있으면
    checkbox_year.click()             # 체크하기
    time.sleep(2)
else:
    print("이미 체크되어 있음, 그대로 둠")


start_year = driver.find_element(By.XPATH, "//div[@id='timeY']//select[@title='시작 시점']")
Select(start_year).select_by_value('2019')
time.sleep(2)

end_year = driver.find_element(By.XPATH, "//div[@id='timeY']//select[@title='마지막 시점']")
Select(end_year).select_by_value('2020')
time.sleep(2)

search_btn = driver.find_element(By.XPATH,'//*[@id="searchStat"]')
search_btn.click()
time.sleep(5)

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


# 해당사이트에서 크롤링 하기
# 크롤링 할 데이터는 년도별, 친환경차(하이브리드,전기,수소)와 비환경(그 외)로 나눠서 수집
# 크롤링 한 데이터를 mysql에 넣기
