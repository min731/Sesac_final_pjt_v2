# <의도 분류 추천> 




# 사용자 요청 종류
# 1. {도서명} 이랑 비슷한 책 추천좀
# 2. 내가 빌렸던 책과 유사한 책 추천좀
# 3. {작가명} 작가님 책 추천좀
# 4. {장르명} 책 추천해봐
# *** {장르명}, {작가명} 기반 추천은 후순위로 (위 1,2와 같이 임베딩 기반 추천을 우선으로 구현)




# 방법
# 1. 사전에 DB에 도서별 임베딩 data 저장
# 2. 추천 요청이 왔을 때 해당하는 도서명의 소개글 임베딩 데이터 SELECT
# 3. 이외 나머지 소개글 임베딩 데이터들과 문단 유사도 계산 후 최상위 3개 도서 추천




# 참고 코드
# 1. sentence-transformer 활용 문단 임베딩

# pip install -U sentence-transformers 설치
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModel
import torch
import time
import numpy as np

start_time = time.time()
# Load model from HuggingFace Hub
tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/paraphrase-multilingual-mpnet-base-v2')
model = AutoModel.from_pretrained('sentence-transformers/paraphrase-multilingual-mpnet-base-v2')
end_time = time.time()
print("모델 로딩 시간: ", end_time - start_time, "(초)")

#Mean Pooling - Take attention mask into account for correct averaging
def mean_pooling(model_output, attention_mask):
    token_embeddings = model_output[0] #First element of model_output contains all token embeddings
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)

# * 문단 안의 문장 갯수 맞춰주어야함
sentences1 = ['문과생도 중고등학생도 직장인도 프로그래밍에 눈뜨게 만든 바로 그 책이 전면 개정판으로 새로 태어났다!', 
             '2016년 《Do it! 점프 투 파이썬》으로 출간되었던 이 책은 약 4년 동안의 피드백을 반영하여 초보자가 더 빠르게 입문하고, 더 깊이 있게 공부할 수 있도록 개정되었다.',
             '특히 ‘나 혼자 코딩’과 ‘코딩 면허 시험 20제’ 등 독자의 학습 흐름에 맞게 문제를 보강한 점이 눈에 띈다.',
             '실습량도 두 배로 늘었다.',
              '4년 동안 압도적 1위!', 
              '위키독스 누적 방문 200만!'] 

sentences2 = ['『혼자 공부하는 파이썬』이 더욱 흥미있고 알찬 내용으로 개정되었다.',
              '프로그래밍이 정말 처음인 입문자도 따라갈 수 있는 친절한 설명과 단계별 학습은 그대로!' ,
              '혼자 공부하더라도 체계적으로 계획을 세워 학습할 수 있도록 ‘혼공 계획표’를 새롭게 추가했다.', 
              '또한 입문자가 자주 물어보는 질문과 오류 해결 방법을 적재적소에 배치하여 예상치 못한 문제에 부딪혀도 좌절하지 않고 끝까지 완독할 수 있도록 도와준다.',
              '단순한 문법 암기와 코딩 따라하기에 지쳤다면, 새로운 혼공파와 함께 ‘누적 예제’와 ‘도전 문제’로 프로그래밍의 신세계를 경험해 보자!',
              '배운 내용을 씹고 뜯고 맛보고 즐기다 보면 응용력은 물론 알고리즘 사고력까지 키워 코딩 실력이 쑥쑥 성장할 것이다.']

sentences3 = ['2000년부터 발표된 그의 주옥같은 글들.' ,
              '독자들이 자발적으로 만든 제본서는 물론, 전자책과 앱까지 나왔던 『세이노의 가르침』이 드디어 전국 서점에서 독자들을 마주한다.',
              '여러 판본을 모으고 저자의 확인을 거쳐 최근 생각을 추가로 수록하였다.',
              '정식 출간본에만 추가로 수록된 글들은 목차와 본문에 별도 표시하였다.',
              '더 많은 사람이 이 책을 보고 힘을 얻길 바라기에 인세도 안 받는 저자의 마음을 담아, 700쪽이 넘는 분량에도 7천 원 안팎에 책을 구매할 수 있도록 했다.',
              '정식 출간 전자책 또한 무료로 선보인다.']

# Tokenize sentences
encoded_input1 = tokenizer(sentences1, padding=True, truncation=True, return_tensors='pt')
encoded_input2 = tokenizer(sentences2, padding=True, truncation=True, return_tensors='pt')
encoded_input3 = tokenizer(sentences3, padding=True, truncation=True, return_tensors='pt')

# Compute token embeddings
with torch.no_grad():
    model_output1 = model(**encoded_input1)
    model_output2 = model(**encoded_input2)
    model_output3 = model(**encoded_input3)

# 임베딩 데이터 DB에 저장
# Perform pooling. In this case, max pooling.
sentence_embeddings1 = mean_pooling(model_output1, encoded_input1['attention_mask'])
sentence_embeddings2 = mean_pooling(model_output2, encoded_input2['attention_mask'])
sentence_embeddings3 = mean_pooling(model_output3, encoded_input3['attention_mask'])

print("Sentence embeddings:")
print(sentence_embeddings1)
print(sentence_embeddings2)
print(sentence_embeddings3)
print(" 현재 문단 하나당 문장 수 : ", len(sentence_embeddings1))
print(" 문장 하나당 차원 수 : ", len(sentence_embeddings1[0]))
# 벡터화 된 데이터 DB에 넣어 두기


# 2. 문단 유사도 계산하기

# '{도서명}과 유사한 책 추천좀' 했을 때
# 사용자가 원하는 도서 임베딩 데이터

# 'Do it 파이썬'
want_recommend_book_emd = sentence_embeddings1

# 그외의 도서들의 임베딩 데이터
other_book_names = ['혼자 공부하는 파이썬','세이노의 가르침']
other_book_emds = [sentence_embeddings2,sentence_embeddings3]

# 문단 유사도 리스트
cos_sim_list = []

for book_emd in other_book_emds:
    cos_sim_list.append(torch.cosine_similarity(sentence_embeddings1.reshape(1,-1),book_emd.reshape(1,-1)))

print("cos_sim_list : ", cos_sim_list)
# 리스트에서 가장 큰 수의 인덱스 == best_idx
best_idx = np.argmax(cos_sim_list)

print("챗봇 : ", other_book_names[best_idx] , " 라는 책 추천드립니다!")
# print("sentence_embeddings1 과 sentence_embeddings2 : ", torch.cosine_similarity(sentence_embeddings1.reshape(1,-1),sentence_embeddings2.reshape(1,-1)))
# print("sentence_embeddings2 과 sentence_embeddings3 : ", torch.cosine_similarity(sentence_embeddings2.reshape(1,-1),sentence_embeddings3.reshape(1,-1)))
# print("sentence_embeddings1 과 sentence_embeddings3 : ", torch.cosine_similarity(sentence_embeddings1.reshape(1,-1),sentence_embeddings3.reshape(1,-1)))
