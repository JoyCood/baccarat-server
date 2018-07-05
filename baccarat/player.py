import threading
import struct
from baccarat.exceptions import (
    ProtocolException,
    UnknownPlayerException,
    MoneyNotEnoughException,
    MoneyValueInvalidException,
)

class Player(object):
    def __init__(self, id, name, money):
        self._id = id
        self._name = name
        self._money = money
        self._room = None

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def money(self):
        return self._money

    @property
    def room(self):
        return self._room
    
    @room.setter
    def room(self, room):
        self._room = room

    def isset_room(self):
        return self._room is not None

    def take_money(self, money):
        if money > self._money:
            raise MoneyNotEnoughException
        if money < 0.0:
            raise MoneyValueInvalidException
        self._money -= money

    def add_money(self, money):
        if money <= 0.0:
            raise MoneyValueInvalidException
        self._money += money

    def __str__(self):
        return "player {}".format(self._id) 

class PlayerServer(Player):
    def __init__(self, channel, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._channel = channel

    @property
    def channel(self):
        return self._channel

    def update_channel(self, player):
        self.disconnect()
        self._channel = player.channel

    def disconnect(self):
        self.try_send_message()

    def try_send_message(self, protocol, message):
        try:
            self.send_message(protocol, message)
            return True
        except ChannelError:
            return False

    def send_message(self, protocol, message):
        message = self.pack_message(protocol, message)
        self._channel.sendall(message)

    def pack_message(self, protocol, message):
        if not isinstance(protocol, int):
            raise ProtocolException("protocol must an positive integer number")
        if not isinstance(message, bytes):
            body_length = message.ByteSize()
            packet = message.SerializeToString()
        else:
            body_length = len(message)
            packet = message
        header = struct.pack('>2I', body_length, protocol)
        return header + packet

 
class Players:
    def __init__(self):
        self._lock = threading.Lock()
        self._players = {}

    @property
    def players(self):
        self._lock.acquire()
        try:
            return [self._players[channel] for channel in self._players]
        finally:
            self._lock.release()

    def add_player(self, player):
        self._lock.acquire()
        try:
            if player.channel in self._players:
                raise DuplicatePlayerException
            else:
                self._players[player.channel] = player
        finally:
            self._lock.release()

    def get_player(self, channel):
        self._lock.acquire()
        try:
            return self._players[channel]
        except KeyError:
            raise UnknownPlayerException
        finally:
            self._lock.release()

    def remove_player(self, channel):
        self._lock.acquire()
        try:
            del self._players[channel]
        except KeyError:
            raise UnknownPlayerException
        finally:
            self._lock.release()



