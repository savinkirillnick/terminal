from math import log10
from os import remove
from os.path import isfile
from threading import Thread
from time import time, sleep, strftime, localtime

import ccxt
import requests


class Common:
    
    def __init__(self, app):
        """Класс основных функций цикла программы.
        """
        self.app = app
        self.exchanges = ccxt.exchanges

    def launch(self):
        """Функция запуска подпроцессов.
        """
        mode = ''
        if self.app.user.demo_mode:
            mode = 'in demo mode'
        self.app.gui.log(f'Welcome to Terminal ver.{self.app.user.ver} {mode}')

        try:
            self.app.user.settings_list = self.app.db.get_settings_list()
        except Exception as e:
            self.app.errors.error(106, e)
            self.app.user.settings_list = list()

        if self.app.user.shared_key != 'demo':
            try:
                self.app.db.save_key(self.app.user.shared_key)
            except Exception as e:
                self.app.errors.error(101, e)

        Thread(target=self.update_depth, daemon=True).start()
        Thread(target=self.update_price, daemon=True).start()
        Thread(target=self.update_orders, daemon=True).start()
        Thread(target=self.update_trades, daemon=True).start()
        Thread(target=self.update_balances, daemon=True).start()
        Thread(target=self.update_main, daemon=True).start()

    def update_depth(self):
        """Цикл получения данных стакана.
        """
        def get_depth():
            try:
                depth = self.app.api.fetch_order_book(self.app.user.rules[self.app.bot.pair]['symbol'], None)
            except Exception as e:
                self.app.errors.error(128, e)
                depth = dict()
            if depth:
                self.app.user.depth = depth

        while True:
            try:
                if self.app.user.bot_is_init and self.app.user.api_is_init:
                    get_depth()
                    self.app.gui.win_main.progress(self.app.gui.win_main.progress_depth)
                    if self.app.gui.win_depth.winfo_exists():
                        self.app.gui.win_depth.view_depth()
                sleep(self.app.bot.upd_time)
            except Exception as e:
                self.app.errors.error(152, e)

    def update_price(self):
        """Цикл получения данных последней цены котировки.
        """
        def get_price():
            try:
                last_price = self.app.api.fetch_ticker(self.app.user.rules[self.app.bot.pair]['symbol'])
            except Exception as e:
                self.app.errors.error(127, e)
                last_price = dict()
            if last_price:
                self.app.user.last_price = last_price['last']
                if self.app.user.kl_is_init is not True:
                    self.app.user.kl_is_init = True
                self.app.kline.add(self.app.user.last_price)
                if self.app.strategy.sell_at.lower() == 'stop':
                    self.app.trailing.check()

        while True:
            try:
                if self.app.user.bot_is_init and self.app.user.api_is_init:
                    get_price()
                    if self.app.user.bot_is_run and self.app.user.last_price:
                        self.app.strategy.check(self.app.user.last_price, self.app.position.price)
                    self.app.gui.win_main.progress(self.app.gui.win_main.progress_price)
                    if self.app.gui.win_chart.winfo_exists():
                        self.app.gui.win_chart.canvas.forget()
                        self.app.gui.win_chart.draw()
                sleep(self.app.bot.upd_time)
            except Exception as e:
                self.app.errors.error(153, e)

    def update_orders(self):
        """Цикл получения данных открытых ордеров.
        """
        def get_orders():
            try:
                orders = self.app.api.fetch_open_orders(self.app.user.rules[self.app.bot.pair]['symbol'])
            except Exception as e:
                self.app.errors.error(130, e)
                orders = list()

            if orders:
                self.app.user.orders = orders
            else:
                self.app.user.orders = list()

        while True:
            try:
                if self.app.ttimer.check(time()):
                    if self.app.user.bot_is_init and self.app.user.api_is_init:
                        get_orders()
                        self.app.gui.win_main.progress(self.app.gui.win_main.progress_orders)
                        if self.app.gui.win_orders.winfo_exists():
                            self.app.gui.win_orders.view_orders()
                    sleep(10)
                else:
                    sleep(1)
            except Exception as e:
                self.app.errors.error(154, e)

    def update_trades(self):
        """Цикл получения данных истории совершенных ордеров.
        """
        def get_trades():
            try:
                trades = self.app.api.fetch_my_trades(self.app.user.rules[self.app.bot.pair]['symbol'], None)

            except Exception as e:
                self.app.errors.error(134, e)
                trades = list()

            if trades:
                self.app.user.trades = trades if len(trades) < 10 else trades[-10:]

        def check_trades():

            if len(self.app.user.trades) > 0:
                try:
                    tmp = list()
                    for i in range(len(self.app.user.trades)):
                        if self.app.user.trades[i]['timestamp'] / 1000 > self.app.user.last_trade_time:
                            tmp.append(self.app.user.trades[i])

                except Exception as e:
                    self.app.errors.error(135, e)

        while True:
            try:
                if self.app.ttimer.check(time()):
                    if self.app.user.bot_is_init and self.app.user.api_is_init:
                        get_trades()
                        check_trades()
                        self.app.gui.win_main.progress(self.app.gui.win_main.progress_trades)
                        if self.app.gui.win_trades.winfo_exists():
                            self.app.gui.win_trades.view_trades()
                    sleep(10)
                else:
                    sleep(1)
            except Exception as e:
                self.app.errors.error(155, e)

    def update_balances(self):
        """Цикл получения данных по балансам монет.
        """
        def get_balances():
            try:
                balances = self.app.api.fetch_balance()
            except Exception as e:
                self.app.errors.error(137, e)
                balances = dict()

            if balances is not dict():
                self.app.user.balances = balances
                if self.app.user.curr_quote.upper() not in balances.keys():
                    self.app.user.balances[self.app.user.curr_quote.upper()] = dict()
                    self.app.user.balances[self.app.user.curr_quote.upper()]['free'] = 0.0
                    self.app.user.balances[self.app.user.curr_quote.upper()]['used'] = 0.0
                    self.app.user.balances[self.app.user.curr_quote.upper()]['total'] = 0.0
                if self.app.user.curr_base.upper() not in balances.keys():
                    self.app.user.balances[self.app.user.curr_base.upper()] = dict()
                    self.app.user.balances[self.app.user.curr_base.upper()]['free'] = 0.0
                    self.app.user.balances[self.app.user.curr_base.upper()]['used'] = 0.0
                    self.app.user.balances[self.app.user.curr_base.upper()]['total'] = 0.0

        while True:
            try:
                if self.app.ttimer.check(time()):
                    if self.app.user.bot_is_init and self.app.user.api_is_init:
                        get_balances()
                        self.app.gui.win_main.progress(self.app.gui.win_main.progress_balances)
                    sleep(10)
                else:
                    sleep(1)
            except Exception as e:
                self.app.errors.error(156, e)

    def update_main(self):
        """Основной цикл программы.
        """
        while True:
            try:
                if self.app.user.bot_is_init and self.app.user.api_is_init:

                    if self.app.gui.win_terminal.winfo_exists():
                        self.app.gui.win_terminal.view_terminal()

                    self.app.gui.win_main.progress(self.app.gui.win_main.progress_main)
                sleep(1.0)

            except Exception as e:
                self.app.errors.error(157, e)

    def cancel_order(self, order_id=''):
        """Функция отмены ордера.
        """
        id = order_id if order_id != '' else self.app.user.queue_id if self.app.user.queue_id != '' else ''
        if id != '':
            try:
                cancel = self.app.api.cancel_order(id, self.app.user.rules[self.app.bot.pair]['symbol'])
            except Exception as e:
                self.app.errors.error(131, e)
                cancel = 0
            if cancel:
                self.app.gui.log('Order canceled')
                self.app.user.queue_id = ''

                self.app.user.queue_side = ''

                for i in range(len(self.app.user.orders)):
                    if self.app.user.orders[i]['id'] == id:
                        del self.app.user.orders[i]
                        break
                if self.app.gui.win_orders.winfo_exists():
                    self.app.gui.win_orders.view_orders()
                return True
        return False

    def update_settings(self, data={}):
        """Обновление настроек.
        """
        if not data:
            data = self.app.gui.win_settings.get_set_data()

        if self.app.bot.exchange != data['exchange'].lower() or self.app.bot.pair != data['pair'].lower():
            self.app.user.depth['bids'] = list()
            self.app.user.depth['asks'] = list()
            self.app.user.trades = list()
            self.app.user.orders = list()
            self.app.user.kl_is_init = False
            self.app.kline.reset()

        self.app.gui.root.title(self.app.user.name + ' ' + self.app.user.ver + ' > ' + data['exchange'].capitalize() + ' > ' + data['pair'].upper())

        if self.app.bot.exchange != data['exchange'].lower():
            self.app.user.api_is_init = False

        self.app.bot.upd(data)
        self.app.position.upd()
        self.app.strategy.upd(data)
        self.app.trailing.upd()
        self.app.stat.set_depo(self.app.bot.depo)
        self.app.user.curr_base = data['pair'].split('_')[0]
        self.app.user.curr_quote = data['pair'].split('_')[1]

        self.app.user.bot_is_init = True
        self.app.user.pos_is_init = True
        self.app.user.st_is_init = True

        self.app.gui.log(self.app.user.name + ' settings updated')

        while not self.app.user.api_is_init:
            try:
                self.api_init()
            except Exception as e:
                self.app.errors.error(125, e)
                self.app.gui.log(str(e))
                self.app.bot.clear()
                self.app.position.clear()
                break

    def delete_set(self):
        """Удаление сета настроек.
        """
        try:
            self.app.db.del_bot_settings(self.app.gui.win_settings.entry_set.get())
        except Exception as e:
            self.app.errors.error(103, e)
        self.app.user.settings_list = self.app.db.get_settings_list()
        self.app.gui.win_settings.entry_set.configure(values=self.app.user.settings_list)
        self.app.gui.log('Set #' + self.app.gui.win_settings.entry_set.get() + ' deleted')

    def save_set(self):
        """Сохранение сета настроек.
        """
        self.update_settings()
        data = self.app.gui.win_settings.get_set_data()
        try:
            self.app.db.save_bot_settings(self.app.gui.win_settings.entry_set.get(), data)
        except Exception as e:
            self.app.errors.error(104, e)
        self.app.user.settings_list = self.app.db.get_settings_list()
        self.app.gui.win_settings.entry_set.configure(values=self.app.user.settings_list)
        self.app.gui.log('Set #' + self.app.gui.win_settings.entry_set.get() + ' saved')

    def load_set(self, set_num=''):
        """Загрухка сета настроек.
        """
        if not set_num:
            set_num = self.app.gui.win_settings.entry_set.get()
        try:
            if set_num:
                data = self.app.db.load_bot_settings(set_num)
            else:
                data = self.app.db.load_bot_settings(self.app.gui.win_settings.entry_set.get())

            self.update_settings(data)

            if self.app.gui.win_settings.winfo_exists():
                self.app.gui.win_settings.view_settings()

            self.app.gui.log('Set #' + self.app.gui.win_settings.entry_set.get() + ' loaded')
        except Exception as e:
            self.app.errors.error(105, e)
            self.app.gui.log('Set #' + self.app.gui.win_settings.entry_set.get() + ' is not loaded')

        try:
            self.app.alarm.upd(self.app.db.load_alarm(self.app.bot.exchange, self.app.bot.pair))
        except Exception as e:
            self.app.errors.error(115, e)
        self.app.bot.num_set = self.app.gui.win_settings.entry_set.get()
        price, qty = 0.0, 0.0
        try:
            price, qty = self.app.db.load_position(self.app.bot.exchange, self.app.bot.pair)
        except Exception as e:
            self.app.errors.error(111, e)
        self.app.position.set_data({'exchange': self.app.bot.exchange, 'pair': self.app.bot.pair, 'price': price, 'qty': qty})
        try:
            self.app.strategy.upd(self.app.db.load_strategy(exchange=self.app.bot.exchange, pair=self.app.bot.pair))
        except Exception as e:
            self.app.errors.error(113, e)
        self.app.trailing.upd()
        self.app.trailing.reset()

    def api_init(self):
        """Инициализация API.
        """
        x = self.app.bot.exchange.lower()

        ccxt_api = {
            'ace': ccxt.ace,
            'alpaca': ccxt.alpaca,
            'ascendex': ccxt.ascendex,
            'bequant': ccxt.bequant,
            'bigone': ccxt.bigone,
            'binance': ccxt.binance,
            'binancecoinm': ccxt.binancecoinm,
            'binanceus': ccxt.binanceus,
            'binanceusdm': ccxt.binanceusdm,
            'bingx': ccxt.bingx,
            'bit2c': ccxt.bit2c,
            'bitbank': ccxt.bitbank,
            'bitbay': ccxt.bitbay,
            'bitbns': ccxt.bitbns,
            'bitcoincom': ccxt.bitcoincom,
            'bitfinex': ccxt.bitfinex,
            'bitfinex2': ccxt.bitfinex2,
            'bitflyer': ccxt.bitflyer,
            'bitget': ccxt.bitget,
            'bithumb': ccxt.bithumb,
            'bitmart': ccxt.bitmart,
            'bitmex': ccxt.bitmex,
            'bitopro': ccxt.bitopro,
            'bitpanda': ccxt.bitpanda,
            'bitrue': ccxt.bitrue,
            'bitso': ccxt.bitso,
            'bitstamp': ccxt.bitstamp,
            'bitteam': ccxt.bitteam,
            'bitvavo': ccxt.bitvavo,
            'bl3p': ccxt.bl3p,
            'blockchaincom': ccxt.blockchaincom,
            'blofin': ccxt.blofin,
            'btcalpha': ccxt.btcalpha,
            'btcbox': ccxt.btcbox,
            'btcmarkets': ccxt.btcmarkets,
            'btcturk': ccxt.btcturk,
            'bybit': ccxt.bybit,
            'cex': ccxt.cex,
            'coinbase': ccxt.coinbase,
            'coinbaseadvanced': ccxt.coinbaseadvanced,
            'coinbaseexchange': ccxt.coinbaseexchange,
            'coinbaseinternational': ccxt.coinbaseinternational,
            'coincheck': ccxt.coincheck,
            'coinex': ccxt.coinex,
            'coinlist': ccxt.coinlist,
            'coinmate': ccxt.coinmate,
            'coinmetro': ccxt.coinmetro,
            'coinone': ccxt.coinone,
            'coinsph': ccxt.coinsph,
            'coinspot': ccxt.coinspot,
            'cryptocom': ccxt.cryptocom,
            'currencycom': ccxt.currencycom,
            'delta': ccxt.delta,
            'deribit': ccxt.deribit,
            'digifinex': ccxt.digifinex,
            'exmo': ccxt.exmo,
            'fmfwio': ccxt.fmfwio,
            'gate': ccxt.gate,
            'gateio': ccxt.gateio,
            'gemini': ccxt.gemini,
            'hashkey': ccxt.hashkey,
            'hitbtc': ccxt.hitbtc,
            'hitbtc3': ccxt.hitbtc3,
            'hollaex': ccxt.hollaex,
            'htx': ccxt.htx,
            'huobi': ccxt.huobi,
            'huobijp': ccxt.huobijp,
            'hyperliquid': ccxt.hyperliquid,
            'idex': ccxt.idex,
            'independentreserve': ccxt.independentreserve,
            'indodax': ccxt.indodax,
            'kraken': ccxt.kraken,
            'krakenfutures': ccxt.krakenfutures,
            'kucoin': ccxt.kucoin,
            'kucoinfutures': ccxt.kucoinfutures,
            'kuna': ccxt.kuna,
            'latoken': ccxt.latoken,
            'lbank': ccxt.lbank,
            'luno': ccxt.luno,
            'lykke': ccxt.lykke,
            'mercado': ccxt.mercado,
            'mexc': ccxt.mexc,
            'ndax': ccxt.ndax,
            'novadax': ccxt.novadax,
            'oceanex': ccxt.oceanex,
            'okcoin': ccxt.okcoin,
            'okx': ccxt.okx,
            'onetrading': ccxt.onetrading,
            'oxfun': ccxt.oxfun,
            'p2b': ccxt.p2b,
            'paradex': ccxt.paradex,
            'paymium': ccxt.paymium,
            'phemex': ccxt.phemex,
            'poloniex': ccxt.poloniex,
            'poloniexfutures': ccxt.poloniexfutures,
            'probit': ccxt.probit,
            'timex': ccxt.timex,
            'tokocrypto': ccxt.tokocrypto,
            'tradeogre': ccxt.tradeogre,
            'upbit': ccxt.upbit,
            'vertex': ccxt.vertex,
            'wavesexchange': ccxt.wavesexchange,
            'wazirx': ccxt.wazirx,
            'whitebit': ccxt.whitebit,
            'woo': ccxt.woo,
            'woofipro': ccxt.woofipro,
            'xt': ccxt.xt,
            'yobit': ccxt.yobit,
            'zaif': ccxt.zaif,
            'zonda': ccxt.zonda
        }

        try:
            if x in ccxt.exchanges:

                # Получаем список наобходимых данных
                required = ccxt_api[x].requiredCredentials

                # Формируем словарь аргументов
                args = dict()
                args.update({key: self.app.bot.opt_key for key in required})
                args.update({'apiKey': self.app.bot.api_key, 'secret': self.app.bot.api_secret})

                # запускаем инициализацию api
                self.app.api = ccxt_api[x](args)

        except Exception as e:

            self.app.gui.log('Initialization API error. Change exchange to another and try again.')
            self.app.api = None

        if self.app.api:
            server_time = 0.0

            if not server_time:
                try:
                    server_time = self.app.api.fetch_time()
                except:
                    pass

            if not server_time:
                try:
                    server_time = self.app.api.fetch_ticker(self.app.api.fetch_markets()[0]['symbol'])['timestamp']
                except:
                    pass

            if not server_time:
                server_time = time() * 1000

            self.app.user.delta_time = time() - server_time / 1000

            rules = self.app.api.load_markets()

            self.app.user.rules = {}
            self.app.user.coins = set()
            self.app.user.pairs = set()

            for symbol in rules:
                if 'type' in rules[symbol]:
                    if rules[symbol]['type'] != 'spot':
                        break
                base_asset = rules[symbol]['base'].lower()
                quote_asset = rules[symbol]['quote'].lower()
                pair = base_asset + '_' + quote_asset
                self.app.user.coins.add(base_asset)
                self.app.user.coins.add(quote_asset)
                self.app.user.pairs.add(pair)

                self.app.user.rules[pair] = {}
                self.app.user.rules[pair]['symbol'] = symbol
                if 'limits' in rules[symbol]:
                    if 'price' in rules[symbol]['limits']:
                        if 'min' in rules[symbol]['limits']['price']:
                            self.app.user.rules[pair]['minPrice'] = float(
                                rules[symbol]['limits']['price']['min']) if isinstance(
                                rules[symbol]['limits']['price']['min'], (int, float)) else 0.0
                        else:
                            self.app.user.rules[pair]['minPrice'] = 0.0
                        if 'max' in rules[symbol]['limits']['price']:
                            self.app.user.rules[pair]['maxPrice'] = float(
                                rules[symbol]['limits']['price']['max']) if isinstance(
                                rules[symbol]['limits']['price']['max'], (int, float)) else 0.0
                        else:
                            self.app.user.rules[pair]['maxPrice'] = 0.0
                    else:
                        self.app.user.rules[pair]['minPrice'] = 0.0
                        self.app.user.rules[pair]['maxPrice'] = 0.0
                    if 'amount' in rules[symbol]['limits']:
                        if 'min' in rules[symbol]['limits']['amount']:
                            self.app.user.rules[pair]['minQty'] = float(rules[symbol]['limits']['amount']['min']) if isinstance(
                                rules[symbol]['limits']['amount']['min'], (int, float)) else 0.0
                        else:
                            self.app.user.rules[pair]['minQty'] = 0.0
                        if 'max' in rules[symbol]['limits']['amount']:
                            self.app.user.rules[pair]['maxQty'] = float(rules[symbol]['limits']['amount']['max']) if isinstance(
                                rules[symbol]['limits']['amount']['max'], (int, float)) else 0.0
                        else:
                            self.app.user.rules[pair]['maxQty'] = 0.0
                    else:
                        self.app.user.rules[pair]['minQty'] = 0.0
                        self.app.user.rules[pair]['maxQty'] = 0.0
                    if 'cost' in rules[symbol]['limits']:
                        if 'min' in rules[symbol]['limits']['cost']:
                            self.app.user.rules[pair]['minSum'] = float(rules[symbol]['limits']['cost']['min']) if isinstance(
                                rules[symbol]['limits']['cost']['min'], (int, float)) else 0.0
                        else:
                            self.app.user.rules[pair]['minSum'] = 0.0
                        if 'max' in rules[symbol]['limits']['cost']:
                            self.app.user.rules[pair]['maxSum'] = float(rules[symbol]['limits']['cost']['max']) if isinstance(
                                rules[symbol]['limits']['cost']['max'], (int, float)) else 0.0
                        else:
                            self.app.user.rules[pair]['maxSum'] = 0.0
                    else:
                        self.app.user.rules[pair]['minSum'] = 0.0
                        self.app.user.rules[pair]['maxSum'] = 0.0
                else:
                    self.app.user.rules[pair]['minPrice'] = 0.0
                    self.app.user.rules[pair]['maxPrice'] = 0.0
                    self.app.user.rules[pair]['minQty'] = 0.0
                    self.app.user.rules[pair]['maxQty'] = 0.0
                    self.app.user.rules[pair]['minSum'] = 0.0
                    self.app.user.rules[pair]['maxSum'] = 0.0

                if 'precision' in rules[symbol]:
                    if 'price' in rules[symbol]['precision']:
                        self.app.user.rules[pair]['aroundPrice'] = int(rules[symbol]['precision']['price']) if isinstance(
                            rules[symbol]['precision']['price'], int) else int(
                            abs(log10(float(rules[symbol]['precision']['price']))))
                    else:
                        self.app.user.rules[pair]['aroundPrice'] = 8
                    if 'amount' in rules[symbol]['precision']:
                        self.app.user.rules[pair]['aroundQty'] = int(rules[symbol]['precision']['amount']) if isinstance(
                            rules[symbol]['precision']['amount'], int) else int(
                            abs(log10(float(rules[symbol]['precision']['amount']))))
                    else:
                        self.app.user.rules[pair]['aroundQty'] = 8
                else:
                    self.app.user.rules[pair]['aroundPrice'] = 8
                    self.app.user.rules[pair]['aroundQty'] = 8

            self.app.user.api_is_init = True
            self.app.kline.upd(delta=self.app.user.delta_time)
            self.app.gui.log('Bot ready for trading on ' + self.app.bot.exchange.capitalize())

    def control_trade(self, order_price, order_qty):
        """Проверка ордера правилам биржи.
        """
        counter = 0
        try:
            if self.app.user.rules[self.app.bot.pair]['minPrice'] > 0:
                if order_price >= self.app.user.rules[self.app.bot.pair]['minPrice']:
                    counter += 1
                else:
                    self.app.gui.log('Price less than min price: ' + str(
                        self.app.user.rules[self.app.bot.pair]['minPrice']) + ' ' + self.app.user.curr_quote.upper())
                    raise Exception('My price: ' + self.app.gui.fp(order_price) + ' < Minimal price: ' + self.app.gui.fp(self.app.user.botst.rules[self.app.bot.pair]['minPrice']))
            else:
                counter += 1

            if self.app.user.rules[self.app.bot.pair]['minQty'] > 0:
                if order_qty >= self.app.user.rules[self.app.bot.pair]['minQty']:
                    counter += 1
                else:
                    self.app.gui.log('Qty less than min qty: ' + str(
                        self.app.user.rules[self.app.bot.pair]['minQty']) + ' ' + self.app.user.curr_base.upper())
                    raise Exception('My amount: ' + self.app.gui.fq(order_qty) + ' < Minimal amount: ' + self.app.gui.fq(self.app.user.rules[self.app.bot.pair]['minQty']))
            else:
                counter += 1

            if self.app.user.rules[self.app.bot.pair]['minSum'] > 0:
                if order_qty * order_price >= self.app.user.rules[self.app.bot.pair]['minSum']:
                    counter += 1
                else:
                    self.app.gui.log('Sum less than min sum: ' + str(
                        self.app.user.rules[self.app.bot.pair]['minSum']) + ' ' + self.app.user.curr_quote.upper())
                    raise Exception('My sum: ' + self.app.gui.fp(order_qty * order_price) + ' < Minimal sum: ' + self.app.gui.fp(self.app.user.rules[self.app.bot.pair]['minSum']))
            else:
                counter += 1

            if self.app.user.rules[self.app.bot.pair]['maxPrice'] > 0:
                if order_price < self.app.user.rules[self.app.bot.pair]['maxPrice']:
                    counter += 1
                else:
                    self.app.gui.log('Price more than max price: ' + str(
                        self.app.user.rules[self.app.bot.pair]['maxPrice']) + ' ' + self.app.user.curr_quote.upper())
                    raise Exception('My price: ' + self.app.gui.fp(order_price) + ' > Maximal price: ' + self.app.gui.fp(self.app.user.rules[self.app.bot.pair]['maxPrice']))
            else:
                counter += 1

            if self.app.user.rules[self.app.bot.pair]['maxQty'] > 0:
                if order_qty < self.app.user.rules[self.app.bot.pair]['maxQty']:
                    counter += 1
                else:
                    self.app.gui.log('Qty more than max qty: ' + str(
                        self.app.user.rules[self.app.bot.pair]['maxQty']) + ' ' + self.app.user.curr_base.upper())
                    raise Exception('My amount: ' + self.app.gui.fq(order_qty) + ' > Maximal amount: ' + self.app.gui.fq(self.app.user.rules[self.app.bot.pair]['maxQty']))
            else:
                counter += 1

            if self.app.user.rules[self.app.bot.pair]['maxSum'] > 0:
                if order_qty * order_price < self.app.user.rules[self.app.bot.pair]['maxSum']:
                    counter += 1
                else:
                    self.app.gui.log('Sum more than max sum: ' + str(
                        self.app.user.rules[self.app.bot.pair]['maxSum']) + ' ' + self.app.user.curr_quote.upper())
                    raise Exception('My sum: ' + self.app.gui.fp(order_qty * order_price) + ' > Maximal sum: ' + self.app.gui.fp(self.app.user.rules[self.app.bot.pair]['maxSum']))
            else:
                counter += 1
        except Exception as e:
            self.app.errors.error(141, e)
            counter = 0
        if counter == 6:
            return True
        else:
            return False

    def send_order(self, side, order_price, order_qty):
        """Отправка ордера.
        """
        if self.app.user.bot_is_init and self.app.user.api_is_init and self.app.bot.api_key != '' and self.app.bot.api_secret != '':
            order = dict()
            try:

                if side.lower() == 'buy':
                    order = self.app.api.create_limit_buy_order(self.app.user.rules[self.app.bot.pair]['symbol'], order_qty, order_price)
                elif side.lower() == 'sell':
                    order = self.app.api.create_limit_sell_order(self.app.user.rules[self.app.bot.pair]['symbol'], order_qty, order_price)

            except Exception as e:
                self.app.errors.error(140, e)
                order = dict()
            if order:

                data = dict()

                data['pair'] = self.app.bot.pair
                data['price'] = order_price
                data['qty'] = order_qty
                data['side'] = side
                data['desc'] = side.upper() + ' ' + str(
                    self.app.gui.fq(order_qty)) + ' ' + self.app.user.curr_base.upper() + ' × ' + str(
                    self.app.gui.fp(order_price)) + ' ' + self.app.user.curr_quote.upper()

                self.app.gui.log(data['desc'])

                self.app.user.orders.append(
                    {'id': order['id'], 'pair': self.app.bot.pair, 'side': side, 'qty': order_qty, 'fill': 0.0,
                     'price': order_price,
                     'time': time()})

                if self.app.gui.win_orders.winfo_exists():
                    self.app.gui.win_orders.view_orders()

    def hand_buy(self):
        """Ручная отправка ордера покупки.
        """
        order_price = float(self.app.gui.win_terminal.entry_buy_price.get())
        order_qty = float(self.app.gui.win_terminal.entry_buy_qty.get())
        if self.control_trade(order_price, order_qty):
            self.send_order('buy', order_price, order_qty)

    def hand_sell(self):
        """Ручная отправка ордера продажи.
        """
        order_price = float(self.app.gui.win_terminal.entry_sell_price.get())
        order_qty = float(self.app.gui.win_terminal.entry_sell_qty.get())
        if self.control_trade(order_price, order_qty):
            self.send_order('sell', order_price, order_qty)
