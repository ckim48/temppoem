import nltk
#nltk.download('cmudict') #cmudict: real dictionary made by cmu; 처음한번 실행하면 다운로드됬으니 꺼나도됨
from nltk.corpus import cmudict
from nltk.corpus import stopwords
import re #re: regular expression (this library comes w/ python like random, x need to download)
#nltk: an open source library for NLP (Natural Language Processing)
#NLP: technique for giving computer an ability to understand human language
import spacy
def cnt_word_syll(word): #count syllables for a single word
    pronounce_dict = cmudict.dict()
    word = word.lower() #change to lower case
    phonetics = pronounce_dict.get(word) #[['EH1', 'L', 'AH0', 'F', 'AH0', 'N', 'T']]

    syllable_cnt = 0
    if phonetics != None:
        for phoneme in phonetics[0]: #'EH1'
            for char in phoneme:
                if char.isdigit(): #guaranteed that digit is only attached to vowel
                    syllable_cnt += 1
    return syllable_cnt

#regular expression: pattern matching (eg. email has @, ., etc.)
def cnt_sent_syll(sentence):
    cleaned_sent = re.sub("[^\w\s]", "", sentence)
    list_words = cleaned_sent.split() # ["Hello", "my", "name", "is", "Serena"]

    total_syll = 0
    for word in list_words:
        num = cnt_word_syll(word)
        total_syll += num
    return total_syll

def haiku_is_standard(poem): # #["elephant is big",line2,line3]
    if len(poem) == 3:
        first_ln_syll = cnt_sent_syll(poem[0])
        second_ln_syll = cnt_sent_syll(poem[1])
        third_ln_syll = cnt_sent_syll(poem[2])
        if first_ln_syll != 5:
            return False
        elif second_ln_syll != 7:
            return False
        elif third_ln_syll != 5:
            return False
        return True
    else:
        return False
def is_acroustic(theme, poem):
    threshold = 0.1
    # return true, if first letter of each line match to each letter in theme
    if not match_theme(theme,poem):
        print("NO Theme")
        return False
    print("Score",isSimilar_theme(theme, poem))
    if isSimilar_theme(theme, poem) < threshold:
        return False
    return True

def check_syllabus(poem):
    for i in range(14):
        syll = cnt_sent_syll(poem[i])
        if syll < 10:
            return False
    return True


def get_last_word_pronunciation(word):
    d = cmudict.dict()
    try:
        return d[word.lower()][0][-1]
    except KeyError:
        return None


def is_rhyme_pair(word1, word2):
    return get_last_word_pronunciation(word1) == get_last_word_pronunciation(word2)


def has_rhyme_scheme(lines):
    lines = [re.sub("[^\w\s']", "", line.lower()) for line in lines]
    words = [line.split() for line in lines]

    for i in range(0, len(words), 4):
        if i + 7 <= len(words):
            if not is_rhyme_pair(words[i][-1], words[i + 2][-1]) or \
                    not is_rhyme_pair(words[i + 1][-1], words[i + 3][-1]) or \
                    not is_rhyme_pair(words[i + 4][-1], words[i + 6][-1]) or \
                    not is_rhyme_pair(words[i + 5][-1], words[i + 7][-1]):
                return False

    return True


def is_sonnet(poem):
    if check_syllabus(poem) == False:
        return False
    if has_rhyme_scheme(poem) == False:
        return False
    return True
def words_rhyme(word1, word2):
    pronounce_dict = cmudict.dict()
    word1 = word1.lower()
    phonetics1 = pronounce_dict.get(word1)
    syll1 = ""
    for i in range(len(phonetics1)-1, len(phonetics1)-3, -1):
        syll1 += phonetics1[0][i]
    word2 = word2.lower()
    phonetics2 = pronounce_dict.get(word2)
    syll2 = ""
    for i in range(len(phonetics2) - 1, len(phonetics2) - 3, -1):
        syll2 += phonetics2[0][i]

    if syll1 == syll2:
        return True
    else:
        return False

# Functions for acrostic

# POEM -> poem
# Poem --> poem
def match_theme(theme, lines): #theme:bat   #lines = ["bring out yoru bat","nd your ball..",",,,,"]
    theme = theme.lower()
    theme_index = 0
    for line in lines:
        if line[0].islower() == None:
            print("HECK")
            return False

        line = line.lower()
        if line[0] != theme[theme_index]:
            return False
        theme_index += 1
    return True

# NLP (Natural Languge Processing) - > Giving ability to understand the human language

# Stopword: meaningless word: is, a, the ,of, are,am, have, will...
def isSimilar_theme(theme, lines):
    nlp = spacy.load("en_core_web_md")  # Load the spaCy model with pre-trained word vectors
    theme = nlp(theme.lower())
    stopword_set = set(stopwords.words('english'))

    similarity_score = 0
    number_word = 0

    for line in lines:
        line = line.lower()
        cleaned_line = re.sub("[^\w\s]", "", line)
        doc = nlp(cleaned_line)

        for token in doc:
            if token.text not in stopword_set:
                similarity = theme.similarity(token)
                similarity_score += similarity
                number_word += 1

    if number_word == 0:
        return 0

    average_similarity = similarity_score / number_word
    print(average_similarity)
    return average_similarity

# 0.3


# lines = ["preserve the high honour of poems dear","Oh poor acrostic-writer: by design","Each line of verse that you will lay down here","My name discover, line by singing line."]
# print(match_theme("poem",lines))
# print(isSimillar_theme("poem",lines))
# similarity = 1 - jaccard_distance(set("poem"), set("eaaaaaa"))
# print(similarity)
#
# lines = ["Paaaaaa","Oeaaaaaa","Eaaaaaaaa","Mmmmmmmm"]
# print(isSimillar_theme("poem",lines))
#
# sample = ["Baseball is fun","and your ball"]
# print(isSimillar_theme("poem",sample))

# similarity = 1 - jaccard_distance(set(word1),set(word2))
# print(similarity)
#
# word1 = "player"
# word2 = "baseball"
# similarity = 1 - jaccard_distance(set(word1),set(word2))
# print(similarity)

