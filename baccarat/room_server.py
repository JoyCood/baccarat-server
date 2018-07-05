class GameRoomEventHandler:
    def __init__(self, room_players, logger):
        self._room_players = room_players
        self._logger = logger

    def room_event(self, protocol, message):
        for player in self._room_players.players:
            player.send_message(message)


class GameRoom(threading.Thread):
    def __init__(self, id, room_size):
        self._id = id
        self._room_players = GameRoomPlayers(room_size)
        self._lock = threading.Lock()
        super().__init__(target=self.activate)

    def join_room(self, player):
        self._lock.acquire()
        try:
            self.room_players.add_player(player)
        except DuplicateRoomPlayerException:
            old_player = self._room_players.get_player(player.id)
            old_player.send_message(common_pb2.KICKOUT, message)
            old_player.update_channel(player)
        finally:
            self._lock.release()

    def leave(self, player_id):
        self._lock.acquire()
        try:
            player = self._room_players.get_player(player_id)
            self._room_players.remove_player(player.id)
            self._room_event_handler.room_event() #向房间内的玩家广播有玩家离开房间
        finally:
            self._lock.release()

    def activate(self):
        while True:
            try:
                game = Game(self._id)
                game.event_dispatcher.subscribe(self)
                game.start()
            except GameError:
                break


