# 같은 폴더/하위폴더의 *_car.xlsx를 찾아서
# (시도=소계 & 용도=계)의 '서울' 값만 뽑아 1st_project.ice_monthly에 업서트
import os, re, glob
import pandas as pd
import pymysql
from pathlib import Path
import os
from dotenv import load_dotenv
# ===== 설정 =====
load_dotenv()
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
CHARSET="utf8mb4"
DB_NAME = "1st_project"
TABLE   = "ice_monthly"                   # 컬럼: date_key, gasoline, diesel, lpg, cng
SHEET   = "10.연료별_등록현황"               # 시트명
DRY_RUN = False                           # True면 DB에 안 씀(프리뷰만)
# ==============


BASE = Path(__file__).resolve().parent
PATTERNS = [
    "**/*_car.xlsx", "**/*car*.xlsx", "**/*자동차*등록*통계*.xlsx"
]

def find_files():
    files = []
    for pat in PATTERNS:
        files += glob.glob(str(BASE / pat), recursive=True)
    files = sorted({str(Path(f)) for f in files})
    print(f"[INFO] 발견 {len(files)}개 파일")
    for f in files: print(" -", Path(f).name)
    return files

def date_key_from_filename(name: str):
    for rx in [
        r'(?<!\d)(20\d{2})[_\-]([01]?\d)(?!\d)',   # 2023_12 / 2023-12
        r'(?<!\d)(20\d{2})([01]\d)(?!\d)',         # 202312
        r'(20\d{2})\s*년\D*([01]?\d)\s*월',        # 2023년 12월
    ]:
        m = re.search(rx, name)
        if m:
            yyyy, mm = int(m.group(1)), int(m.group(2))
            if 1 <= mm <= 12:
                return yyyy*100 + mm
    return None

def extract_values(path: str):
    raw = pd.read_excel(path, sheet_name=SHEET, header=None, engine="openpyxl")

    # 헤더 줄(연료 & 서울 포함) 찾기
    header_idx = None
    for i in range(min(60, len(raw))):
        row = raw.iloc[i].astype(str).fillna("")
        if ("연료" in "".join(row)) and ("서울" in "".join(row)):
            header_idx = i; break
    if header_idx is None:
        raise RuntimeError("헤더 행을 찾지 못함")

    data = raw.iloc[header_idx+1:].reset_index(drop=True).copy()
    hdr  = raw.iloc[header_idx].astype(str).fillna("")
    seoul_idx = int(hdr.str.contains("서울").idxmax())

    # 연료열(내용 기반)
    fuel_candidates = ["휘발유","경유","LPG"]
    def hit(c):
        s = data[c].astype(str)
        return sum(s.str.contains(k, na=False).sum() for k in fuel_candidates)
    fuel_idx = max(data.columns, key=hit)

    # 같은 행의 문자열 열 어디에든 '소계'와 '계'가 모두 있는 행만 채택
    obj_cols = data.select_dtypes(include="object").columns

    def pick(kor_regex: str):
        fuel_mask = data[fuel_idx].astype(str).str.contains(kor_regex, na=False, regex=True)
        if not fuel_mask.any(): return 0
        block = data.loc[fuel_mask, obj_cols].astype(str)
        ok = block.apply(lambda r: ("소계" in "".join(r)) and ("계" in "".join(r)), axis=1)
        if not ok.any(): return 0
        ridx = ok[ok].index[0]
        val  = str(data.iat[ridx, seoul_idx]).replace(",", "").strip()
        try:   return int(float(val))
        except: return 0

    return {
        "gasoline": pick(r"휘발유"),
        "diesel"  : pick(r"경유"),
        "lpg"     : pick(r"LPG|엘피지|액화석유"),
        
    }
def upsert(date_key: int, v: dict):
    conn = pymysql.connect(
      host=DB_HOST,
      user=DB_USER,
      password=DB_PASSWORD,
      database=DB_NAME,
      charset=CHARSET
    )
    try:
        with conn.cursor() as cur:
            # FK 대비(없으면 무시)
            try:
                cur.execute(
                    "INSERT IGNORE INTO `1st_project`.`dim_month` (date_key) VALUES (%s)",
                    (date_key,)
                )
            except Exception:
                pass

            sql = f"""
            INSERT INTO `1st_project`.`{TABLE}` (date_key, gasoline, diesel, lpg)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
              gasoline=VALUES(gasoline),
              diesel  =VALUES(diesel),
              lpg     =VALUES(lpg)
            """
            cur.execute(sql, (
                int(date_key),
                int(v.get("gasoline", 0) or 0),
                int(v.get("diesel", 0)   or 0),
                int(v.get("lpg", 0)      or 0),
            ))
        conn.commit()
        print(f"[OK] {DB_NAME}.{TABLE} upsert {date_key} -> {v}")
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()



def main():
    files = find_files()
    if not files:
        print("처리할 파일이 없습니다. (스크립트 폴더/하위폴더 확인)")
        return

    for f in files:
        name = Path(f).name
        dk = date_key_from_filename(name)
        if not dk:
            print(f"[SKIP] date_key 파싱 실패: {name}"); continue
        try:
            vals = extract_values(f)
            print(f"[PREVIEW] {name} -> {dk} {vals}")
            if not DRY_RUN:
                upsert(dk, vals)
        except Exception as e:
            print(f"[ERR] {name}: {e}")

if __name__ == "__main__":
    main()
