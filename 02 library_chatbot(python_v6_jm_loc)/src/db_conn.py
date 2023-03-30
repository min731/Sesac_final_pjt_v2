import pymysql

class Database:
    # 데이터베이스에 연결
    def __init__(self):
        self.conn = pymysql.connect(host='127.0.0.1', user='root', password='1234', db='lib_total', charset='utf8')
        self.cur = self.conn.cursor()
        self.curdic = self.conn.cursor(pymysql.cursors.DictCursor)
    
    
    # 도서명으로 DB 검색
    # ['통합도서코드', '도서코드', 'isbn', '도서명', '저자명', '대출여부', '장르', '이미지', '소개글']
    
    def loc_list(self, lib_nm):
        search_sql = f'''SELECT * 
                        from (select * 
                                from search_book_t_1
                                where library_nm like '%{lib_nm}%'
                                order by t_book_cd asc, rent_yn asc
                                limit 18446744073709551615) as sc
                        group by isbn
                        order by rent_yn asc;'''
        self.curdic.execute(search_sql)
        result = self.curdic.fetchall()
        return result
    
    
    
    def search_book(self, title=None, author=None, lib_nm=None):
        search_sql = f'''SELECT *
                        FROM (SELECT * 
                                FROM search_book_t_1
                                WHERE TITLE LIKE '%{title}%'
                                AND AUTHOR LIKE '%{author}%'
                                AND LIBRARY_NM like '%{lib_nm}%'
                                ORDER BY T_BOOK_CD ASC, RENT_YN ASC
                                LIMIT 18446744073709551615) AS ORDER_SC
                        GROUP BY ISBN
                        ORDER BY RENT_YN ASC
                        ;'''
        
        self.cur.execute(search_sql)
        result = self.cur.fetchall()
        print("타이틀검색부분에서 확인", result)
        return result
    

    # 추천도서 DB 검색
    # ['도서코드', 'isbn', '도서명', '저자명', '대출여부', '장르', '이미지', '소개글']
    def recommend_book(self, search_list):
        
        if len(search_list) != 0:
            sql = f'''select * 
                    from search_book_t_1
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