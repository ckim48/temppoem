import nltk # nltk.py
# import random # random.py
import random

# nltk.download('punkt') # word_tokenize
# nltk.download('stopwords') # list of stopwords

from nltk.corpus import stopwords # stopwords.py
from nltk.tokenize import word_tokenize

s = "Hello my name is Scott"

stopword_list = stopwords.words('english') # getting english topwords
word_list = s.lower().split() # ["hello", "my", "name", "is" , "Scott"]
no_stopword = [word for word in word_list if word not in stopword_list]
# no_stopword = []
# for word in word_list:
#     if word not in stopword_list:
#         no_stopword.append(word)
print(no_stopword)