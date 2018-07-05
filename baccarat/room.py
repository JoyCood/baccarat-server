#!/usr/bin/python 
# -*- coding: utf-8 -*-

import threading
import time
import logging
from uuid import uuid4

from baccarat.exceptions import (
    FullGameRoomException, 
    DuplicateRoomPlayerException,
    UnknownRoomPlayerException, 
    GameException,
)

from docs import (
    conf,
    protocol,
)
from baccarat.game import (
    Game,
)
from baccarat.events import (
    RoomEventDispatcher,
    GameEventDispatcher,
)

class Room(threading.Thread):
    def __init__(self, id, room_size, logger):
        self._id = id
        self._logger = logger
        self._room_players = RoomPlayers(room_size)
        self._game_event_dispatcher = GameEventDispatcher(self, self._logger)
        self._room_event_dispatcher = RoomEventDispatcher(self, self._logger)
        self._event_message = []
        self._lock = threading.Lock()
        self._game = None
        super().__init__(target=self.activate)

    @property
    def id(self):
        return self._id

    @property
    def room_players(self):
        return self._room_players

    def join_room(self, player):
        try:
            self._room_players.add_player(player)
        except DuplicateRoomPlayerException:
            self._logger.exception('DuplicateRoomPlayerException')
        else:
            self._logger.debug('room_event_disaptcher.join_room_event')
            player.room = self
            self._room_event_dispatcher.join_room_event(player)

    def leave_room(self, player):
        try:
            self._room_players.remove_player(player)
        except UnknownRoomPlayerException:
            pass
        self._room_event_dispatcher.leave_room_event(player)
        if len(self._room_players.players)<1:
            raise GameError('game over')

    def bet(self, player, type, money):
        try:
            self._logger.info('bet action..')
            self._game.bet(player, type, money)
        except AttributeError:
            self._logger.error('not in bet status')

    def activate(self):
        while True:
            if len(self._room_players.players)<1:
                raise GameError('game Error')
            self._game = Game(self._id, self._game_event_dispatcher, self._logger)
            self._game.start()

class Rooms():
    def __init__(self):
        self._lock = threading.Lock()
        self._rooms = []
        self._room_maps = {}
        self._logger = logging.getLogger()

    def join(self, player):
        self._logger.debug('Rooms.join()')
        room = self._join(player)
        if not room.is_alive():
            room.start()

    def _join(self, player): 
        with self._lock:
            for room in self._rooms:
                try:
                    room.join_room(player)
                    return room
                except FullGameRoomException:
                    pass
            self._logger.debug('Rooms._join()')
            room_id = str(uuid4())
            room = Room(id=room_id, room_size=conf.room_size, logger=self._logger)
            self._logger.debug('create room')
            room.join_room(player)
            self._rooms.append(room)
            self._room_maps[room_id] = room
            return room

    def leave(self, player):
        with self._lock:
            try:
                room.leave_room(player)
            except UnknownRoomPlayerException:
                pass

    def remove_room(self, room_id):
        with self._lock:
            try:
                del self._room_maps[room_id]
            except KeyError:
                pass

class RoomPlayers:
    def __init__(self, room_size):
        self._seats = [None] * room_size
        self._players = {}
        self._lock = threading.Lock()

    @property
    def players(self):
        with self._lock:
            return [self._players[player_id] for player_id in self._seats if player_id is not None]

    @property
    def seats(self):
        with self._lock:
            return list(self._seats)

    def get_player(self, player_id):
        with self._lock:
            try:
                return self._players[player_id]
            except KeyError:
                raise UnknownRoomPlayerException

    def add_player(self, player):
        with self._lock:
            if player.id in self._players:
                raise DuplicateRoomPlayerException
            try:
                free_seat = self._seats.index(None)
            except ValueError:
                raise FullGameRoomException
            else:
                self._seats[free_seat] = player.id
                self._players[player.id] = player

    def remove_player(self, player_id):
        with self._lock:
            try:
                seat = self._seats.index(player_id)
            except ValueError:
                raise UnknownRoomPlayerException
            else:
                self._seats[seat] = None
                del self._players[player_id]
