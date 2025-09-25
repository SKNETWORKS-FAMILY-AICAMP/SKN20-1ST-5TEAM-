import sys 
import os 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))) 

from vehicle_crawler import VehicleCrawler
from vehicle_repository import VehicleRepository

def main():
    crawler = VehicleCrawler()
    repo = VehicleRepository()

    crawler.start_dynamic_option_setting()
    crawler.run_matrix_steps()
    data_list = crawler.get_table_data()
    repo.save(data_list)
    crawler.quit()

if __name__ == "__main__":
    main()