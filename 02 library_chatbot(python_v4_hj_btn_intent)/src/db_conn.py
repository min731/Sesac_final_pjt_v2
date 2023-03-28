import pymysql

class Database:
    # 데이터베이스에 연결
    def __init__(self):
        self.conn = pymysql.connect(host='127.0.0.1', user='root', password='1234', db='library_chatbot', charset='utf8')
        self.cur = self.conn.cursor()
    
    
    # 도서명으로 DB 검색
    # ['도서코드', 'isbn', '도서명', '저자명', '대출여부', '장르', '이미지', '소개글']
    def search_title(self, search_name):
        search_sql = f'''SELECT *
                        FROM (SELECT * 
                                FROM search_view
                                WHERE TITLE LIKE '%{search_name}%'
                                ORDER BY lib_book_cd ASC, RENT_YN ASC
                                LIMIT 18446744073709551615) AS ORDER_SC
                        GROUP BY ISBN
                        ORDER BY rent_yn ASC
                        ;'''
        
        self.cur.execute(search_sql)
        result = self.cur.fetchall()
        # print("타이틀검색부분에서 확인", result)
        return result
    
    
    # 작가명으로 DB 검색
    def search_author(self, search_name):
        search_sql = f'''SELECT *
                        FROM (SELECT * 
                                FROM search_view
                                WHERE AUTHOR_NM LIKE '%{search_name}%'
                                ORDER BY lib_book_cd ASC, RENT_YN ASC
                                LIMIT 18446744073709551615) AS ORDER_SC
                        GROUP BY ISBN
                        ORDER BY rent_yn ASC
                        ;'''
        
        self.cur.execute(search_sql)
        result = self.cur.fetchall()
        # print("작가검색부분에서 확인", result)
        return result


    # 추천도서 DB 검색
    # ['도서코드', 'isbn', '도서명', '저자명', '대출여부', '장르', '이미지', '소개글']
    def recommend_book(self, search_list):
        
        if len(search_list) != 0:
            sql = f'''select * 
                    from search_view
                    where genre like "%{search_list[0]}%"'''
        
        if len(search_list) > 1:
            for i in range(1, len(search_list)):
                sql += f'''\n and genre like "%{search_list[i]}%"'''
                
        # 대출가능한 책만 찾아야한다면 order by 앞에 [\n and rent_yn = 0] 추가해주기
        sql += '''\n order by rand() limit 3;'''
                           
        self.cur.execute(sql)
        result = self.cur.fetchall()
        
        print(result)
        
        return result    