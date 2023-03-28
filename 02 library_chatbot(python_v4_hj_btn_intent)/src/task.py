# from tensorflow.keras import preprocessing
from keras_preprocessing.sequence import pad_sequences
import preprocess
import pandas as pd
import torch
from sentence_transformers import util
import numpy as np
import pickle
import db_conn

local_path = 'C:/Users/user/Documents/GitHub/hj_sesac_final_pjt/FINAL_CHATBOT_PROJECT(~ing)/02 library_chatbot(python_v4_hj)/'
p = preprocess.Preprocess(word2index_dic=local_path+'data/dic/chatbot_dict.bin' ,userdic=local_path+'data/dic/userdict_intent_classify_v3(library)_all_bname_wname_v2.txt')
# database = pd.read_csv(local_path+'/data/csv/intent_classify/intent_classify_v3_database(library).csv',encoding='cp949')
db = db_conn.Database()


## node1: 의도 분류 (조회,추천,문의사항)
def intent_classify(ans, intent_classify_model,user_input):

    user_input_list = []
    user_input_list.append(user_input)

    input_predicted = intent_classify_model.predict(sentences_to_idx(user_input_list))
    print("<System> 의도 예측 확률", input_predicted)
    input_predicted = input_predicted.argmax(axis=-1)
    print("<System> 가장 높은 확률 input_predicted: ", input_predicted)

    # input_predicted[0] : 0 == 문의 , 1 == 검색 , 2 == 추천 
    ans.set_intent(input_predicted[0])

    return ans, input_predicted[0], user_input

def sentences_to_idx(intents_list):
    sequences = []
    check_keywords = True
    # text는 모든 문장들의 list
    for sentence in intents_list:

        # 문장을 [(단어1,품사1),(단어2,품사2)...] 로 변환
        pos = p.pos(sentence)

        # get_keywords(pos, without_tag=True) => 불용어 처리 후 품사(태그)없이 단어들만의 list
        # keywords : 불용어 처리된 [(단어1,품사1),(단어2,품사2)...], list형
        keywords = p.get_keywords(pos, without_tag=True)
        print_keywords = p.get_keywords(pos, without_tag=False)

        # 첫번째 keywords 와 sequence[0] 어떻게 대응되는지 체크해보고 싶음
        if check_keywords is True:
            print(print_keywords)
            check_keywords = False
        # 태그없이 '단어'만 있는 keywords에서 [[단어1,단어2],[단어1,단어2,단어3]...]들을 인덱싱해줌
        # 우리가 만든 단어사전에 없으면(OOV token이므로 인덱스 1로 고정)
        seq = p.get_wordidx_sequence(keywords)
        sequences.append(seq)

    # 조회, 추천, 문의 의도 분류 데이터 tokenize 시 최대 형태소 길이
    max_len = 15

    input_test = pad_sequences(sequences, maxlen=max_len)

    return input_test

## node2: (조회) 도서명, 작가명 인식 Tokenizer 작동
def check_bname_wname(ans,user_input):

    # DB 상 외의 모든 도서명, 작가명 파일 필요
    # 예시로 작성
    # book_list = ['크리스마스 피그','데미안','유다','유다2','유다3','유다4','파란 책']
    # writer_list = ['J.K.롤링','헤르만 헤세','아모스 오즈','정민']
    
    with open(local_path+'data/dic/all_bname_list_v2.pkl','rb') as f1:
        all_bname_list = pickle.load(f1)

    with open(local_path+'data/dic/all_wname_list_v2.pkl','rb') as f2:
        all_wname_list = pickle.load(f2)

    
    req_bname = ""
    req_wname = ""
    
    pos = p.pos(user_input)
    keywords = p.get_keywords(pos, without_tag=False)
    print("<System> 형태소 분해 : ", keywords)
    for keyword, tag in keywords:
        if tag == 'NNP':
            if keyword in all_bname_list:
                print("<System> 도서명 확인")
                req_bname = keyword
                # 도서명있으면 작가명 알 수 있음 => return
                ans.set_req_bname(req_bname)
                # ans.set_req_wname(wname)
            
            elif keyword in all_wname_list:
                print("<System> 작가명 확인")
                req_wname = keyword
                # ans.set_req_bname(bname)
                ans.set_req_wname(req_wname)
                # 작가명 알지만 이후 토큰에서 도서명까지 받을 수도 있음

    return ans


## node3 : (추천) 장르명 추천

