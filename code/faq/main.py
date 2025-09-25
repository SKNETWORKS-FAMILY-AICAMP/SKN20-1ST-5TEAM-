import sys 
import os 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))) 

from .faq_crawler import FAQCrawler
from .faq_repository import FAQRepository

def main():
    crawler = FAQCrawler()
    repo = FAQRepository()

    crawler.set_hyundai_dynamic_crawling_option()
    hyundai_faqs = crawler.crawl_hyundai_faq()
    repo.save(hyundai_faqs)

    genesis_faqs = crawler.crawl_genesis_faq()
    repo.save(genesis_faqs)

    crawler.quit()

if __name__ == "__main__":
    main()