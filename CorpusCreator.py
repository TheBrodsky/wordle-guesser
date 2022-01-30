import pickle

WORD_LIST_PATH = "wordle word list (spoilers).txt"
CORPUS_OUT_PATH = "wordleCorpus.pickle"

if __name__ == "__main__":
    corpus = set()
    with open(WORD_LIST_PATH, 'r') as file:
        for word in file:
            word = word.strip()
            corpus.add(word)
    
    with open(CORPUS_OUT_PATH, 'wb') as file:
        pickle.dump(corpus, file)