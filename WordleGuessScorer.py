from collections import Counter
from copy import deepcopy

class WordleGuessScorer:
    def __init__(self, corpus, pools, yellowConstraints):
        self.corpus = corpus.copy()
        self.pools = deepcopy(pools)
        self.yellowConstraints = yellowConstraints.copy()
        
    # Public - Scoring/Guessing methods for guesses
    def getBestWord(self):
        letterScoringMap = self.makeScoringMap()
        bestWord = None
        bestScore = 0
        for word in self.corpus:
            score = self._scoreWord(word, letterScoringMap)
            if score > bestScore:
                bestWord = word
                bestScore = score
        return bestWord, bestScore

    def getSortedScoredWords(self):
        wordScores = self.scoreWords()
        sortedScores = sorted(list(wordScores.items()), key=lambda x: -x[1])
        return sortedScores

    # Public - Other methods
    def scoreWords(self):
        letterScoringMap = self.makeScoringMap()
        wordScores = {}
        for word in self.corpus:
            wordScores[word] = self._scoreWord(word, letterScoringMap)
        return wordScores
    
    def makeScoringMap(self):
        letterFreqs = self._scoreLetters()
        letterBlacklist = self._getConstrainingLetters()

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
    
    def _getConstrainingLetters(self):
        '''returns yellow or green constraining letters. Used for blacklisting
        letters from scoring algorithm'''
        letters = []
        for char in self.yellowConstraints:
            letters.append(char)

        for pool in self.pools:
            if len(pool) == 1:
                # len 1 is a green constraint
                letters.append(list(pool)[0]) # convert to char

        return letters

    def _scoreLetters(self):
        letterCounts = self._getLetterCounts()
        numLetters = len(self.corpus) * 5 # every word is 5 letters
        letterFreqs = {}
        for letter, count in letterCounts.items():
            letterFreqs[letter] = count/numLetters
        return letterFreqs

    def _getLetterCounts(self):
        counts = Counter('')
        for word in self.corpus:
            counts += Counter(word)
        return counts