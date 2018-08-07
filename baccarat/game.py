import time
import threading

from baccarat.contract import (
    Contract,
)
from baccarat.exceptions import (
    EndGameException,
    MoneyNotEnoughException,
    MoneyValueInvalidException,
)

class Game(object):
    def __init__(self, room_id, game_event_dispatcher, logger):
        self._room_id = room_id
        self._game_event_dispatcher = game_event_dispatcher
        self._deal_card = threading.Event()
        self._logger = logger
        self._contract_shuffle = ContractShuffle(self._room_id)
        #self._bets = {'bank':{}, 'play':{}, 'tie': {}}

    def start(self):
        self._logger.info('new game start')
        self._shuffle()
        while True:
            try:
                time.sleep(5)
                self.deal()
            except EndGameException:
                break

    def bet(self, player, type, money):
        #开牌中，不能下注
        if self._deal_card.is_set():
            self._logger.exception('DealCardTimeException')
        else:
            self._logger.info('bet success')
            self._game_event_dispatcher.bet_event(player, type, money)
            try:
                player.take_money(money)
            except MoneyNotEnoughException:
                self._logger.error(
                    "player id:{}, money not enough".format(player.id)
                )
            except MoneyValueInvalidException:
                self._logger.error(
                    "player id:{}, money value `{}` invalid".format(
                        player.id,
                        money
                    )
                )

            self._logger.info("after bet, player id:{}, money leave:{}".format(player.id,
                player.money))

        #if to in self.bets:
        #    self.bets[to][player.id] += bet

    #洗牌
    def _shuffle(self):
        self._logger.info('shuffle')
        contract_shuffle.shuffle(self._room_id)

    def deal(self):
        try:
            self._deal_card.set()
            self._logger.info('deal')
            #contract.deal(self._room_id)
            raise EndGameException
        except EndGameException:
            self._detect_winners()
            raise
        finally:
            self._deal_card.clear()

    def _detect_winners(self):
        self._logger.info('detect winners')

