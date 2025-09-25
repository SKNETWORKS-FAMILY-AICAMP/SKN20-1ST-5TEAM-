from code.db.db_connect import get_connection

class VehicleRepository:
    def insert_dim_month(self, cur, int_date, year, month):
        sql = """
            INSERT INTO dim_monthly (date_key, year, month)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE
                year = VALUES(year),
                month = VALUES(month)
        """
        cur.execute(sql, (int_date, year, month))

    def insert_eco_monthly(self, cur, int_date, electric, hybrid, hydrogen, etc, cng):
        sql = "INSERT INTO eco_monthly (date_key, ev, hev, fcev, etc, cng) VALUES (%s, %s, %s, %s, %s, %s)"
        cur.execute(sql, (int_date, electric, hybrid, hydrogen, etc, cng))

    def insert_ice_monthly(self, cur, int_date, gasoline, diesel, lpg):
        sql = "INSERT INTO ice_monthly (date_key, gasoline, diesel, lpg) VALUES (%s, %s, %s, %s)"
        cur.execute(sql, (int_date, gasoline, diesel, lpg))

    def save(self, data_list):
        with get_connection() as conn:
            with conn.cursor() as cur:
                for data in data_list:
                    try:
                        self.insert_dim_month(cur, data["int_date"], data["year"], data["month"])
                        self.insert_eco_monthly(cur, data["int_date"], data["electric"], data["hybrid"], data["hydrogen"], data["etc"], data["cng"])
                        self.insert_ice_monthly(cur, data["int_date"], data["gasoline"], data["diesel"], data["lpg"])
                    except Exception as e:
                        print(f'e: {e}')
                conn.commit()