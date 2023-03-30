import task

class Node:

    def __init__(self,info):

        # 노드 역할 설명
        self.info = info

        # 노드 별 모델
        self.model = None

        # 노드별 emd 데이터 리스트
        # 통합, 광진, 자양, 군자, 합정 순서
        self.emd_csv = []
        self.emd_pt = []

        # 데이터 (도서명 , 작가명, 장르, 대출 여부 , 대출 예약 여부)
        self.data = {}

        # 각 노드별 역할(task) 구분 키
        # 기본 key = -1
        self.key = -1

        # 다음 depth에서 제거할 노드의 idx
        self.rmv_idx = -1

    def get_info(self):
        return self.info

    def set_info(self,new_info):
        self.info = new_info

    def get_model(self):
        return self.model

    def set_model(self,model_obj):
        self.model = model_obj

    def get_emd_data(self):
        return self.emd_csv , self.emd_pt

    def set_emd_data(self,emd_csv,emd_pt):
        self.emd_csv.append(emd_csv)
        self.emd_pt.append(emd_pt)

    def get_key(self):
        return self.key

    def set_key(self,new_key):
        self.key = new_key

    def get_data(self):
        return self.data

    def set_data(self,key,value):
        data = self.get_data()
        data[key] = value
        self.data = data 

    def get_rmv_idx(self):
        return self.rmv_idx

    def set_rmv_idx(self,rmv_idx):
        self.rmv_idx = rmv_idx

    # 노드 별 역할 
    def task(self,graph,node,user_input,ans,btn_intent):

        print(node.get_info())
        next_node = None

        # 의도 분류(조회 or 추천 or 문의)
        if node.get_key() == 1:

            intent_classify_model = node.get_model()
            ans, input_label, user_input = task.intent_classify(ans, intent_classify_model,user_input)

            # CNN 의도분류 모델 Labelencoding 시 문의:0, 조회:1, 추천:2, negative:3 로 설정함

            # btn_intent 안눌렀을 때
            # default = -1
            if btn_intent == -1:
                print("<System> btn_intent 버튼 X")
                
                # 조회
                if input_label == 0:
                    print("next_node = node2")
                    next_node = graph[1][0] # node2
                    rmv_idx = 0

                # 추천
                elif input_label == 1:
                    print("next_node = node3")
                    next_node = graph[1][1] # node3
                    rmv_idx = 1

                # 문의
                elif input_label == 2:
                    print("next_node = node4")
                    next_node = graph[1][2] #node4
                    rmv_idx = 2
                    
                # 예외 (negative)
                elif input_label == 3:
                    print("next_node = node5")
                    next_node = graph[1][3] # node5
                    rmv_idx = 3

            # btn_intent 눌렀을 때
            # btn_intent != -1 일 때
            else :
                print("<System> btn_intent 버튼 O")
                
                if btn_intent == 0:
                    print("next_node = node2")
                    next_node = graph[1][0] # node2
                    rmv_idx = 0
            
                elif btn_intent == 1:
                    print("next_node = node3")
                    next_node = graph[1][1] # node3
                    rmv_idx = 1

                elif btn_intent == 2:
                    print("next_node = node4")
                    next_node = graph[1][2] #node4
                    rmv_idx = 2

                # 예외 (negative)
                elif btn_intent == 3:
                    print("next_node = node5")
                    print("의도분류 - negative 구현중...")
                    next_node = graph[1][3] # node5
                    rmv_idx = 3

                # ans 객체에 btn_intent set
                ans.set_btn_intent(btn_intent)


            # 다음 depth 에서 제거할 노드의 idx 설정
            next_node.set_rmv_idx(rmv_idx)

            # 다음 노드에게 정보 전달함
            next_node.set_data('user_input',user_input)

        # 의도 분류(조회) : 도서명 or 작가명 요청
        elif node.get_key() == 2:
            
            ans  = task.check_lname_bname_wname(ans,node.get_data()['user_input'])

            if ans.get_req_lname() == '' and ans.get_req_bname() == '' and ans.get_req_wname() == '':
                print("정확한 위치명이나 도서명 혹은 작가명을 입력해주세요.")
                ans.set_response("정확한 위치명이나도서명 혹은 작가명을 입력해주세요.")
                next_node = graph[6][1] # node8
            elif ans.get_req_lname() != '' or ans.get_req_bname() != '' or ans.get_req_wname() != '':
                next_node = graph[2][0] #node6
                next_node.set_rmv_idx(0)
                next_node.set_data('req_lname',ans.get_req_lname())
                next_node.set_data('req_bname',ans.get_req_bname())
                next_node.set_data('req_wname',ans.get_req_wname())
                # node2 ==> node5 자신의 인덱스를 rmv_idx 로
                # rmv_idx 디폴트 값은 -1 이기 때문


        # 의도 분류(추천) : 모델링 중
        elif node.get_key() == 3:
            
            print("의도 분류: 추천")
            
            ans = task.recommed_by_lname_gname(ans,user_input)

            next_node = None

        # 의도 분류(문의) : 문장 유사도 계산 후 답변 출력
        elif node.get_key() == 4:

            sbert_model = node.get_model()
            emd_csv , emd_pt = node.get_emd_data()

            ans = task.check_inquiry_ans(ans,user_input, sbert_model, emd_csv ,emd_pt)
            next_node = None
        
        # 의도 분류(negative) : 데이터 수집
        elif node.get_key() == 5:
            
            neg_data = node.get_data()['user_input']
            # neg_data 수집
            ans.set_response("챗봇: 죄송합니다. 이해할 수 없는 내용입니다.")
            ans.set_neg_data(neg_data)
            
        # DB에 책 있는지 확인
        elif node.get_key() == 6:
            
            ans, can_search  = task.check_is_in_library(ans,node)

            # 찾음
            if can_search == 0:
                next_node = graph[6][0] #node7
            # 못찾음
            elif can_search == 1:
                next_node = graph[6][1] #node8

            next_node.set_rmv_idx(can_search)
            next_node.set_data('in_lib_bname',ans.get_in_lib_bname())
            next_node.set_data('in_lib_wname',ans.get_in_lib_wname())

        # DB 검색 성공, 대출 가능 or 불가능 판단
        elif node.get_key() == 7:

            ans = task.check_can_borrow(ans,node)
            next_node = None
    
        # DB 검색 실패 , node1으로
        elif node.get_key() == 8:

            print("<System> DB 검색 실패")
            ans.set_response("챗봇 : 현재 관내(DB)에 없는 도서명 혹은 작가명입니다.다른 도서관을 이용해 주세요.")
            # next_node = None
            
        if next_node != None:
            print(next_node.get_info())

        # ans 객체 필드 출력
        ans.print_ans()

        return ans , next_node