def recommed_by_gname(ans,user_input):

    with open(local_path+'data/dic/all_gname_list.pkl','rb') as f3:
        all_gname_list = pickle.load(f3)

    req_gname_list = []
    
    pos = p.pos(user_input)
    keywords = p.get_keywords(pos, without_tag=False)
    print("<System> 형태소 분해 : ", keywords)
    for keyword, tag in keywords:
        if tag == 'NNG':
            if keyword in all_gname_list:
                print("<System> 장르명 확인")
                req_gname_list.append(keyword)
                # req, in_lib에 각각 넣음
                ans.set_req_gname(keyword)

    
    # 중복 제거
    req_gname_list = list(set(req_gname_list))
    
    response_gnames = ''
    for req_gname in req_gname_list:
        
        # 중복제거 후 in_lib에 넣음
        # ex) req_gname = ['소설','소설']
        #     in_lib = ['소설']
        ans.set_in_lib_gname(req_gname)
        
        # 답변할 str 
        # ex) response_gnames = 소설, 에세이 
        response_gnames+=req_gname+','
    
    in_lib_gname = ans.get_in_lib_gname()
    
    result = db.recommend_book(in_lib_gname)

    for i in range(len(result)):
        ans.set_search_bcode(result[i][0])
        ans.set_search_bname(result[i][2])
        ans.set_search_wname(result[i][3])
        ans.set_search_gname(result[i][5])
        ans.set_borrowable(result[i][4])
        ans.set_imgURL(result[i][6])
        ans.set_intro(result[i][7])
            
    # 마지막 , 이면 제거
    response_gnames = response_gnames.rstrip(',')

    ans.set_response("챗봇 : " + response_gnames + " 장르에 해당하는 추천도서 목록입니다.")
      
    return ans
    
    
 
## node4 : (문의) 5가지 기타 문의 사항
def check_inquiry_ans(ans,user_input, sbert_model, emd_csv ,emd_pt):

    sentence = user_input
    model = sbert_model
    data = emd_csv
    embedding_data = emd_pt

    # 띄어쓰기 제거
    sentence = sentence.replace(" ","")
    # 인코딩
    sentence_encode = model.encode(sentence)
    # 텐서화
    sentence_tensor = torch.tensor(sentence_encode)
    # 텐서화된 입력값과 문의 데이터 비교
    cos_sim = util.cos_sim(sentence_tensor, embedding_data)
    # 가장 큰 문장유사도 인덱스
    best_sim_idx = int(np.argmax(cos_sim))
    # 가장 큰 문장유사도 인덱스의 질문
    sentence_qes = data['input'][best_sim_idx]
    print(f"<System> 선택된 질문 = {sentence_qes}")
    print(f'<System> util.cos_sim 활용 코사인 유사도 : {cos_sim[0][best_sim_idx]}')

    # 가장 큰 유사도 인데스에 대응하는 답변 출력
    inquiry_ans = data['output'][best_sim_idx]
    print("챗봇 : ",inquiry_ans)

    ans.set_response(inquiry_ans)
    
    return ans

## node6 : 도서명, 작가명 책이 도서관에 있는지 확인
def check_is_in_library(ans,node):

    # 찾음 = 0 , 못찾음 = 1 
    can_search = 1

    req_bname = node.get_data()['req_bname'] 
    req_wname = node.get_data()['req_wname']

    # db_bname_list = database['bname'].tolist()
    # db_wname_list = database['wname'].tolist()
    
    # 도서관 도서명, 작가명 list 불러오기    
    with open(local_path+'data/dic/lib_bname_list_v2.pkl','rb') as f4:
        lib_bname_list = pickle.load(f4)

    with open(local_path+'data/dic/lib_wname_list_v2.pkl','rb') as f5:
        lib_wname_list = pickle.load(f5)
    
    # 도서관 도서명, 작가명 parser 불러오기 (dict타입)
    with open(local_path+'data/dic/lib_bname_parser_v2.pkl','rb') as f6:
        lib_bname_parser = pickle.load(f6)

    with open(local_path+'data/dic/lib_wname_parser_v2.pkl','rb') as f7:
        lib_wname_parser = pickle.load(f7)

    
    
    if req_bname != '':
        if req_bname in lib_bname_list:
            print("<System> 도서명 기반 검색 완료")
            # print(database[database['bname']==req_bname])
            ans.set_in_lib_bname(lib_bname_parser[req_bname])
            # ans.set_response("<System> 도서명 기반 검색 완료")
            # ans.set_response(str(database[database['bname']==req_bname]))
            can_search = 0

    elif req_wname != '':
        if req_wname in lib_wname_list:
            print("<System> 작가명 기반 검색 완료")
            # print(database[database['wname']==req_wname])
            ans.set_in_lib_wname(lib_wname_parser[req_wname])
            # ans.set_response("<System> 작가명 기반 검색 완료")
            # ans.set_response(str(database[database['wname']==req_wname]))
            can_search = 0

    else:
        print("<System> DB 상 존재하지 않는 도서명, 작가명 입니다.")
        ans.set_response("챗봇: DB 상 존재하지 않는 도서명, 작가명 입니다.")
        

    
        

    return ans, can_search

