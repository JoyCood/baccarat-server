class GameException(Exception):
    pass

class EndGameException(GameException):
    pass

class ProtocolException(GameException):
    pass

class FullGameRoomException(GameException):
    pass

class DuplicateRoomPlayerException(GameException):
    pass

class UnknownRoomPlayerException(GameException):
    pass

class MoneyNotEnoughException(GameException):
    pass

class MoneyValueInvalidException(GameException):
    pass

class UnknownPlayerException(GameException):
    pass
