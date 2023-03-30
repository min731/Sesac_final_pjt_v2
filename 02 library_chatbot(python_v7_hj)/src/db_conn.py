import pymysql
from itertools import combinations

class Database:
    # 데이터베이스에 연결
    def __init__(self):
        self.conn = pymysql.connect(host='127.0.0.1', user='root', password='1234', db='lib_total', charset='utf8')
        # self.cur = self.conn.cursor()
        self.curdic = self.conn.cursor(pymysql.cursors.DictCursor)
    
    
    # 도서명으로 DB 검색
    # ['통합도서코드', '도서코드', 'isbn', '도서명', '저자명', '대출여부', '장르', '이미지', '소개글']
    
    def loc_list(self, lib_nm):
        search_sql = f'''SELECT * 
                        from (select * 
                                from search_book_t
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
                                FROM search_book_t
                                WHERE TITLE LIKE '%{title}%'
                                AND AUTHOR LIKE '%{author}%'
                                AND LIBRARY_NM like '%{lib_nm}%'
                                ORDER BY T_BOOK_CD ASC, RENT_YN ASC
                                LIMIT 18446744073709551615) AS ORDER_SC
                        GROUP BY ISBN
                        ORDER BY RENT_YN ASC
                        ;'''
        
        self.curdic.execute(search_sql)
        result = self.curdic.fetchall()
        print("타이틀검색부분에서 확인", result)
        return result
    


    # 추천도서 DB 검색
    # ['도서코드', 'isbn', '도서명', '저자명', '대출여부', '장르', '이미지', '소개글']
    def recommend_book(self, genre_list=None, lib_nm=None):
        
        n = len(genre_list)
        res = 3
        
        if n == 0:
            return
        
        final_num = 3
        final_list = []
        
        for i in range(n+1, 0, -1):
            for choice in combinations(genre_list, i):
                m = len(choice)
                
                if lib_nm != '':
                    if m != 0:
                        sql = f'''select * 
                                from (
                                    select *
                                    from (
                                        select * 
                                        from search_book_t
                                        order by rent_yn asc limit 18446744073709551615) as ord_tmp
                                    group by title ) as grp_tmp
                                where library_nm like '%{lib_nm}%'
                                and genre like "%{choice[0]}%"'''
                    
                    if m > 1:
                        for k in range(1, m):
                            sql += f'''\n and genre like "%{choice[k]}%"'''
                            
                    sql += '''\n order by rent_SUM DESC, rent_yn asc, rand() limit 3;'''
                    
                else:
                    if m != 0:
                        sql = f'''select * 
                                from (
                                    select *
                                    from (
                                        select * 
                                        from search_book_t
                                        order by rent_yn asc limit 18446744073709551615) as ord_tmp
                                where genre like "%{choice[0]}%"'''
                    
                    if m > 1:
                        for k in range(1, m):
                            sql += f'''\n and genre like "%{choice[k]}%"'''
                            
                    sql += '''\n order by rent_SUM DESC, rent_yn asc, rand() limit 3;'''
                
                self.curdic.execute(sql)
                result = self.curdic.fetchmany(res)
                
                # print(choice, '#@%@#^$#^&@%^@', result)
            
                for x in range(len(result)):
                    if len(final_list) < final_num:
                        final_list.append(result[x])

                    else:
                        return final_list
                
                if len(result) >= final_num:
                    return result
                        