from vehicle.main import main as vehicle_main
from faq.main import main as faq_main
from csv_processor.main import main as csv_main

def main():
    # print("Vehicle 크롤링 시작")
    # vehicle_main()
    # print("FAQ 크롤링 시작")
    # faq_main()
    # print("모든 크롤링 완료")
    csv_main()
    print("모든 작업 완료")

if __name__ == "__main__":
    main()