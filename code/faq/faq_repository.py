from db.db_connect import get_connection

class FAQRepository:
    def insert_faq(self, cur, company, question, answer):
        sql = '''
            INSERT INTO faq (idfaq, company, question, answer)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                question = VALUES(question),
                answer = VALUES(answer)
        '''
        cur.execute(sql, (None, company, question, answer))

    def save(self, faq_list):
        with get_connection() as conn:
            with conn.cursor() as cur:
                for faq in faq_list:
                    try:
                        self.insert_faq(cur, faq["company"], faq["question"], faq["answer"])
                    except Exception as e:
                        print(f'e: {e}')
                conn.commit()