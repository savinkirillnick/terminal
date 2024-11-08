from gui import *
from bot import *
from errors import *
from threadtimer import *
from user import *
from kline import *
from api import *
from db import *
from common import *
import sys


class App:
    def __init__(self):
        # Инициируем приложение в режиме debug
        self.debug = False
        for i in sys.argv:
            a = i.split("=")
            if a[0] == '--debug':
                self.debug = True
        
        # Запуск основных сервисов
        self.ttimer = ThreadTimer()
        self.errors = Errors()
        self.bot = Bot()
        self.user = User()
        self.kline = Kline()
        self.api = Api()
        self.db = DB(self)
        self.common = Common(self)
        self.gui = Gui(self)

    def start(self):
        self.gui.run()


if __name__ == "__main__":

    app = App()
    app.start()
