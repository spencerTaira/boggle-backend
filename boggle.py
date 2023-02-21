"""Code for the logic of boggle game."""

from random import choice
from wordlist import english_words

DEFAULT_LETTERS_BY_FREQ = (
        "EEEEEEEEEAAAAAAAOOOOOOIIIIUUU" +  # super-common
        "RRRRRSSSSSSTTTTTLLLLNNN" +  # common
        "BBCCDDFFGGHHKKMMPPYY" +  # less common
        "JVWXZ")  # rare (we never include Q)


class BoggleGame():
    """A game for Boggle, where it can find words on the board."""

    def __init__(self,
                 word_list=english_words,
                 board_size=5,
                 fill_letters=DEFAULT_LETTERS_BY_FREQ,
                 word_length_scores={3: 1, 4: 1, 5: 2, 6: 3, 7: 5},
                 max_word_length_score=11,
                 ):
        """Create empty board and fill with random letters.

        - word_list: instance of WordList class [defaults to english]
        - board_size: size of board [defaults to 5]
        - fill_letters: letters to fill board with
        - board: can supply board letters (list of list)

        You can make a game like:

            >>> game = BoggleGame()

        You score in the game by playing words:

            >>> game.play_and_score_word("CAT")
            1
            >>> game.play_and_score_word("HIPPO")
            2
            >>> game.play_and_score_word("OPULENCE")
            11
            >>> game.score
            14

        It keeps track of played words, so you can check if a word is a
        duplicate:

            >>> game.is_word_not_a_dup("CAT")
            False
            >>> game.is_word_not_a_dup("DOG")
            True

        You can check if a word is in the valid word list:

            >>> game.is_word_in_word_list("STILL")
            True
            >>> game.is_word_in_word_list("XXX")
            False

        The `.check_word_on_board` method has its own tests, below.
        """

        self.word_list = word_list
        self.board_size = board_size
        self.word_length_scores = word_length_scores
        self.max_word_length_score = max_word_length_score

        self.board = self.get_random_board(fill_letters)
        self.played_words = set()
        self.score = 0

    def __repr__(self):
        board_text = ".".join(["".join(row) for row in self.board])
        return (f"<BoggleGame board={board_text}"
                + f" played_words={self.played_words}>")

    def get_random_board(self, fill_letters):
        """Return a random board (a list of lists)."""

        board = []
        for y in range(self.board_size):
            board.append(
                [choice(fill_letters) for x in range(self.board_size)])

        return board

    def play_and_score_word(self, word):
        """Score a Boggle word and add to played words. Returns game score."""

        assert len(word) >= 3, "1- or 2-letter words shouldn't have been legal"

        word_score = self.word_length_scores.get(
            len(word), self.max_word_length_score)

        self.played_words.add(word)
        self.score += word_score

        return word_score

    def is_word_not_a_dup(self, word):
        """Return True/False if a word has not already been played."""

        return word not in self.played_words

    def is_word_in_word_list(self, word):
        """Return True/False if the word is in our word list."""

        return self.word_list.check_word(word)

    def check_word_on_board(self, word):
        """Can word be found in board? Returns True/False.

        Let's make a game and fill the board with a forced example:

            >>> game = BoggleGame(board_size=3)
            >>> game.board = ["C","A","T"], ["O", "X", "X"], ["X", "G", "X"]

        It searches to find word horizontally, vertically, or diagonally:

            >>> game.check_word_on_board("CAT")
            True

            >>> game.check_word_on_board("COG")
            True

        It cannot use the same tile twice, though:

            >>> game.check_word_on_board("TAT")
            False
        """

        # Find starting letter --- try every spot on board and,
        # win fast, should we find the word at that place.

        for y, row in enumerate(self.board):
            for x, cell in enumerate(row):
                if self._find_from(word, y, x, seen=set()):
                    return True

        # Tried every path from every starting square w/o luck. Sad panda.
        return False

    def _find_from(self, word, y, x, seen):
        """Can we find a word on board, starting at x, y?

        - word: word in all uppercase
        - y, x: coordinates to start search
        - seen: set of of (y,x) starting places already checked

        Returns True/False
        """

        # This is called recursively to find smaller and smaller words
        # until all tries are exhausted or until success.

        # if we're searching off the board, current recursion fails
        if x < 0 or x >= self.board_size or y < 0 or y >= self.board_size:
            return False

        # Base case: this isn't the letter we're looking for.
        if self.board[y][x] != word[0]:
            return False

        # Base case: we've used this letter before in this current path
        if (y, x) in seen:
            return False

        # Base case: we are down to the last letter --- so we win!
        if len(word) == 1:
            return True

        # Otherwise, this letter is good, so note that we've seen it, and try of
        # all of its neighbors for the first letter of the rest of the word/

        # This next line is a bit tricky: we want to note that we've seen the
        # letter at this location. However, we only want the child calls of this
        # to get that, and if we used `seen.add(...)` to add it to our set,
        # *all* calls would get that, since the set is passed around. That would
        # mean that once we try a letter in one call, it could never be tried
        # again, even in a totally different path. Therefore, we want to create
        # a *new* seen set that is equal to this set plus the new letter. Being
        # a new object, rather than a mutated shared object, calls that don't
        # descend from us won't have this `y,x` point in their seen.
        #
        # To do this, we use the | (set-union) operator, read this as "rebind
        # seen to the union of the current seen and the set of point(y,x))."

        seen = seen | {(y, x)}

        rest_of_word = word[1:]

        # Search every letter (horiz, vert, diagonal) from here
        for dx in [-1, 0, +1]:
            for dy in [-1, 0, +1]:
                # already on the center letter, so don't use that
                if dx == dy == 0:
                    continue

                # here's the recursion
                if self._find_from(rest_of_word, y + dy, x + dx, seen):
                    return True

        # Couldn't find the next letter, so this path is dead
        return False
