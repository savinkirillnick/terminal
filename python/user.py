from time import time


class User:

    def __init__(self):
        """Класс настроек пользователя
        """
        self.name = 'Terminal'
        self.ver = '3.0.1o'
        self.build = '2024-11-08.231'
        self.shared_key = 'demo'
        self.demo_mode = False
        self.file_data = 0
        self.activation = UserActivation(self)
        self.api_is_init = False
        self.bot_is_init = False
        self.kl_is_init = False
        self.settings_list = list()
        self.rules = dict()
        self.coins = set()
        self.pairs = set()
        self.balances = dict()
        self.depth = dict()
        self.depth['bids'] = list()
        self.depth['asks'] = list()
        self.orders = list()
        self.trades = list()
        self.curr_base = ''
        self.curr_quote = ''
        self.queue_id = ''
        self.queue_side = ''
        self.last_price = 0.0
        self.delta_time = 0.0


class UserActivation:
    def __init__(self, parent):
        """Класс активации пользователя урезан до постоянного разрешения
        КТ
        """
        self.parent = parent

    def check(self):
        return True

