from spell_checker import try_word

sentence = input("Type in a sentence: ")

def word_check(sentence):
    words = sentence.split()
    corrected = []
    for w in words:
        corrected.append(try_word(w))
    return " ".join(corrected)

print(word_check(sentence))