import threading

class Lobby(object):
    def __init__(self):
        self._lock = threading.Lock()
        self._players = {}
        self._channel = {}

    #用户登录大厅
    def player_join(self, player): 
        self._lock.acquire()
        try:
            self._players[player.id] = player
            self._channel[player.channel] = player.id
        finally:
            self._lock.release()
        
    #用户离开大厅
    def player_leave(self, player_id):
        self._lock.acquire()
        try:
            del self._players[player_id]
        except KeyError:
            pass
        finally:
            self._lock.release()

    def get_player(self, socket):
        self._lock.acquire()
        try:
            player_id = self._channel[socket]
            return self._players[player.id]
        except KeyError:
            raise UnknowLobbyPlayerException
        finally:
            self._lock.release()

    #获取大厅玩家列表
    @property
    def players(self):
        self._lock.acquire()
        try:
            return [self._players[player_id] for player_id in self._players]
        finally:
            self._lock.release()

