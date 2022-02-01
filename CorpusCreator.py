import pickle

WORD_LIST_PATH = "wordle word list (spoilers).txt"
GUESS_LIST_PATH = "wordle guess list (spoilers).txt"
CORPUS_OUT_PATH = "wordleCorpus.pickle"
GUESSES_OUT_PATH = "guessCorpus.pickle"

if __name__ == "__main__":
    corpus = set()
    with open(WORD_LIST_PATH, 'r') as file:
        for word in file:
            corpus.add(word.strip())
    
    with open(CORPUS_OUT_PATH, 'wb') as file:
        pickle.dump(corpus, file)
    
    guesses = set()
    with open(GUESS_LIST_PATH, 'r') as file:
        for word in file:
            guesses.add(word.strip())
            
    with open(GUESSES_OUT_PATH, 'wb') as file:
        pickle.dump(guesses, file)