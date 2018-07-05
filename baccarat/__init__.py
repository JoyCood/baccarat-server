from pymongo import MongoClient

from baccarat.exceptions import (
    GameException, 
    FullGameRoomException, 
    DuplicateRoomPlayerException,
    UnknownRoomPlayerException, 
    ProtocolException
)
from baccarat.hall import (
        Lobby,
)
from baccarat.player import (
    PlayerServer, 
    Players
)
from baccarat.game import (
    Game,
) 
from baccarat.room import (
    Rooms,
)

mongo = MongoClient().baccarat
lobby = Lobby()
players = Players()
rooms = Rooms()

