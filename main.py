
from nltk.corpus import cmudict
def get_last_word_pronunciation(word):
    d = cmudict.dict()
    try:
        print(d[word.lower()])
        print(d[word.lower()][0])
        print(d[word.lower()][0][-1])
        return d[word.lower()][0][-1]
    except KeyError:
        return None

print(get_last_word_pronunciation("elephant"))