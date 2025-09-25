from vehicle.main import main as vehicle_main
# from faq.main import main as faq_main

def main():
    print("Vehicle 크롤링 시작")
    vehicle_main()
    print("FAQ 크롤링 시작")
    # faq_main()
    print("모든 크롤링 완료")

if __name__ == "__main__":
    main()