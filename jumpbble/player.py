class Status:
    TURNS = 3


class Diagonal(Status):
    """
    Must place pieces diagonally.
    """

    pass


class Ordered(Status):
    """
    Letters become ordered.
    """

    pass


class Wildcard(Status):
    """
    Allows selecting any piece from bag.
    """

    pass


class Jump(Status):
    """
    Ignore tile value and place on any position on board.
    """

    pass


class Blind(Status):
    """
    Disables viewing piece.
    """

    pass


class Erase(Status):
    """
    Piece placement erases pre-existing pieces.
    """

    pass


class Player:
    def __init__(self, char: str):
        self.char = char
        self.experience = 0

    @property
    def level(self):
        return self.experience // 10
