from src.data_structures.spell_checker import try_word

def word_check(sentence):
    words = sentence.split()
    corrected = []
    for w in words:
        corrected.append(try_word(w))
    return " ".join(corrected)
