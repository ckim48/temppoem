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

def is_rhyme_pair(pronunciation1, pronunciation2):
    # pronunciation1 = get_last_word_pronunciation(word1)
    # pronunciation2 = get_last_word_pronunciation(word2)
    # print("AA",word1,pronunciation1)
    # print("aa,",word2,pronunciation2)
    if pronunciation1 is None or pronunciation2 is None:
        return True  # Treat as a rhyme if either word is not found
    if (pronunciation1 == "Z" and pronunciation2 =="S") or (pronunciation1 == "S" and pronunciation2 =="Z")or (pronunciation1 == "ER0" and pronunciation2 =="R")or (pronunciation1 == "R" and pronunciation2 =="ER0")or (pronunciation1 == "N" and pronunciation2 =="D")or (pronunciation1 == "D" and pronunciation2 =="N")or (pronunciation1 == "AY1" and pronunciation2 =="IY0")or (pronunciation1 == "IY0" and pronunciation2 =="AY1"):
        return True

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
        print("FIRST")
        return False
    if not is_rhyme_pair(last_words_pronunciations[1], last_words_pronunciations[3]):
        print("2")
        return False
    if not is_rhyme_pair(last_words_pronunciations[4], last_words_pronunciations[6]):
        print("3")

        return False
    if not is_rhyme_pair(last_words_pronunciations[5], last_words_pronunciations[7]):
        print("4")

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
sonnet = [
    "Amidst the whispers of the evening breeze,",
    "Where shadows dance in moonlight's soft embrace,",
    "A yearning heart finds solace, finds release,",
    "In dreams that linger in this sacred space.",
    "With each caress of night upon my brow,",
    "I drift away to realms of endless flight,",
    "Where stars above sing secrets, softly vow,",
    "To guide me through the darkness of the night.",
    "Oh, how I long to hold this fleeting dream,",
    "To capture time within my trembling grasp,",
    "Yet time, relentless, flows like a stream,",
    "And slips away like sand within my clasp.",
    "But in this moment, let me linger here,",
    "Embraced by night, and free from doubt and fear."
]
sonnet_73 = [
    "That time of year thou mayst in me behold,",
    "When yellow leaves, or none, or few, do hang",
    "Upon those boughs which shake against the cold,",
    "Bare ruined choirs, where late the sweet birds sang.",
    "In me thou see'st the twilight of such day",
    "As after sunset fadeth in the west;",
    "Which by and by black night doth take away,",
    "Death's second self, that seals up all in rest.",
    "In me thou see'st the glowing of such fire,",
    "That on the ashes of his youth doth lie,",
    "As the death-bed whereon it must expire,",
    "Consumed with that which it was nourished by.",
    "This thou perceiv'st, which makes thy love more strong,",
    "To love that well which thou must leave ere long."
]
sonnet_custom = [
    "In fields of gold, where whispers softly sing,",
    "Beneath the moon's enchanting gentle light,",
    "A solitary bird takes to the wing,",
    "In silent flight, a creature of the night.",
    "Through valleys deep, where shadows dance and play,",
    "And rivers weave a tale of ancient lore,",
    "The stars above, in endless cosmic sway,",
    "Illuminate the path forevermore.",
    "Upon the breeze, the fragrance of the rose,",
    "Awakens memories of days long past,",
    "Where love once bloomed, as tender as the prose,",
    "That poets wrote, in verses meant to last.",
    "And in this moment, captured by the pen,",
    "We find the beauty that shall never end."
]
sonnet_another = [
    "Beneath the canopy of emerald trees,",
    "Where sunlight dances in a playful breeze,",
    "A brook meanders, singing soft refrains,",
    "Its melody a balm for weary pains.",
    "Among the blooms that blush in hues divine,",
    "A butterfly alights, a fleeting sign,",
    "Of beauty fragile, transient as dew,",
    "Yet vibrant, like the sky's eternal blue.",
    "In twilight's embrace, the stars ignite,",
    "A tapestry of dreams in darkest night,",
    "Whispers of hope within the silent gloom,",
    "A beacon guiding through the misty tomb.",
    "Through nature's symphony, we find our way,",
    "And in its song, discover light of day."
]
sonnet_shakespeare_another = [
    "When I consider every thing that grows",
    "Holds in perfection but a little moment,",
    "That this huge stage presenteth nought but shows",
    "Whereon the stars in secret influence comment;",
    "When I perceive that men as plants increase,",
    "Cheered and checked even by the self-same sky,",
    "Vaunt in their youthful sap, at height decrease,",
    "And wear their brave state out of memory;",
    "Then the conceit of this inconstant stay",
    "Sets you most rich in youth before my sight,",
    "Where wasteful time debateth with decay,",
    "To change your day of youth to sullied night;",
    "And all in war with Time for love of you,",
    "As he takes from you, I engraft you new."
]
sonnet_shakespeare_yet_another = [
    "My mistress' eyes are nothing like the sun;",
    "Coral is far more red than her lips' red;",
    "If snow be white, why then her breasts are dun;",
    "If hairs be wires, black wires grow on her head.",
    "I have seen roses damasked, red and white,",
    "But no such roses see I in her cheeks;",
    "And in some perfumes is there more delight",
    "Than in the breath that from my mistress reeks.",
    "I love to hear her speak, yet well I know",
    "That music hath a far more pleasing sound;",
    "I grant I never saw a goddess go;",
    "My mistress, when she walks, treads on the ground:",
    "And yet, by heaven, I think my love as rare",
    "As any she belied with false compare."
]
sonnet_shakespeare_last = [
    "That time of year thou mayst in me behold,",
    "When yellow leaves, or none, or few, do hang",
    "Upon those boughs which shake against the cold,",
    "Bare ruined choirs, where late the sweet birds sang.",
    "In me thou see'st the twilight of such day",
    "As after sunset fadeth in the west;",
    "Which by and by black night doth take away,",
    "Death's second self, that seals up all in rest.",
    "In me thou see'st the glowing of such fire,",
    "That on the ashes of his youth doth lie,",
    "As the death-bed whereon it must expire,",
    "Consumed with that which it was nourished by.",
    "This thou perceiv'st, which makes thy love more strong,",
    "To love that well which thou must leave ere long."
]
# for i, line in enumerate(sonnet_shakespeare_last):
#     last_word = re.findall(r'\b\w+\b', line)[-1]  # Extract the last word
#     print(f"Line {i+1}: {last_word} -> {get_last_word_pronunciation(last_word)}")
#
# print(is_sonnet(sonnet_shakespeare_last))
def has_stress_pattern(word):
    d = cmudict.dict()

    if word.lower() in d:
        pronunciation = d[word.lower()][0]

        stress_pattern = ''.join(['S' if re.search(r'\d', phoneme) else 'U' for phoneme in pronunciation])

        if re.search(r'SUS', stress_pattern):
            return True

    return False



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

