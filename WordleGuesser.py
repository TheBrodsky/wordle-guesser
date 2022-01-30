from nltk.corpus import brown
from collections import Counter
from copy import deepcopy
import re

class WordleGuesser:
    def __init__(self, corpusReader):
        self.corpusReader = corpusReader
        self.letterPools = self._initLetterPools()
        self.yellowConstraints = set()
        self.corpus = self._getFiveLetterWordCorpus(corpusReader)
        self.printBestConstrainedGuesses(5)

    # Getters
    def getCorpus(self):
        return self.corpus.copy()

    def getPools(self):
        return deepcopy(self.letterPools)

    def getYellowConstraints(self):
        return self.yellowConstraints.copy()

    # Public Methods
    def makeGuess(self, word):
        if len(word) != 5:
            print(f"Guess must be 5 letters")
            return
        
        print(f"You guessed ${word}.")
        i = 0
        while i < 5:
            char = word[i]
            color = input(f"What color was ${char}?").lower()
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
        self.printBestConstrainedGuesses(5)

    def getCorpusSize(self):
        return len(self.corpus)

    def reset(self):
        self.__init__(self.corpusReader)

    def printPoolsAndConstraints(self):
        for pool in self.letterPools:
            print(''.join(pool))
        print(f"Yellow: {''.join(self.yellowConstraints)}")

    # Public - Guess methods, Constrained
    def printBestConstrainedGuesses(self, numGuesses):
        guesses = self.getBestNConstrainedGuesses(numGuesses)
        print(f"Best {numGuesses} guesses:")
        for word, score in guesses:
            print(f"{word}: {score:.3f}")

    def getBestConstrainedGuess(self):
        bestWord, bestScore = WordleGuessScorer().getBestWord(self)
        return bestWord

    def getBestNConstrainedGuesses(self, n):
        if len(self.corpus) < n:
            n = len(self.corpus)
        return WordleGuessScorer().getSortedScoredWords(self)[:n]

    # Public - Guess methods, Unconstrained
    def printBestUnconstrainedGuesses(self, numGuesses):
        pass

    def getBestUnconstrainedGuess(self):
        pass

    def getBestNUnconstrainedGuesses(self, n):
        pass

    # Sorta Public Methods (public but probably not useful)
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
    def _getFiveLetterWordCorpus(self, corpusReader):
        fiveLetterWords = set(filter(lambda x: len(x) == 5, corpusReader.words()))
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

class WordleGuessScorer:
    # Public - Scoring/Guessing methods for real guesses
    def getBestWord(self, guesser):
        letterScoringMap = self.makeScoringMap(guesser)
        bestWord = None
        bestScore = 0
        for word in guesser.getCorpus():
            score = self._scoreWord(word, letterScoringMap)
            if score > bestScore:
                bestWord = word
                bestScore = score
        return bestWord, bestScore

    def getSortedScoredWords(self, guesser):
        scoringFunc = lambda word, scoreMap: self._scoreWord(word, scoreMap)
        wordScores = self.scoreWords(guesser, scoringFunc)
        sortedScores = sorted(list(wordScores.items()), key=lambda x: -x[1])
        return sortedScores
    
    # Public - Scoring/Guessing methods for filter guesses
    # (a filter guess is a word which targets likely, unguessed letters)

    # Public - Other methods
    def scoreWords(self, guesser, scoringFunc):
        letterScoringMap = self.makeScoringMap(guesser)
        wordScores = {}
        for word in guesser.getCorpus():
            wordScores[word] = scoringFunc(word, letterScoringMap)
        return wordScores
    
    def makeScoringMap(self, guesser):
        corpus = guesser.getCorpus()
        pools = guesser.getPools()
        yellowConstraints = guesser.getYellowConstraints()

        letterFreqs = self._scoreLetters(corpus)
        letterBlacklist = self._getConstrainingLetters(yellowConstraints, pools)

        for char in letterBlacklist:
            letterFreqs[char] = 0

        return letterFreqs

    # Private Methods
    def _scoreWord(self, word, scoringMap):
        score = 0
        countedChars = set()
        for char in word:
            # avoids counting chars twice; more letters is more valuable
            if char not in countedChars:
                score += scoringMap[char]
                countedChars.add(char)
        return score
    
    def _getConstrainingLetters(self, yellowConstraints, letterPools):
        '''returns yellow or green constraining letters. Used for blacklisting
        letters from scoring algorithm'''
        letters = []
        for char in yellowConstraints:
            letters.append(char)

        for pool in letterPools:
            if len(pool) == 1:
                # len 1 is a green constraint
                letters.append(list(pool)[0]) # convert to char

        return letters

    def _scoreLetters(self, corpus):
        letterCounts = self._getLetterCounts(corpus)
        numLetters = len(corpus) * 5 # every word is 5 letters
        letterFreqs = {}
        for letter, count in letterCounts.items():
            letterFreqs[letter] = count/numLetters
        return letterFreqs

    def _getLetterCounts(self, corpus):
        counts = Counter('')
        for word in corpus:
            counts += Counter(word)
        return counts

    

if __name__ == "__main__":
    guesser = WordleGuesser(brown)
