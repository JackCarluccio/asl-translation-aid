import re
import string
from collections import Counter
import numpy as np
from wordfreq import zipf_frequency
from pathlib import Path

def modern_score(word):
    # Higher = more common in contemporary English
    return zipf_frequency(word, 'en')

def read_corpus(filename):
        with open(filename, "r") as file:
            lines = file.readlines()
            words = []
            for line in lines:
                words += re.findall(r'\w+', line.lower())
        return words

# creating vocabulary
words = read_corpus(Path(__file__).resolve().parents[2] / "data" / "big.txt")
vocabs = set(words)

# creating a dictionary with word and its probability
word_probas = {word: modern_score(word) for word in words}
# splitting the word in all of its versions
def split(word):
    return [(word[:i], word[i:]) for i in range(len(word) + 1)]

# deleting a character 
def delete(word):
    return [l + r[1:] for l,r in split(word) if r]

# swapping different combinations
def swap(word):
    return [l + r[1] + r[0] + r[2:] for l,r in split(word) if len(r)>1]

# replacing letters combinations
def replace(word):
    letters = string.ascii_lowercase
    return [l + c + r[1:] for l,r in split(word) if r for c in letters]

# inserting letters combinations
def insert(word):
    letters = string.ascii_lowercase
    return [l + c + r for l,r in split(word) for c in letters]

def level_one_edit(word):
    return set(delete(word) + swap(word) + replace(word) + insert(word))

def level_two_edit(word):
    return set(e2 for e1 in level_one_edit(word) for e2 in level_one_edit(e1))

def correct_spelling(word, vocabulary):
    word = word.lower()
    if word in vocabulary:
        return word
    # generate candidates
    suggestion = level_one_edit(word)
    best_guesses = [w for w in suggestion if w in vocabulary]
    if best_guesses:
        best = max(best_guesses, key=modern_score)
        return best
    else:
        suggestion = level_two_edit(word)
        best_guesses = [w for w in suggestion if w in vocabulary]
        if best_guesses:
            best = max(best_guesses, key=modern_score)
            return best
        else:
            return "Word is not in dictionary"
def try_word(word):
    return correct_spelling(word, vocabs)

#word = input("Type a word here: ")
#print(try_word(word))