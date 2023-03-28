import googletrans
import pandas as pd
from tqdm import tqdm

# def google_translate(word, code):
#     translator = Translator()
#     translator.raise_Exception = True
#     translated = translator.translate(word, src=code, dest='en').text
#     return translated

translator = googletrans.Translator()
translator.raise_Exception = True
local_path = 'C:/backend_study/final_pjt/library_chatbot(python_max_n9)/'
neg_data_en = pd.read_csv(local_path + 'data/csv/neg_data(en).csv')

inputs= neg_data_en['input'].tolist()[:1000]
inputs_ko = []

for input in tqdm(inputs):
    inputs_ko.append(translator.translate(input, dest='ko').text)

print(inputs_ko[:5])

neg_data_ko = pd.DataFrame(inputs_ko,columns=['neg_data_ko'])
neg_data_ko.to_csv(local_path + 'data/csv/neg_data(ko).csv')
# result1 = translator.translate(str1, dest='en')

# print(result1.text)
