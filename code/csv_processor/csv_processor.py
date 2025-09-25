import re
import glob
import pandas as pd
from pathlib import Path

class CsvProcessor:
    def __init__(self, base_path: Path, sheet_name: str):
        self.base_path = base_path
        self.sheet_name = sheet_name
        self.patterns = [
            "**/*_car.xlsx", 
            "**/*car*.xlsx", 
            "**/*자동차*등록*통계*.xlsx"
        ]

    def find_files(self):
        files = []
        for pat in self.patterns:
            files += glob.glob(str(self.base_path / pat), recursive=True)
        files = sorted({str(Path(f)) for f in files})
        print(f"[INFO] 발견 {len(files)}개 파일")
        for f in files: print(" -", Path(f).name)
        return files

    def date_key_from_filename(self, name: str):
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

    def extract_values(self, path: str):
        raw = pd.read_excel(path, sheet_name=self.sheet_name, header=None, engine="openpyxl")

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