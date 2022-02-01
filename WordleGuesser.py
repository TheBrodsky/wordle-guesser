from WordleGuessScorer import WordleGuessScorer
from CorpusCreator import CORPUS_OUT_PATH, GUESSES_OUT_PATH
import re
import pickle

class WordleGuesser:
    def __init__(self, corpus):
        self.originalCorpus = corpus
        self.letterPools = self._initLetterPools()
        self.yellowConstraints = set()
        self.corpus = self._getFiveLetterWordCorpus(corpus.copy())
        self.printBestGuesses(5)

    # Getters
    def getCorpus(self):
        return self.corpus

    def getPools(self):
        return self.letterPools

    def getYellowConstraints(self):
        return self.yellowConstraints
    
    def getScorer(self):
        return WordleGuessScorer(self.corpus, self.letterPools, self.yellowConstraints)

    # Public Methods
    def makeGuess(self, word):
        if len(word) != 5:
            print("Guess must be 5 letters")
            return
        
        print(f"You guessed {word}.")
        i = 0
        while i < 5:
            char = word[i]
            color = input(f"What color was {char}?").lower()
            if color in ['gray', 'grey']:
                self.addGrayLetterConstraint(char)
            elif color == 'yellow':
                self.addYellowLetterConstraint(i, char)
            elif color == 'green':
                self.addGreenLetterConstraint(i, char)
            else:
                print("Sorry, that's not a valid color. Choose gray, yellow, or green")
                continue
            i += 1

        self.corpus = self.filterCorpus(self.corpus)
        print(f"There are {len(self.corpus)} possible words left.")
        self.printBestGuesses(5)

    def getCorpusSize(self):
        return len(self.corpus)

    def reset(self):
        self.__init__(self.originalCorpus)

    def printPoolsAndConstraints(self):
        for pool in self.letterPools:
            print(''.join(pool))
        print(f"Yellow: {''.join(self.yellowConstraints)}")

    # Public - Guess methods
    def printBestGuesses(self, numGuesses):
        guesses = self.getBestNGuesses(numGuesses)
        print(f"Best {numGuesses} guesses:")
        for word, score in guesses:
            print(f"{word}: {score:.3f}")

    def getBestGuess(self):
        scorer = self.getScorer()
        bestWord, bestScore = scorer.calculateBestWord()
        return bestWord

    def getBestNGuesses(self, n):
        scorer = self.getScorer()
        if len(self.corpus) < n:
            n = len(self.corpus)
        return scorer.calculateSortedScoredWords()[:n]

    # Supporting, Public Methods
    def addGreenLetterConstraint(self, index, letter):
        self.letterPools[index] = set({letter})

    def addYellowLetterConstraint(self, index, letter):
        try:
            self.letterPools[index].remove(letter)
            self.yellowConstraints.add(letter)
        except KeyError:
            pass

    def addGrayLetterConstraint(self, letter):
        for pool in self.letterPools:
            try:
                pool.remove(letter)
            except KeyError:
                pass

    def filterCorpus(self, corpus):
        patterns = self._assemblePatterns()
        filtered = corpus
        for pattern in patterns:
            filtered = set(filter(lambda word: bool(pattern.match(word)), filtered))
        return set(filtered)

    # Private Methods
    def _getFiveLetterWordCorpus(self, corpus):
        fiveLetterWords = set(filter(lambda x: len(x) == 5, corpus))
        return self.filterCorpus(fiveLetterWords)

    def _assemblePatterns(self):
        patterns = [self._assembleMainPattern()]
        for letter in self.yellowConstraints:
            patterns.append(re.compile(f".*{letter}.*"))
        return patterns

    def _assembleMainPattern(self):
        patternString = ''
        for pool in self.letterPools:
            patternString += f"[{''.join(pool)}]"
        return re.compile(patternString)

    def _initLetterPools(self):
        pool = []
        alphabet = set('abcdefghijklmnopqrstuvwxyz')
        for i in range(5):
            pool.append(alphabet.copy())
        return pool



    

if __name__ == "__main__":
    corpus = None
    guesses = None
    with open(CORPUS_OUT_PATH, 'rb') as file:
        corpus = pickle.load(file)
    
    with open(GUESSES_OUT_PATH, 'rb') as file:
        guesses = pickle.load(file)
        
    guesser = WordleGuesser(corpus)
    fullGuesser = WordleGuesser(guesses)