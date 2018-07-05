import threading

from docs import (
    conf,
    protocol,        
)

class BaseEventHandler:

    def broadcast(self, event, message):
        for player in self._room.room_players.players:
            player.try_send_message(event, message)

    def event(self, event, message):
        self._logger.debug(
            "\n" + 
            ("-" * 80) + "\n"
            "ROOM: {}\nEVENT: {}\nMESSAGE: {}\nSEATS:\n - {}".format(
                self._room.id,
                event,
                message,
                "\n -".join([str(seat) if seat is not None else "empty" for seat in self._room.room_players.players])
            ) + "\n" +
            ("-" * 80) + "\n"
        )
        self.broadcast(event, message)


class LobbyEventDispatcher:

    @staticmethod
    def loggin_event(player):
        response = protocol.HallListResponse()
        for item in conf.HALLS:
            hall = response.hall.add()
            hall.id = item['id']
            hall.title = item['title']
            hall.min = item['min_coin']
            hall.max = item['max_coin']
        response.error_code = protocol.SUCCESS
        player.send_message(protocol.HALL_LIST, response)

class RoomEventDispatcher(BaseEventHandler):
    def __init__(self, room, logger):
        self._room = room
        self._logger = logger

    def join_room_event(self, player):
        room_players = self._room.room_players
        response = protocol.JoinRoomResponse()
        response.room_id = self._room.id
        response.player_id = player.id

        for item in room_players.players:
            player = response.players.add()
            player.id = item.id
            player.name = item.name
            player.money = item.money
        for seat_id, player_id in enumerate(room_players.seats):
            seat = response.seats.add()
            seat.id = seat_id
            seat.player_id = player_id if player_id else ""
        response.error_code = protocol.SUCCESS
        self.event(protocol.JOIN_ROOM, response)

class GameEventDispatcher(BaseEventHandler):
    def __init__(self, room, logger):
        self._room = room
        self._event_messages = []
        self._logger = logger
        self._lock = threading.Lock()

    def new_game_event(self):pass

    def deal_event(self):pass

    def bet_event(self, player, type, money):
        response = protocol.BetResponse()
        response.player_id = player.id
        response.type = type
        response.money = money
        response.error_code = protocol.SUCCESS
        self.event(protocol.BET, response)

    def game_over_event(self):
        response = protocol.GameOverResponse()
        response.error_code = protocol.SUCCESS
        self.event(protocol.GAME_OVER, response)

    def leave_room_event(self, player):
        response = protocol.LeaveRoomResponse()
        response.player_id = player.id
        response.error_code = protocol.SUCCESS
        self.event(protocol.LEAVE_ROOM, response)

    def game_event(self, event, message):
        with self._lock:
            if message.HasField('target') and message.target:
                player = self._room_players.get_player(message.target)
                player.send_message(message)
            else:
                self.broadcast(event, message)
            if protocol == event.GAME_OVER:
                self._event_messages = []
            else:
                self._event_messages.append(message)
