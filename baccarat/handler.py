import sys

from baccarat.db import (
    Member,
) 
from docs import ( 
    conf,
    protocol,
)
from baccarat import (
    PlayerServer, 
    players,
    lobby,
    rooms,
)

from baccarat.events import (
    LobbyEventDispatcher,        
    GameEventDispatcher,
)

route = {
    protocol.REGISTER: 'register',
    protocol.LOGIN: 'login',
    protocol.CLOSE: 'close',
    protocol.JOIN_ROOM: 'join_room',
    protocol.LEAVE_ROOM: 'leave_room',
    protocol.BET: 'bet',
}

def handle(socket, event, data, logger):
    handler = route.get(event)
    if handler is None:
        return
    fun = getattr(sys.modules[__name__], handler)
    fun(socket, data, logger)

def register(socket, data):
    pass

def login(socket, data, logger):
    request = protocol.LoginRequest()
    request.ParseFromString(data)
    logger.info("phone:{}".format(request.phone))
    member = Member.find_one({'phone': request.phone})
    logger.info(member)
    player = PlayerServer(socket, id='1', name='joy', money=50)
    players.add_player(player)
    player = players.get_player(socket)

    logger.info(player)
    LobbyEventDispatcher.loggin_event(player)

def close(socket, data, logger):
    pass

def join_room(socket, data, logger):
    request = protocol.JoinRoomRequest()
    request.ParseFromString(data)
    logger.debug("join_room laby id:{}".format(request.lobby_id))
    try:
        player = players.get_player(socket)
    except UnknownLobbyPlayerException:
        logger.exception('UnknownLobbyPlayerException')
        response = protocol.JoinRoomResponse()
        response.error_code = protocol.NOT_LOGIN
    else:
        logger.info('join_room player_info id:{} name:{} money:{}'.format(player.id, player.name, player.money))
        rooms.join(player)

def leave_room(socket, data):
    request = protocol.LeaveRoomRequest()
    request.ParseFromString(data)
    try:
        player = players.get_player(socket)
    except UnknownLobbyPlayerException:
        response = protocol.LeaveRoomResponse()
        response.error_code = protocol.ERROR_NOT_LOGIN
    else:
        rooms.leave(player)

def bet(socket, data, logger):
    request = protocol.BetRequest()
    request.ParseFromString(data)
    logger.debug(data)
    try:
        player = players.get_player(socket)
    except UnknownLobbyPlayerException:
        logger.exception('bet UnknownLobbyPlayerException')
        response = protocol.BetResponse()
        response.error_code = protocol.ERROR_NOT_LOGIN
        player.send_message(protocol.BET, response)
        return

    if not player.isset_room(): 
        response = protocol.BetResponse()
        response.error_code = protocol.ERROR_NOT_IN_ROOM
    else:
        player.room.bet(player, request.type, request.money)


