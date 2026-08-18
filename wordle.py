"""
File: wordle.py

Description: Core Wordle-solving logic. Filters the word list down to
candidates that match known letter positions/constraints, then scores
each candidate by summed letter frequency so the UI can rank guesses.
"""

from helpers import wordle_words


class Words:
    """Holds the word list, letter-frequency tables, and the search/scoring logic."""

    def __init__(self):
        self.map = dict()  # word -> score, populated by find()
        self.word_size = 5

        # General English letter frequency (%). Used by the UI to populate the
        # letter-selection list box (see WordleUI.create_list_box).
        self.letters = {
            "A": 8.34,
            "B": 1.54,
            "C": 2.73,
            "D": 4.14,
            "E": 12.60,
            "F": 2.03,
            "G": 1.92,
            "H": 6.11,
            "I": 6.71,
            "J": 0.23,
            "K": 0.87,
            "L": 4.24,
            "M": 2.53,
            "N": 6.80,
            "O": 7.70,
            "P": 1.66,
            "Q": 0.09,
            "R": 5.68,
            "S": 6.11,
            "T": 9.37,
            "U": 2.85,
            "V": 1.06,
            "W": 2.34,
            "X": 0.20,
            "Y": 2.04,
            "Z": 0.06,
        }

        # Recommended opening guesses, shown to the user on startup.
        self.starters = ['arose', 'soare', 'later',
                         'saine', 'tares', 'lares',
                         'rales', 'rates', 'cares',
                         'abide', 'piose', 'tenia',
                         'sough', 'atone', 'notes',
                         'audio', 'chevy', 'rides']

        # Letter frequency (%) specific to the Wordle answer list, used by score()
        # to rank candidate words.
        self.wordle_letters = {
            'S': 45.8,
            'E': 44,
            'A': 41.1,
            'O': 30.1,
            'R': 30.1,
            'I': 27.7,
            'L': 24,
            'T': 23.4,
            'N': 21.5,
            'U': 18.8,
            'D': 17.7,
            'Y': 15.7,
            'C': 14.8,
            'P': 14.5,
            'M': 14.4,
            'H': 13.2,
            'G': 11.9,
            'B': 11.7,
            'K': 11.1,
            'W': 7.9,
            'F': 7.6,
            'J': 0.23,
            'Q': 0.09,
            'V': 1.06,
            'X': 0.20,
            'Z': 0.06,

        }

    def score(self, word):
        """Sum per-letter Wordle-frequency scores for a word; higher is more likely useful."""
        score = 0
        for letter in word:
            score += self.wordle_letters[letter]
        return score

    def find(self, word_list, bad_list, wild_list, not_list, repeats):
        """Filter the word list down to valid candidates and score them.

        word_list: list of 5 known letters by position ('' if unknown/green not set).
        bad_list: letters confirmed absent from the word (gray).
        wild_list: letters known to be in the word but position unknown (yellow).
        not_list: list of 5 lists, letters known NOT to be at that position (yellow at a
                   different spot).
        repeats: if False, reject words with any repeated letter.

        Populates self.map with {WORD: score} for every candidate that passes all
        constraints.
        """
        word_list_len = len(word_list)

        self.map.clear()

        # A letter can't be both confirmed-absent and placed as a known letter.
        for letter in word_list:
            if letter in bad_list:
                print(f'{letter} in bad and good list')
                return

        count = 0
        for item in wordle_words.wordle_words:
            count += 1
            item_len = len(item)
            if item_len == self.word_size and isinstance(item, str):
                store = True
                check_list = list(item.upper())

                # Reject words containing any letter confirmed absent (gray).
                for letter in check_list:
                    if letter in bad_list:
                        store = False

                # Optionally reject words with repeated letters.
                if not repeats:
                    for i in range(len(check_list)):
                        for j in range(len(check_list)):
                            if j == i:
                                continue
                            elif check_list[i] == check_list[j]:
                                store = False
                                break

                if store:
                    for i in range(word_list_len):
                        # Reject if a known-yellow letter is placed where it's known
                        # not to belong.
                        if check_list[i] in not_list[i]:
                            store = False
                            break

                        # Reject if any known-present (yellow) letter is missing entirely.
                        for letter in wild_list:
                            if letter not in check_list:
                                store = False
                                break

                        # Match confirmed (green) letters by position; '' means unknown.
                        if word_list[i] == '' or word_list[i] == check_list[i]:
                            continue
                        elif word_list[i] != check_list[i]:
                            store = False
                            break

                    if store:
                        score = 0
                        # Only the first 2316 entries are common Wordle answers;
                        # words after that are valid guesses but not scored.
                        if count < 2316:
                            score = self.score(item.upper())
                        self.map[item.upper()] = score
