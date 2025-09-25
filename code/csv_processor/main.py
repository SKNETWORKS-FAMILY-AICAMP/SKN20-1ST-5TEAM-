import sys 
import os 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))) 

from pathlib import Path
from .csv_processor import CsvProcessor
from .csv_repository import CsvRepository

SHEET = "10.연료별_등록현황"
DRY_RUN = False

def main():
    base = Path(__file__).resolve().parent
    
    processor = CsvProcessor(base, SHEET)
    repository = CsvRepository()

    files = processor.find_files()
    if not files:
        print("처리할 파일이 없습니다. (스크립트 폴더/하위폴더 확인)")
        return

    for f in files:
        name = Path(f).name
        dk = processor.date_key_from_filename(name)
        if not dk:
            print(f"[SKIP] date_key 파싱 실패: {name}")
            continue
            
        try:
            vals = processor.extract_values(f)
            print(f"[PREVIEW] {name} -> {dk} {vals}")
            if not DRY_RUN:
                repository.upsert(dk, vals)
        except Exception as e:
            print(f"[ERR] {name}: {e}")

if __name__ == "__main__":
    main()