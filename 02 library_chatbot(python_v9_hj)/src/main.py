from keras.models import load_model
from collections import deque
from sentence_transformers import SentenceTransformer
import torch
import pandas as pd
import answer
import node
import re


def set_node_list1():

    #local_path 이미 선언
    local_path = 'C:/Users/user/Documents/GitHub/hj_sesac_final_pjt/FINAL_CHATBOT_PROJECT(~ing)/02 library_chatbot(python_v7_hj)/'

    # 모델 로드
    print("의도 분류 모델 로딩 중...")
    intent_classify_model = load_model(local_path+'models/CNN_library_involve_name_4_labels_location.h5')
    print("의도 분류 모델 로딩 완료...")

    # sbert 모델 한번 다운 후 로딩해서 사용 (시간 절약)
    # print("<System> sbert 다운 중...")
    # sbert_model = SentenceTransformer('snunlp/KR-SBERT-V40K-klueNLI-augSTS')
    # print("<System> sbert 다운 완료...")
    # print("<System> sbert 저장 중...")
    # sbert_model.save(local_path+'models/saved_KR_sbert_model')

    print("<System> sbert 로드 중...")
    sbert_model = SentenceTransformer(local_path+'models/saved_KR_sbert_model')
    # saved_KR_sbert_model = SentenceTransformer(local_path+'models/saved_KR_sbert_model')
    print("<System> sbert 로드 완료...")
    
    # 통합 문의 데이터 로드
    print("<System> 문의 csv, emd 데이터 로드 중...")
    inquiry_data_all = pd.read_csv(local_path+'data/csv/inquiry/inquiry_all.csv',encoding='cp949')
    inquiry_embedding_data_all = torch.load(local_path+'data/embedding_data/inquiry_embedding_data_all.pt')

    # 개별 문의 데이터 로드
    # 광진
    inquiry_data_GWJ = pd.read_csv(local_path+'data/csv/inquiry/inquiry_GWJ.csv',encoding='cp949')
    # inquiry_embedding_data_GWJ = torch.load(local_path+'data/embedding_data/inquiry_embedding_data_GWJ.pt')
    # 자양
    inquiry_data_JAY = pd.read_csv(local_path+'data/csv/inquiry/inquiry_JAY.csv',encoding='cp949')
    # inquiry_embedding_data_JAY = torch.load(local_path+'data/embedding_data/inquiry_embedding_data_JAY.pt')
    # 군자
    inquiry_data_GUJ = pd.read_csv(local_path+'data/csv/inquiry/inquiry_GUJ.csv',encoding='cp949')
    # inquiry_embedding_data_GUJ = torch.load(local_path+'data/embedding_data/inquiry_embedding_data_GUJ.pt')
    # 합정
    inquiry_data_HJ = pd.read_csv(local_path+'data/csv/inquiry/inquiry_HJ.csv',encoding='cp949')
    # inquiry_embedding_data_HJ = torch.load(local_path+'data/embedding_data/inquiry_embedding_data_HJ.pt')
    print("<System> 문의 csv, emd 데이터 로드 완료...")

    # node 생성1
    node1 = node.Node("<System> 의도 분류 모델 작동")
    node1.set_key(1)
    node1.set_model(intent_classify_model)

    node2 = node.Node("<System> (조회) 도서명,작가명 Tokenizer 작동, 도서명 혹은 작가명 틀릴 시 초기화")
    node2.set_key(2)

    node3 = node.Node("<System> (추천) 알고리즘 작동")
    node3.set_key(3)

    node4 = node.Node("<System> (문의사항)문장 유사도 모델 작동")
    node4.set_key(4)
    node4.set_model(sbert_model) #sbert_model
    node4.set_emd_data(inquiry_data_all,inquiry_embedding_data_all)
    node4.set_emd_data(inquiry_data_GWJ,inquiry_embedding_data_all)
    node4.set_emd_data(inquiry_data_JAY,inquiry_embedding_data_all)
    node4.set_emd_data(inquiry_data_GUJ,inquiry_embedding_data_all)
    node4.set_emd_data(inquiry_data_HJ,inquiry_embedding_data_all)

    return node1, node2, node3, node4

def set_node_list2():

    # node 생성2

    node5 = node.Node("<System> (negative) 예외 처리 클래스, 데이터 수집 후 초기화")
    node5.set_key(5)

    node6 = node.Node("<System> DB 접근 후 도서 유무 확인")
    node6.set_key(6)

    node7 = node.Node("<System> 도서 보유 , 대출 가능 or 불가능 확인")
    node7.set_key(7)

    node8 = node.Node("<System> 도서 미보유 , node1으로")
    node8.set_key(8)

    return node5, node6, node7, node8

def set_graph(node1,node2,node3,node4,node5,node6,node7,node8):

    # 그래프 설정
    graph = [
            [],
            [node2, node3, node4,node5],
            [node6],
            [],
            [],
            [],
            [node7,node8],
            [],
            []
            ]

    # 노드별로 방문 정보를 리스트로 표현
    visited = [False] * 9

    return graph, visited

## BFS 메서드 정의
def bfs (graph, node, visited,user_input,btn_intent):

    # Answer 인스턴스
    # 도서명, 작가명 등의 정보를 기록할 객체
    ans = answer.Answer()

    # 큐 구현을 위한 deque 라이브러리 활용
    queue = deque([node])
    
    # 큐가 완전히 빌 때까지 반복
    while queue:

        # 큐에 삽입된 순서대로 노드 하나 꺼내기
        poped_node = queue.popleft()

        # 현재 노드를 방문 처리
        visited[poped_node.get_key()] = True

        print("<System> 현재 visited: ", visited)

        # 탐색 순서 출력
        # print(poped_node.get_key(), end = ' ')

        ans , next_node = poped_node.task(graph,poped_node,user_input,ans,btn_intent)

        # 현재 처리 중인 노드에서 방문하지 않은 인접 노드를 모두 큐에 삽입
        for idx, node in enumerate(graph[poped_node.get_key()]):

            if idx != next_node.get_rmv_idx():
                visited[node.get_key()] = True

            print("<System> 현재 visited: ", visited)
            
            if not (visited[node.get_key()]):

                queue.append(node)
                # print("<System> 현재 visited: ", visited)
                
    return ans
       
def chatbot_start(user_input,btn_intent):

    print("<System> 챗봇 초기화!")

    node1, node2, node3, node4 = set_node_list1()
    node5, node6, node7, node8= set_node_list2()
    graph, visited = set_graph(node1, node2, node3, node4,node5, node6, node7, node8)
    
    print("<System> 챗봇 작동 시작!")
    print(f'''챗봇: 안녕하세요. 새싹 스마트 도서관입니다.
              현재 대화 내용은 보다 더 나은 서비스 
              개선을 위해 수집될 수 있습니다.
              무엇을 도와드릴까요?''')
    
    ans = bfs(graph, node1, visited,user_input,btn_intent)
    
    return ans

# 주고 받는 data
#         (string)
# spring    ==>     flask
#           <==
#          (json)

# string 객체 주입
print('입력하세요')
user_input = input().upper()
user_input = re.sub('([ㄱ-ㅎㅏ-ㅣ]+)', '', user_input)
# user_input = '로맨스 장르 소설 찾아서 추천해봐'.upper()

# btn_intent 추가
btn_intent = -1

# 실행 (Answer 인스턴스 반환)
ans = chatbot_start(user_input,btn_intent)