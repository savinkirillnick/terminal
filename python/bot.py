

class Bot:
    def __init__(self):
        """Класс настроек бота"""
        self.error = ''
        self.api_key = ''
        self.api_secret = ''
        self.opt_key = ''
        self.exchange = ''
        self.pair = ''
        self.upd_time = 1.0
        self.num_set = ''

    def upd(self, data):
        """Обновление настроек из словаря data"""
        self.api_key = data['api_key'] if 'api_key' in data else self.api_key
        self.api_secret = data['api_secret'] if 'api_secret' in data else self.api_secret
        self.opt_key = data['opt_key'] if 'opt_key' in data else self.opt_key
        self.exchange = data['exchange'] if 'exchange' in data else self.exchange
        self.pair = data['pair'] if 'pair' in data else self.pair
        self.num_set = data['num_set'] if 'num_set' in data else self.num_set
        self.upd_time = data['upd_time'] if 'upd_time' in data else self.upd_time

    def get_set_data(self):
        """Получение настроек в виде словаря"""
        data = dict()
        data['api_key'] = self.api_key
        data['api_secret'] = self.api_secret
        data['opt_key'] = self.opt_key
        data['num_set'] = self.num_set
        data['exchange'] = self.exchange
        data['pair'] = self.pair
        data['upd_time'] = self.upd_time
        return data

    def clear(self):
        """Обнуление настроек"""
        self.error = ''
        self.api_key = ''
        self.api_secret = ''
        self.opt_key = ''
        self.exchange = ''
