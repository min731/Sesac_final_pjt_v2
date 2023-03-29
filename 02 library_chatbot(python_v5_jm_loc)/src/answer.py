# flask => spring 전달 객체 클래스
# ans = answer.Answer()

class Answer:

    def __init__(self):
        
        # 의도 분류 클래스
        self.intent = -1
        
        # 버튼 의도 분류 클래스
        self.btn_intent = -1

        # 요청 위치명
        # location name
        self.req_lname = ''

        # 요청 도서명
        self.req_bname = ''
        
        # 요청 작가명
        self.req_wname = ''
        
        # 요청 장르명
        self.req_gname = []

        # 보유 도서명
        self.in_lib_bname = ''
        
        # 보유 작가명
        self.in_lib_wname = ''
        
        # 보유 장르명
        self.in_lib_gname = []

        # 검색 도서코드
        self.search_bcode = []

        # 검색 도서명
        self.search_bname = []
        
        # 검색 작가명
        self.search_wname = []
        
        # 검색 장르명
        self.search_gname = []

        # 책 이미지
        self.imgURL = []
        
        # 소개글
        self.intro = []
        
        # 대출 가능 여부
        self.borrowable = []
        
        # 반납 알림 여부
        # self.alarm = []
        
        # 챗봇 답변
        self.response = []
        
        # (의도분류-negative) 예외 데이터 
        self.neg_data = []

    def get_intent(self):
        return self.intent
    
    def set_intent(self,intent):
        self.intent = intent
        
    def get_btn_intent(self):
        return self.btn_intent
    
    def set_btn_intent(self,btn_intent):
        self.btn_intent = btn_intent

    # 위치 getter, setter 추가
    def get_req_lname(self):
        return self.req_lname
    
    def set_req_lname(self,req_lname):
        self.req_lname = req_lname


    def get_req_bname(self):
        return self.req_bname
    
    def set_req_bname(self,req_bname):
        self.req_bname = req_bname

    def get_req_wname(self):
        return self.req_wname

    def set_req_wname(self,req_wname):
        self.req_wname = req_wname

    def get_req_gname(self):
        return self.req_gname
    
    def set_req_gname(self,req_gname):
        self.req_gname.append(req_gname)

    def get_in_lib_bname(self):
        return self.in_lib_bname
    
    def set_in_lib_bname(self,in_lib_bname):
        self.in_lib_bname = in_lib_bname

    def get_in_lib_wname(self):
        return self.in_lib_wname

    def set_in_lib_wname(self,in_lib_wname):
        self.in_lib_wname = in_lib_wname

    def get_in_lib_gname(self):
        return self.in_lib_gname
    
    def set_in_lib_gname(self,in_lib_gname):
        self.in_lib_gname.append(in_lib_gname)

    def get_search_bcode(self):
        return self.search_bcode
    
    def set_search_bcode(self,search_bcode):
        self.search_bcode.append(search_bcode)

    def get_search_bname(self):
        return self.search_bname
    
    def set_search_bname(self,search_bname):
        self.search_bname.append(search_bname)

    def get_search_wname(self):
        return self.search_wname
    
    def set_search_wname(self,search_wname):
        self.search_wname.append(search_wname)

    def get_search_gname(self):
        return self.search_gname
    
    def set_search_gname(self,search_gname):
        self.search_gname.append(search_gname)

    def get_imgURL(self):
        return self.imgURL
    
    def set_imgURL(self,imgURL):
        self.imgURL.append(imgURL)

    def get_intro(self):
        return self.intro
    
    def set_intro(self,intro):
        self.intro.append(intro)

    def get_borrowable(self):
        return self.borrowable
    
    def set_borrowable(self,borrowable):
        self.borrowable.append(borrowable)

    # def get_alarm(self):
    #     return self.alarm
    
    # def set_alarm(self,alarm):
    #     self.alarma.append(alarm)

    def set_response(self,response):
        self.response.append(response)

    def get_response(self):
        return self.response
    
    def set_neg_data(self,neg_data):
        self.neg_data.append(neg_data)
        
    def get_neg_data(self):
        return self.neg_data
    
    def print_ans(self):
        print("<System> ans 객체 필드 출력")
        print("<System> ans.intent : ", self.get_intent(), "( 0 == 검색 , 1 == 추천 , 2 == 문의, 3 == negative(예외) )")
        print("<System> ans.btn_intent : ", self.get_btn_intent(), "( 0 == 검색 , 1 == 추천 , 2 == 문의, 3 == negative(예외) )")
        print("<System> ans.req_lname : ", self.get_req_lname())
        print("<System> ans.req_bname : ", self.get_req_bname())
        print("<System> ans.req_wname : ", self.get_req_wname())
        print("<System> ans.req_gname : ", self.get_req_gname())
        print("<System> ans.in_lib_bname : ", self.get_in_lib_bname())
        print("<System> ans.in_lib_wname : ", self.get_in_lib_wname())
        print("<System> ans.in_lib_gname : ", self.get_in_lib_gname())
        print("<System> ans.search_bcode : ", self.get_search_bcode())
        print("<System> ans.search_bname : ", self.get_search_bname())
        print("<System> ans.search_wname : ", self.get_search_wname())
        print("<System> ans.search_gname : ", self.get_search_gname())
        print("<System> ans.imgURL : ", self.get_imgURL())
        print("<System> ans.intro : ", self.get_intro())
        print("<System> ans.borrowable : ", self.get_borrowable())
        print("<System> ans.response : ", self.get_response())
        print("<System> ans.neg_data : ", self.get_neg_data())