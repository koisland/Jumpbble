class Status:
    def __init__(self, turns: int) -> None:
        self.turns = turns

    def __add__(self):
        self.turns += 1

    def __sub__(self):
        if self.turns > 0:
            self.turns -= 1


class Diagonal(Status):
    """
    Must place pieces diagonally.
    """

    def __init__(self, turns: int) -> None:
        super().__init__(turns)


class Ordered(Status):
    """
    Letters become ordered.
    """

    def __init__(self, turns: int) -> None:
        super().__init__(turns)


class Wildcard(Status):
    """
    Allows selecting any piece from bag.
    """

    def __init__(self, turns: int) -> None:
        super().__init__(turns)


class Jump(Status):
    """
    Ignore tile value and place on any position on board.
    """

    def __init__(self, turns: int) -> None:
        super().__init__(turns)


class Blind(Status):
    """
    Disables viewing piece.
    """

    def __init__(self, turns: int) -> None:
        super().__init__(turns)


class Erase(Status):
    """
    Piece placement erases pre-existing pieces.
    """

    pass


class Mirror(Status):
    """
    Piece placement is mirrored. This ignores tile availabililty
    """

    pass


class Player:
    def __init__(self, char: str):
        self.char = char
        self.experience = 0
        self.status = {
            "mirror": Mirror(0),
            "diagonal": Diagonal(0),
            "ordered": Ordered(0),
            "wildcard": Wildcard(0),
            "jump": Jump(0),
            "blind": Blind(0),
            "erase": Erase(0),
        }

    @property
    def level(self):
        return self.experience // 10

    def is_affected(self, status: str) -> bool:
        if status_effect := self.status.get(status):
            if status_effect.turns != 0:
                return True
            else:
                return False
        else:
            print(f"Not a valid status effect: {status}")
