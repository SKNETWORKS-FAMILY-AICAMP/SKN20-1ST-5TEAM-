from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time

class VehicleCrawler:
    URL = 'https://stat.eseoul.go.kr/statHtml/statHtml.do?orgId=201&tblId=DT_201004_I020004&conn_path=I2&obj_var_id=&up_itm_id='

    def __init__(self):
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service)

    def start_dynamic_option_setting(self):
        driver = self.driver
        driver.get(self.URL)
        driver.maximize_window()
        time.sleep(1)
        driver.find_element(By.CSS_SELECTOR, "#header > div > div.titleRight > a.btnStaSet").click()
        time.sleep(3)
        iframe = driver.find_element(By.ID, "ifrSearchDetail")
        driver.switch_to.frame(iframe)
        driver.find_element(By.XPATH, '//*[@id="ifr_pop_selectAll2"]/div/div/div[3]/div[1]/div[2]/ul[2]/li[2]/img[2]').click()
        time.sleep(3)
        car_all_select = driver.find_element(By.ID, 'selectLeft_1')
        Select(car_all_select).select_by_value('001@1')
        time.sleep(3)
        driver.find_element(By.XPATH, '//*[@id="ifr_pop_selectAll2"]/div/div/div[3]/div[1]/div[2]/ul[2]/li[1]/img[2]').click()
        time.sleep(3)
        driver.find_element(By.XPATH, '//*[@id="ifr_pop_selectAll2"]/div/div/div[3]/div[3]/div/div[2]/ul[3]/li[1]/img[1]').click()
        time.sleep(3)
        apply_btn = driver.find_element(By.XPATH, '//*[@id="ifr_pop_selectAll2"]/div/div/div[4]/span/a')
        driver.execute_script("arguments[0].click();", apply_btn)
        driver.switch_to.default_content()
        time.sleep(3)

    def run_matrix_steps(self):
        driver = self.driver
        steps = [
            ('//*[@id="ico_swap"]/a', 5),
            ('//*[@id="Ri0"]', 1),
            ('//*[@id="pop_pivotfunc2"]/div[2]/div[1]/div[2]/p/a[2]/img', 1),
            ('//*[@id="Le0"]', 1),
            ('//*[@id="pop_pivotfunc2"]/div[2]/div[1]/div[1]/div/span/a[2]/img', 1),
            ('//*[@id="pop_pivotfunc2"]/div[2]/div[2]/span/a', 10)
        ]
        for xpath, wait_time in steps:
            driver.find_element(By.XPATH, xpath).click()
            time.sleep(wait_time)

    def get_table_data(self):
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        selected_tr = soup.select('#mainTable > tbody > tr')
        result = []

        def parse_int(value):
            if value is None or value.strip() == "" or value.strip() == "-":
                return 0
            try:
                return int(value.replace(",", ""))
            except (ValueError, AttributeError):
                return 0

        for tr in selected_tr:
            tds = tr.select('td')
            date = tds[0].get('title').strip()
            year, month = [x.strip() for x in date.split('.')]
            int_date = int(year) * 100 + int(month)
            gasoline = parse_int(tds[3].get('title'))
            diesel = parse_int(tds[4].get('title'))
            lpg = parse_int(tds[5].get('title'))
            electric = parse_int(tds[6].get('title'))
            cng = parse_int(tds[7].get('title'))
            hybrid = parse_int(tds[8].get('title'))
            hydrogen = parse_int(tds[9].get('title'))
            etc = parse_int(tds[10].get('title'))
            result.append({
                "int_date": int_date,
                "year": year,
                "month": month,
                "gasoline": gasoline,
                "diesel": diesel,
                "lpg": lpg,
                "electric": electric,
                "cng": cng,
                "hybrid": hybrid,
                "hydrogen": hydrogen,
                "etc": etc
            })
        return result

    def quit(self):
        self.driver.quit()