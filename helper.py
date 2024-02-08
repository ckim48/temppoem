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
        print("SYLLABELS_WORD for", word,"is", phonetics[0])
        for phoneme in phonetics[0]: #['EH1', 'L', 'AH0', 'F', 'AH0', 'N', 'T']
            for char in phoneme:
                if char.isdigit(): #guaranteed that digit is only attached to vowel
                    if phoneme != 'AW1':
                        syllable_cnt += 1
    else:
        syllable_cnt = simple_syllable_count(word)
        #print("SYLLABELS_WORD for", word, "is", syllable_cnt )
    print("Total SYLLABELS_WORD for", word, "is", syllable_cnt)
    return syllable_cnt
def simple_syllable_count(word):

    vowels = "aeiouy"
    count = 0
    prev_char_vowel = False  # Flag to track if the previous character was a vowel
    for char in word:
        if char in vowels:

            if not prev_char_vowel:
                count += 1
            prev_char_vowel = True
        else:
            prev_char_vowel = False

    if word.endswith("e") and count > 1:
        count -= 1

    if word.endswith("s") or word.endswith("es"):
        count -= 1

    return max(count, 1)
#regular expression: pattern matching (eg. email has @, ., etc.)
def cnt_sent_syll(sentence): # elephant is big
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
        print("SYLLABELS",first_ln_syll,second_ln_syll,third_ln_syll)

        if first_ln_syll != 5:
            return False
        elif second_ln_syll != 7:
            return False
        elif third_ln_syll != 5:
            return False
        return True
    else:
        return False
def is_acroustic(theme, poem): #bat, b a t
    threshold = 0.11
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


import re
from nltk.corpus import cmudict


def get_last_word_pronunciation(word):
    if word is None:
        return None
    d = cmudict.dict()
    try:
        pronunciation = d[word.lower()]
        # Get the pronunciation of the last syllable
        last_syllable_pronunciation = pronunciation[0][-1]
        return last_syllable_pronunciation
    except KeyError:
        return None

def is_rhyme_pair(word1, word2):
    pronunciation1 = get_last_word_pronunciation(word1)
    pronunciation2 = get_last_word_pronunciation(word2)
    if pronunciation1 is None or pronunciation2 is None:
        return True  # Treat as a rhyme if either word is not found
    return pronunciation1 == pronunciation2

def has_rhyme_scheme(lines):
    #lines = [re.sub("[^\w\s']", "", line.lower()) for line in lines]
    last_words_pronunciations = []
    # for i, line in enumerate(sonnet_29):
    #     last_word = re.findall(r'\b\w+\b', line)[-1]  # Extract the last word
    #     print(f"Line {i + 1}: {last_word} -> {get_last_word_pronunciation(last_word)}")
    words = []
    for i, line in enumerate(lines):
        last_word = re.findall(r'\b\w+\b', line)[-1]  # Extract the last word
        words.append(last_word)
        print(last_word)
        last_words_pronunciations.append(get_last_word_pronunciation(last_word))

    # last_words_pronunciations = [get_last_word_pronunciation(line[-1]) for line in words]
    print(words)
    print(len(words))
    print(len(last_words_pronunciations))
    if not is_rhyme_pair(last_words_pronunciations[0], last_words_pronunciations[2]):
        return False
    if not is_rhyme_pair(last_words_pronunciations[1], last_words_pronunciations[3]):
        return False
    if not is_rhyme_pair(last_words_pronunciations[4], last_words_pronunciations[6]):
        return False
    if not is_rhyme_pair(last_words_pronunciations[5], last_words_pronunciations[7]):
        return False
    if not is_rhyme_pair(last_words_pronunciations[8], last_words_pronunciations[10]):
        return False
    if not is_rhyme_pair(last_words_pronunciations[9], last_words_pronunciations[11]):
        return False
    if not is_rhyme_pair(last_words_pronunciations[-2], last_words_pronunciations[-1]):
        return False

    return True

def is_sonnet(poem):
    if has_rhyme_scheme(poem) is False:
        return False
    return True

sonnet_18 = [
    "Shall I compare thee to a summer's day?",
    "Thou art more lovely and more temperate:",
    "Rough winds do shake the darling buds of May,",
    "And summer's lease hath all too short a date:",
    "Sometime too hot the eye of heaven shines,",
    "And often is his gold complexion dimmed;",
    "And every fair from fair sometime declines,",
    "By chance or nature's changing course untrimmed;",
    "But thy eternal summer shall not fade",
    "Nor lose possession of that fair thou ow'st;",
    "Nor shall Death brag thou wanderest in his shade,",
    "When in eternal lines to time thou grow'st:",
    "So long as men can breathe or eyes can see,",
    "So long lives this, and this gives life to thee."
]
sonnet_29 = [
    "When, in disgrace with fortune and men's eyes,",
    "I all alone beweep my outcast state,",
    "And trouble deaf heaven with my bootless cries,",
    "And look upon myself, and curse my fate,",
    "Wishing me like to one more rich in hope,",
    "Featured like him, like him with friends possessed,",
    "Desiring this man's art and that man's scope,",
    "With what I most enjoy contented least;",
    "Yet in these thoughts myself almost despising,",
    "Haply I think on thee, and then my state,",
    "Like to the lark at break of day arising",
    "From sullen earth, sings hymns at heaven's gate;",
    "For thy sweet love remembered such wealth brings",
    "That then I scorn to change my state with kings."
]

# for i, line in enumerate(sonnet_18):
#     last_word = re.findall(r'\b\w+\b', line)[-1]  # Extract the last word
#     print(f"Line {i+1}: {last_word} -> {get_last_word_pronunciation(last_word)}")
#
# print(is_sonnet(sonnet_18))


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
def match_theme(theme, lines): #theme:bat   #lines = ["bring out yoru bat","and your ball..",",,,,"]
    theme = theme.lower()
    theme_index = 0
    for line in lines:
        if line[0].islower() == None:
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

