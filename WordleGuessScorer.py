from collections import Counter
from copy import deepcopy
import numpy as np

class WordleGuessScorer:
    def __init__(self, corpus, pools, yellowConstraints, penalizeDuplicates=True):
        self.corpus = corpus.copy()
        self.pools = deepcopy(pools)
        self.yellowConstraints = yellowConstraints.copy()
        self.alphabet = list('abcdefghijklmnopqrstuvwxyz')
        self.penalizeDuplicates = penalizeDuplicates
        
    # Main Methods
    def calculateBestWord(self):
        bestWord = None
        bestScore = 0
        for word in self.corpus:
            score = self.scoreWord(word)
            if score > bestScore:
                bestWord = word
                bestScore = score
        return bestWord, bestScore

    def calculateSortedScoredWords(self):
        wordScores = self.scoreAllWords()
        sortedScores = sorted(list(wordScores.items()), key=lambda x: -x[1])
        return sortedScores

    # Supporting Methods
    def scoreAllWords(self):
        positionalMatrix = self.getPositionalLetterScores()
        nonpositionalMatrix = self.getNonpositionalLetterScores()
        wordScores = {}
        for word in self.corpus:
            wordScores[word] = self.scoreWord(word, positionalMatrix, nonpositionalMatrix)
        return wordScores

    def scoreWord(self, word, positionalMatrix=None, nonpositionalMatrix=None):
        if positionalMatrix is None:
            positionalMatrix = self.getPositionalLetterScores()
            
        if nonpositionalMatrix is None:
            nonpositionalMatrix = self.getNonpositionalLetterScores()
        
        letterIndexes = np.array([ord(c) - ord('a') for c in word])
        positionalScores = positionalMatrix[np.arange(5), letterIndexes]
        nonpositionalScores = nonpositionalMatrix[letterIndexes]
        
        # max constraints is 5; more constraints = positional predictions are better
        positionalBias = self._getBlacklistedLettersIndexes().sum() / 5
        
        # count occurences of each letter in word to penalize words with repeats
        if self.penalizeDuplicates:
            _, uniqueIndexes = np.unique(letterIndexes, return_inverse=True)
            letterOccurences = np.bincount(uniqueIndexes)[uniqueIndexes]
            positionalScores /= letterOccurences
            nonpositionalScores /= letterOccurences
            
        compositeScores = (positionalScores * positionalBias) + (nonpositionalScores * (1-positionalBias))
        
        return compositeScores.sum()
    
    def getPositionalLetterScores(self):
        counts = np.zeros((5, len(self.alphabet))).astype(float) # 5x26 matrix; count per letter per position
        for i, position in enumerate(zip(*self.corpus)):
            countPairs = Counter(position) + Counter(self.alphabet) # alphabet added to ensure all 26 letters present
            sortedCountPairs = sorted(countPairs.items(), key=lambda x: x[0])
            positionCounts = [count for char, count in sortedCountPairs]
            counts[i, :] = positionCounts
        counts -= 1 # subtract 1 from adding alphabet to each row
        return counts / counts.sum(axis=1)[:, None] # normalize
    
    def getNonpositionalLetterScores(self):
        constrainingLetters = self._getBlacklistedLettersIndexes()^1 # inverted blacklist
        countPairs = Counter(''.join(self.corpus)) + Counter(self.alphabet)
        sortedCountPairs = sorted(countPairs.items(), key=lambda x: x[0])
        positionCounts = [count for char, count in sortedCountPairs]
        counts = np.array(positionCounts) - 1
        counts = counts * constrainingLetters
        return counts / (counts.sum() + 1)
    
    # Private methods
    def _getBlacklistedLettersIndexes(self):
        '''returns yellow or green constraining letters. Used for blacklisting
        letters from nonpositional scoring algorithm'''
        blacklist = set()
        for char in self.yellowConstraints:
            blacklist.add(char)

        for pool in self.pools:
            if len(pool) == 1:
                # len 1 is a green constraint
                blacklist.add(list(pool)[0]) # convert to char
        
        return np.array([int(char in blacklist) for char in sorted(self.alphabet)])