## node7 : 대출 가능 여부 확인
def check_can_borrow(ans,node):


    # 대출 예약 가능 여부: 대출 예약 가능 == 0, 대출 예약 불가 == 1
    # can_borrow_label = 1

    # DB에 확인된 도서명 or 작가명
    in_lib_bname = node.get_data()['in_lib_bname'] 
    in_lib_wname = node.get_data()['in_lib_wname'] 

    print("check_can_borrow 함수 실행")
    print(in_lib_bname)
    print(in_lib_wname)
    
    if in_lib_bname != '':
        search_result = db.search_title(in_lib_bname)
        for i in range(len(search_result)):
            ans.set_search_bcode(search_result[i][0])
            ans.set_search_bname(search_result[i][2])
            ans.set_search_wname(search_result[i][3])
            ans.set_search_gname(search_result[i][5])
            ans.set_borrowable(search_result[i][4])
            ans.set_imgURL(search_result[i][6])

            if search_result[i][3] == 0:
                ans.set_response(f"현재 '{search_result[i][1]}' 도서는 대출 가능합니다., 대출 예약을 원하시면 '대출 예약' 버튼을 눌러주세요.")
            elif search_result[i][3] == 1:
                ans.set_response(f"현재 '{search_result[i][1]}' 도서는 대출 중입니다., 반납 알림을 원하시면 '반납 알림' 버튼을 눌러주세요.")
            
    elif in_lib_wname != '':
        search_result = db.search_author(in_lib_wname)
        for i in range(len(search_result)):
            ans.set_search_bcode(search_result[i][0])
            ans.set_search_bname(search_result[i][2])
            ans.set_search_wname(search_result[i][3])
            ans.set_search_gname(search_result[i][5])
            ans.set_borrowable(search_result[i][4])
            ans.set_imgURL(search_result[i][6])
            if search_result[i][3] == 0:
                ans.set_response(f"현재 {search_result[i][1]} 도서는 대출 가능합니다. 대출 예약을 원하시면 '대출 예약' 버튼을 눌러주세요.")
            elif search_result[i][3] == 1:
                ans.set_response(f"현재 {search_result[i][1]} 도서는 대출 중입니다. 반납 알림을 원하시면 '반납 알림' 버튼을 눌러주세요.")
            
    return ans    
    
    
    

    # if in_lib_bname != '':
    #     if database.loc[database['bname']==in_lib_bname,'borrowable'].iloc[0] == 0:
    #         # can_borrow_label = 0
    #         print("챗봇 : 현재 ", in_lib_bname," 도서 대출이 가능합니다.대출 예약을 원하시면 '대출 예약' 버튼을 눌러주세요.")
    #         ans.set_response("챗봇 : 현재 " + in_lib_bname + " 도서 대출이 가능합니다.대출 예약을 원하시면 '대출 예약' 버튼을 눌러주세요.")

    #     else:
    #         print("챗봇 : 현재 ", in_lib_bname," 도서는 대출 중입니다. 반납 알림을 원하시면 '반납 알림' 버튼을 눌러주세요.")
    #         ans.set_response("챗봇 : 현재 " + in_lib_bname + " 도서는 대출 중입니다. 반납 알림을 원하시면 '반납 알림' 버튼을 눌러주세요.")

    # elif in_lib_wname != '':

    #     database_borrow_wname_borrowable_0 = database.loc[(database['wname']==in_lib_wname) & (database['borrowable']==0)]
    #     database_borrow_wname_borrowable_1 = database.loc[(database['wname']==in_lib_wname) & (database['borrowable']==1)]

    #     # 대출 가능한 목록
    #     if len(database_borrow_wname_borrowable_0) > 1:
    #         # can_borrow_label = 0
    #         print(database_borrow_wname_borrowable_0)
    #         print("챗봇 : " , in_lib_wname," 작가님의 작품들 중 대출 예약이 가능한 도서 목록입니다. 대출 예약을 원하시면 '대출 예약' 버튼을 눌러주세요.")
    #         ans.set_response(str(database_borrow_wname_borrowable_0))
    #         ans.set_response("챗봇 : " + in_lib_wname + " 작가님의 작품들 중 대출 예약이 가능한 도서 목록입니다. 대출 예약을 원하시면 '대출 예약' 버튼을 눌러주세요.")
    #     elif len(database_borrow_wname_borrowable_0) == 1:
    #         # can_borrow_label = 0
    #         print(database_borrow_wname_borrowable_0)
    #         print("챗봇 : " + in_lib_wname + " 작가님의 작품들 중 대출 예약이 가능한 도서입니다.대출 예약을 원하시면 '대출 예약'버튼을 눌러주세요.")
    #         ans.set_response(str(database_borrow_wname_borrowable_0))
    #         ans.set_response("챗봇 : " + in_lib_wname + " 작가님의 작품들 중 대출 예약이 가능한 도서입니다.대출 예약을 원하시면 '대출 예약'버튼을 눌러주세요.")

    #     # 대출 불가능한 목록
    #     if len(database_borrow_wname_borrowable_1) > 1:
    #         print(database_borrow_wname_borrowable_1)
    #         print("챗봇 : " , in_lib_wname," 작가님의 작품들 중 대출 중인  도서 목록입니다.반납 알림을 원하시면 '반납 알림' 버튼을 눌러주세요.")
    #         ans.set_response(str(database_borrow_wname_borrowable_1))
    #         ans.set_response("챗봇 : " + in_lib_wname + " 작가님의 작품들 중 대출 중인  도서 목록입니다.반납 알림을 원하시면 '반납 알림' 버튼을 눌러주세요.")
    #     elif len(database_borrow_wname_borrowable_1) == 1:
    #         # can_borrow_label = 0
    #         print(database_borrow_wname_borrowable_1)
    #         print("챗봇 : " + in_lib_wname + " 작가님의 대출 중인 도서입니다.'반납 알림을 원하시면 '반납 알림' 버튼을 눌러주세요.")
    #         ans.set_response(str(database_borrow_wname_borrowable_1))
    #         ans.set_response("챗봇 : " + in_lib_wname + " 작가님의 대출 중인 도서입니다.'반납 알림을 원하시면 '반납 알림' 버튼을 눌러주세요.")           


    #     if len(database_borrow_wname_borrowable_0) == 0:
    #         print("챗봇 : " , in_lib_wname," 작가님의 작품들은 모두 대출 중입니다. 반납 알림을 원하시면 '반납 알림' 버튼을 눌러주세요.")
    #         ans.set_response("챗봇 : " + in_lib_wname + " 작가님의 작품들은 모두 대출 중입니다. 반납 알림을 원하시면 '반납 알림' 버튼을 눌러주세요.")

    #     # ans.set_search_bname()
    #     # ans.set_search_wname()
    #     # ans.set_search_gname()
    # return ans

