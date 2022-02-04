from WordleGuesser import WordleGuesser
from CorpusCreator import CORPUS_OUT_PATH
import pickle
import random

class WordleSimulator:
    def __init__(self, corpusFilePath):
        self.corpus = None
        with open(corpusFilePath, 'rb') as file:
            self.corpus = pickle.load(file)
        self.guesser = WordleGuesser(self.corpus.copy(), True)
    
    def run(self, firstGuess, verbose=True, samples=10, sampleSize=500):
        averages = []
        for sample in range(samples):
            numGuesses = []
            print(f"Starting sample {sample} of {samples}, size {sampleSize}")
            for i, word in enumerate(random.sample(self.corpus,sampleSize)):
                if verbose and i % 100 == 0:
                    print(f"\tWord {i} of {sampleSize}")
                guess = 1
                guessWord = firstGuess
                while guessWord != word:
                    letterColors = self.compareGuess(word, guessWord)
                    self.guesser.machineGuess(guessWord, letterColors)
                    guessWord = self.guesser.getBestGuess()
                    guess += 1
                numGuesses.append(guess)
                self.guesser.reset(True)
            averages.append(sum(numGuesses) / len(numGuesses))
            print(f"\tsample avg - {averages[-1]}")
        return sum(averages) / samples
    
    def compareGuess(self, word, guess):
        colors = []
        for expected, actual in zip(word, guess):
            if expected == actual:
                colors.append(self.guesser.Color.GREEN)
            elif actual in word:
                colors.append(self.guesser.Color.YELLOW)
            else:
                colors.append(self.guesser.Color.GRAY)
        return colors

if __name__ == "__main__":
    simulator = WordleSimulator(CORPUS_OUT_PATH)
    firstGuess = input("What word would you like to simulate? Type 'quit' to quit.").strip()
    while firstGuess != 'quit':
        print(f"Simulating starting word: {firstGuess}.\n")
        numGuesses = simulator.run(firstGuess)
        print(f"Starting word {firstGuess} averaged {numGuesses:.2f} guesses per word.\n")
        firstGuess = input("What word would you like to simulate? Type 'quit' to quit.").strip()