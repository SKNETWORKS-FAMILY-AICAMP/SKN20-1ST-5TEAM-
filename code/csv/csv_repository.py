import os
import pymysql
from dotenv import load_dotenv

class CsvRepository:
    def __init__(self):
        load_dotenv()
        self.db_host = os.getenv("DB_HOST")
        self.db_user = os.getenv("DB_USER")
        self.db_password = os.getenv("DB_PASSWORD")
        self.charset = "utf8mb4"
        self.db_name = "1st_project"
        self.table = "ice_monthly"

    def upsert(self, date_key: int, v: dict):
        conn = pymysql.connect(
            host=self.db_host,
            user=self.db_user,
            password=self.db_password,
            database=self.db_name,
            charset=self.charset
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
                INSERT INTO `1st_project`.`{self.table}` (date_key, gasoline, diesel, lpg)
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
            print(f"[OK] {self.db_name}.{self.table} upsert {date_key} -> {v}")
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()