## node9 : 대출 가능, 대출 여부 확인

# def check_want_borrow(ans,node):
#     print("check_want_borrow 함수 진입")

#     if want_borrow_bname != "" :
#         print("챗봇 : " , want_borrow_bname," 대출 예약 해드릴까요?\n (대출 예약을 원하시면 대출 예약 버튼을 눌러주세요.)")
#         ans.set_response("챗봇 : " + want_borrow_bname + " 대출 예약 해드릴까요?\n (대출 예약을 원하시면 대출 예약 버튼을 눌러주세요.)")

#     elif want_borrow_wname != "":
#         print("챗봇 : " , want_borrow_bname," 작가님 도서들 중에서 대출 예약 원하시는 도서가 있으신가요?\n (원하시는 도서의 대출 예약 버튼을 눌러주세요.)")
#         ans.set_response("챗봇 : " + want_borrow_bname + " 작가님 도서 대출 예약 해드릴까요??\n (원하시는 도서의 대출 예약 버튼을 눌러주세요.)")
    
#     return ans





## node10 : 대출 불가능, 반납 알림 여부 확인

# def check_want_alarm(ans,want_alarm_bname,want_alarm_wname):
#     print("check_want_alarm 함수 진입")

#     if want_alarm_bname != "":
#         print("챗봇 : " , want_alarm_bname,"이(가) 반납되면 알림 드릴까요?\n (반납 알림을 원하시면 반납 알림 버튼을 눌러주세요.)")
#         ans.set_response("챗봇 : " + want_alarm_bname + "이(가) 반납되면 알림 드릴까요?\n (반납 알림을 원하시면 반납 알림 버튼을 눌러주세요.)")

#     elif want_alarm_wname != "":
#         print("챗봇 : " , want_alarm_wname,"의 책이 반납되면 알림 드릴까요?\n (반납 알림을 원하시는 책의 반납 알림 버튼을 눌러주세요.)")
#         ans.set_response("챗봇 : " + want_alarm_wname +"의 책이 반납되면 알림 드릴까요?\n (반납 알림을 원하시는 책의 반납 알림 버튼을 눌러주세요.)")

#     return ans