import json
import tkinter as tk
import webbrowser
from base64 import b64encode, b64decode
from math import log10
from threading import Thread
from time import strftime, localtime, time, sleep
from tkinter import ttk
from random import randrange


class Gui:

    def __init__(self, app):
        """
        Класс вывода на экран
        """
        self.app = app
        self.tk = tk
        self.root = tk.Tk()
        self.win_main = MainWindow(False, self.root, self.app)

    @staticmethod
    def rand_xy():
        """Получение рандомных координат, чтобы окно каждый раз открывалось в новом месте."""
        return '+' + str(randrange(10, 320)) + '+' + str(randrange(10, 200))

    def fp(self, price):
        """Форматирование цены перед отправкой на биржу."""
        around_price = self.app.user.rules[self.app.bot.pair]['aroundPrice']
        format_price = '{:.' + str(around_price) + 'f}'
        return str(format_price.format(price))

    def fq(self, qty):
        """Форматирование объема перед отправкой на биржу."""
        around_qty = self.app.user.rules[self.app.bot.pair]['aroundQty']
        format_qty = '{:.' + str(around_qty) + 'f}'
        return str(format_qty.format(qty))

    @staticmethod
    def _on_key_release(event):
        """Захват кнопок ctrl + a[x/c/v]."""
        ctrl = (event.state & 0x4) != 0
        if event.keycode == 88 and ctrl and event.keysym.lower() != "x":
            event.widget.event_generate("<<Cut>>")

        if event.keycode == 86 and ctrl and event.keysym.lower() != "v":
            event.widget.event_generate("<<Paste>>")

        if event.keycode == 67 and ctrl and event.keysym.lower() != "c":
            event.widget.event_generate("<<Copy>>")

        if event.keycode == 65 and ctrl and event.keysym.lower() != "a":
            event.widget.event_generate("<<SelectAll>>")

    def run(self):
        """Запуск графики"""
        main_icon = "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"
        self.root.title(self.app.user.name + ' ' + self.app.user.ver)
        self.root.tk.call('wm', 'iconphoto', self.root._w, "-default", tk.PhotoImage(data=main_icon))
        self.root.bind_all("<Key>", self._on_key_release, "+")
        self.root.geometry('400x160' + self.rand_xy())
        self.root.resizable(False, False)

        self.win_main = MainWindow(True, self.root, self.app)

        self.root.mainloop()

    def log(self, s):
        self.win_main.log(s)


class MainWindow(tk.Frame):

    def __init__(self, apply, root, app):
        """Основное окно"""
        super().__init__(root)
        self.root = root
        self.app = app

        self.icon_book = tk.PhotoImage(data='R0lGODlhGwAeALMAAAF1yzyZ2U1qf3eOnhyN1FOn3oacqpCksaCxvCiX2E+q31+x4na85mF+j2qGlv///ywAAAAAGwAeAAAEbvDJSau9OOvNu/9g6CVkWUpOqqoX4L6vJMw0fTF4nktI7/uioJBiKqJWqwthyWRKGtBo9KbT8X6/oVak6Hq9EoN4PL4Ezmi0ZMBut6lV3BXb29o9i7xeLzn4/38XBYOEhGFkZHBxc3R3jo+QkZERADs=')
        self.icon_chart = tk.PhotoImage(data='R0lGODlhGQAeALMAAAV3zE1qf73J0Ueh26CxvGy45GqGlrDZ8dng5P///wAAAAAAAAAAAAAAAAAAAAAAACwAAAAAGQAeAAAEZDDJSau9OOvNu/9giCRjSZ6mGa7c0U7C5W5zElcFMNASERg4ncWU2/mARGGmmDgGd0uh08m0zJjTn6RWuSpvzgR3wqyCtdEd0+RUUarjJhoDv9zSW/uLRYmLUIApgHyEhYaHIREAOw==')
        self.icon_clock = tk.PhotoImage(data='R0lGODlhGQAeALMAAAB7zpeptMnR1jSc2nS856fV8Imcp7bCyeHn6qKzu////wAAAAAAAAAAAAAAAAAAACwAAAAAGQAeAAAEk1DJSau9OOvNu/+ecIyk8AlBqq7mhhqBgBQF8sbaKyMIAPA2WMuiA/Z+QIHwcogZj0/UgRgwPKHPJSXhfPquqESFe8U+A2JKquwjXFMVWJngG9SA1XigPBsABkZ5FAYGO1cFBHdBBhUHcnxnBlN6hpAvTEKQNlWTFo5dYJwan6CbohuOhKqrnRwjKyMgsrO0tba3EQA7')
        self.icon_code = tk.PhotoImage(data='R0lGODlhFgAeAKIAAE1qf+Dm6qCxvCiX2Ha85mqGlrLX7f///ywAAAAAFgAeAAADfHi63P4wykmrvVeUzbsXTUGMZGkWIWGY7Igy4tqe4WDfeP4uReD/wOBO0Qsaf8NDMVAA/AQBwDJZFDiRPgCUGfJZn0Wtj+q9MrdiLoyZjj6lal7Zu0yTA9/zz97FX5dRW3dseHtTfUdGSWaJQAANVgCSk5SUIBiYmZqbnAkAOw==')
        self.icon_orders = tk.PhotoImage(data='R0lGODlhGQAeAKIAAAF1y01qf6CxvCiX2Ha85mqGlv///wAAACwAAAAAGQAeAAADUGi63P4wykmrvTgXUdT4YCg2QiAoQKqurNMpRCzPdGbfymuIfEiaKJZQ1di8aMgZbnnR9Z6/k2FILXJgySRzKzF6nrxokNoqLrJarnrNbi8TADs=')
        self.icon_settings = tk.PhotoImage(data='R0lGODlhGQAeALMAAPX2+PL09vj5+unt8FJxh8rT2dfe4+7x83W65GaXtmqGlqGyvLvIz+Dm6fv8/P///ywAAAAAGQAeAAAEqfDJSau9OOvNu6/CoiiL81HiSJ5TOi6spKrN5iz4UihE7yuMQe5QcfF6CQQi8VPBKDNeUkllRiszwpRaJcwqjFFPyfRNey/LTqv0Fh48sjezIFAJgIm9/bzU7wMSAHsIBH0UDgFSbQQHa3JAAhUGYntlSIxpUCpsXF1fm5xbn6AtWZhLTZoTDgkjAAU+skBhCgkBGwdRCg+SJ0aHH8AxEikLgcTJysvMExEAOw==')
        self.icon_terminal = tk.PhotoImage(data='R0lGODlhGQAeALMAAAF1y+Hm6k1qf3S75p+wu9vt+CiX2HzA55zQ7WqGlsXQ1ur1+/T6/fH09fz9/f///ywAAAAAGQAeAAAEefDJSau9OOvNu/9gKG7OSDlDeRFJsiEGgrFuxhg4s7YajMsTWmtIsCxwyMUkMGwGLAck7kARtoqVghRZmDSaiYZlsMUNKIqhQkM2XBxDFaaNSa/ZuMzdxAeVkRJgTRUAhYaGEgKKi4sVA4+QkBIElJWVfZiZmpucFREAOw==')
        self.icon_trades = tk.PhotoImage(data='R0lGODlhGQAeAKIAAAF1y01qf6CxvCiX2Ha85mqGlv///wAAACwAAAAAGQAeAAADUGi63P4wykmrvTiDrYr/YNgQAKEEaKquzrAIcCzPWW0bG9CF/DeWp5Uw1XrNjrGb0pLb9Xg/k2FILSqQ2KVW0jQ8e9EgldVwXbHHrXrNbi8TADs=')
        self.icon_info = tk.PhotoImage(data='R0lGODlhGwAeAKIAAAB7zlOn3oacqqCxvGqGluHn6v///////yH/C05FVFNDQVBFMi4wAwEAAAAh+QQFAAAHACwAAAAAGwAeAAADeWi63P4wykmrvVgOwvvIXShanDAUaDoIHFWmcMoS0gsHQTxHhBAXuB8LsjnFAIBf8cH5OVMtR/PpjDamseDPysDeclualODUxrgLb8oMQyuKPzZqyfRlwbAhxJZC6txdPVQFOxMlRjArgEwijRkbIh8Zk5SVlpeYCgkAOw==')
        self.icon_play = tk.PhotoImage(data='R0lGODlhCwALAJEAACiX2Ha85v///wAAACH/C05FVFNDQVBFMi4wAwEAAAAh+QQEAAAAACwAAAAACwALAAACE5SPqQh7AIKDUCZKL7UsTgeGRgEAOw==')
        self.icon_stop = tk.PhotoImage(data='R0lGODlhCwALAIAAAKCxvP///yH/C05FVFNDQVBFMi4wAwEAAAAh+QQEAAAAACwAAAAACwALAAACEYyPqQftgJ6LErJKZX57rv8VADs=')

        if apply:
            self.init_window()
        else:
            self.destroy()

    def init_window(self):
        self.tool_bar = tk.Frame(bg='#ffffff', bd=0, width=400, height=160)
        self.tool_bar.pack(side=tk.TOP, fill=tk.BOTH)
        y = 10
        tk.Label(self.tool_bar, bg='#ffffff', text='Share').place(x=10, y=y)
        self.entry_share = ttk.Entry(self.tool_bar)
        self.entry_share.place(x=80, y=y, width=120, height=25)

        ttk.Button(self.tool_bar, text='Init', command=self.access).place(x=220, y=y, width=120, height=25)
        y = 30
        tk.Label(self.tool_bar, bg='#ffffff', text='').place(x=10, y=y)

        y = 40
        self.failed_activation = tk.Label(self.tool_bar, bg='#ffffff', text='', fg='#dd3333', font='Arial 10')
        self.failed_activation.place(x=80, y=y)

        try:
            self.entry_share.insert(0, self.app.db.load_key())
        except:
            pass

    def access(self):
        self.app.user.shared_key = self.entry_share.get()
        """Упрощен блок проверки пользователя.
        """
        if self.app.user.activation.check():
            self.init_main_window()
            self.app.common.launch()
            self.app.db.save_key(self.app.user.shared_key)
        else:
            self.failed_activation.config(text='Activation failed')

    def log(self, s):
        """Вывод логов в основное окно"""
        t = strftime("%m/%d %H:%M", localtime(time()))
        self.logs_box.configure(state='normal')
        self.logs_box.insert(tk.END, t + ' ' + s + '\n')
        self.logs_box.configure(state='disabled')

        self.logs_box.yview_moveto(1)

    def reset_log(self):
        """Очистка окна логов"""
        self.logs_box.configure(state='normal')
        self.logs_box.delete(1.0, tk.END)
        self.logs_box.configure(state='disabled')
        return 0

    @staticmethod
    def progress(progress_bar):
        """Смена иконки при работе программы с серого на синий для разных подпроцессов"""
        if progress_bar.cget('fg') == '#3399dd':
            progress_bar.configure(fg='#dddddd')
        else:
            progress_bar.configure(fg='#3399dd')

    def init_main_window(self):
        self.tool_bar.forget()

        menu_bar = tk.Frame(bg='#ffffff', bd=0, width=400, height=30)
        menu_bar.pack(side=tk.TOP, fill=tk.BOTH)

        tool_bar = tk.Frame(bg='#ffffff', bd=0, width=400, height=20)
        tool_bar.pack(side=tk.TOP, fill=tk.BOTH)

        log_bar = tk.Frame(bg='#ffffff', bd=0, width=400, height=70)
        log_bar.pack(side=tk.TOP, fill=tk.BOTH)

        button_bar = tk.Frame(bg='#ffffff', bd=0, width=400, height=60)
        button_bar.pack(side=tk.TOP, fill=tk.BOTH)

        # menu bar
        tk.Button(menu_bar, command=self.__check_for_depth_window, bg='#ffffff', bd=0, compound=tk.TOP, image=self.icon_book).pack(side=tk.LEFT)
        tk.Button(menu_bar, command=self.__check_for_orders_window, bg='#ffffff', bd=0, compound=tk.TOP, image=self.icon_orders).pack(side=tk.LEFT)
        tk.Button(menu_bar, command=self.__check_for_trades_window, bg='#ffffff', bd=0, compound=tk.TOP, image=self.icon_trades).pack(side=tk.LEFT)
        tk.Button(menu_bar, command=self.__check_for_terminal_window, bg='#ffffff', bd=0, compound=tk.TOP, image=self.icon_terminal).pack(side=tk.LEFT)
        tk.Button(menu_bar, command=self.__check_for_chart_window, bg='#ffffff', bd=0, compound=tk.TOP, image=self.icon_chart).pack(side=tk.LEFT)
        tk.Button(menu_bar, command=self.__check_for_clocks_window, bg='#ffffff', bd=0, compound=tk.TOP, image=self.icon_clock).pack(side=tk.LEFT)

        tk.Button(menu_bar, command=self.__check_for_settings_window, bg='#ffffff', bd=0, compound=tk.TOP, image=self.icon_settings).pack(side=tk.LEFT)
        if self.app.debug:
            tk.Button(menu_bar, command=self.__check_for_debug_window, bg='#ffffff', bd=0, compound=tk.TOP, image=self.icon_code).pack(side=tk.LEFT)
        tk.Button(menu_bar, command=self.__check_for_info_window, bg='#ffffff', bd=0, compound=tk.TOP, image=self.icon_info).pack(side=tk.LEFT)

        # toolbar
        self.progress_depth = tk.Label(tool_bar, bg='#ffffff', text='D', fg='#3399dd', font='Arial 6')  # □■
        self.progress_depth.place(x=370, y=0)

        self.progress_price = tk.Label(tool_bar, bg='#ffffff', text='P', fg='#3399dd', font='Arial 6')  # □■
        self.progress_price.place(x=360, y=0)

        self.progress_orders = tk.Label(tool_bar, bg='#ffffff', text='O', fg='#3399dd', font='Arial 6')  # □■
        self.progress_orders.place(x=350, y=0)

        self.progress_trades = tk.Label(tool_bar, bg='#ffffff', text='T', fg='#3399dd', font='Arial 6')  # □■
        self.progress_trades.place(x=340, y=0)

        self.progress_balances = tk.Label(tool_bar, bg='#ffffff', text='B', fg='#3399dd', font='Arial 6')  # □■
        self.progress_balances.place(x=330, y=0)

        self.progress_main = tk.Label(tool_bar, bg='#ffffff', text='M', fg='#dddddd', font='Arial 6')  # □■
        self.progress_main.place(x=320, y=0)

        self.indicator_run = tk.Label(tool_bar, image=self.icon_stop, bd=0)
        self.indicator_run.place(x=308, y=2)

        tk.Label(tool_bar, bg='#ffffff', text='LOGS:', font='Arial 10 bold').place(x=10, y=0)

        # log bar
        self.logs_box = tk.Text(log_bar, font='Arial 10', wrap=tk.WORD, state='disabled')
        logs_scrollbar = ttk.Scrollbar(log_bar, orient='vertical', command=self.logs_box.yview, )

        self.logs_box.config(yscrollcommand=logs_scrollbar.set)

        logs_scrollbar.place(x=380, y=0, width=15, height=70)
        self.logs_box.place(x=5, y=0, width=375, height=70)

        # button bar
        ttk.Button(button_bar, text='Clear Logs', command=self.reset_log).place(x=10, y=5, width=120, height=23)

        self.progress(self.progress_main)

    def __check_for_depth_window(self):
        try:
            self.app.gui.win_depth.focus()
        except:
            self.app.gui.win_depth = DepthWindow(True, self.root, self.app)

    def __check_for_orders_window(self):
        try:
            self.app.gui.win_orders.focus()
        except:
            self.app.gui.win_orders = OrdersWindow(True, self.root, self.app)

    def __check_for_trades_window(self):
        try:
            self.app.gui.win_trades.focus()
        except:
            self.app.gui.win_trades = TradesWindow(True, self.root, self.app)

    def __check_for_clocks_window(self):
        try:
            self.app.gui.win_clocks.focus()
        except:
            self.app.gui.win_clocks = ClocksWindow(True, self.root, self.app)

    def __check_for_terminal_window(self):
        try:
            self.app.gui.win_terminal.focus()
        except:
            self.app.gui.win_terminal = TerminalWindow(True, self.root, self.app)

    def __check_for_settings_window(self):
        try:
            self.app.gui.win_settings.focus()
        except:
            self.app.gui.win_settings = SettingsWindow(True, self.root, self.app)
        if self.app.user.bot_is_init:
            self.app.gui.win_settings.view_settings()

    def __check_for_chart_window(self):
        try:
            self.app.gui.win_chart.focus()
        except:
            self.app.gui.win_chart = ChartWindow(True, self.root, self.app)

    def __check_for_info_window(self):
        try:
            self.app.gui.win_info.focus()
        except:
            self.app.gui.win_info = InfoWindow(True, self.root, self.app)

    def __check_for_debug_window(self):
        try:
            self.app.gui.win_debug.focus()
        except:
            self.app.gui.win_debug = DebugWindow(True, self.root, self.app)


class DepthWindow(tk.Toplevel):

    def __init__(self, apply, root, app):
        super().__init__(root)
        self.app = app
        if apply:
            self.init_window()
        else:
            self.destroy()

    def init_window(self):
        self.title('Openbook window')
        self.geometry('300x165'+self.app.gui.rand_xy())
        self.resizable(False, False)

        tool_bar = tk.Frame(self, bg='#ffffff', bd=0, width=300, height=35)
        tool_bar.pack(side=tk.TOP, fill=tk.X)

        tk.Label(tool_bar, text='Bid', bg='#ffffff', font='Arial 10 bold').place(x=10, y=10)
        tk.Label(tool_bar, text='Ask', bg='#ffffff', font='Arial 10 bold').place(x=160, y=10)

        self.tree = ttk.Treeview(self)
        self.tree['columns'] = ('bid_price', 'bid_qty', 'bid_sum', 'ask_price', 'ask_qty', 'ask_sum',)
        self.tree.column('#0', width=0, minwidth=0, stretch=tk.NO)
        self.tree.column('bid_price', width=50, minwidth=50, stretch=tk.NO)
        self.tree.column('bid_qty', width=50, minwidth=50, stretch=tk.NO)
        self.tree.column('bid_sum', width=50, minwidth=50, stretch=tk.NO)
        self.tree.column('ask_price', width=50, minwidth=50, stretch=tk.NO)
        self.tree.column('ask_qty', width=50, minwidth=50, stretch=tk.NO)
        self.tree.column('ask_sum', width=50, minwidth=50, stretch=tk.NO)

        self.tree.heading('bid_price', text='Price', anchor=tk.W)
        self.tree.heading('bid_qty', text='Qty', anchor=tk.W)
        self.tree.heading('bid_sum', text='Sum', anchor=tk.W)
        self.tree.heading('ask_price', text='Price', anchor=tk.W)
        self.tree.heading('ask_qty', text='Qty', anchor=tk.W)
        self.tree.heading('ask_sum', text='Sum', anchor=tk.W)

        for i in range(5):
            if len(self.app.user.depth['bids']) > i and len(self.app.user.depth['asks']) > i:
                self.tree.insert('', 'end', 'depth_'+str(i), values=(
                    0.0 if not self.app.user.depth['bids'][i][0] else self.app.gui.fp(self.app.user.depth['bids'][i][0]),
                    0.0 if not self.app.user.depth['bids'][i][1] else self.app.gui.fq(self.app.user.depth['bids'][i][1]),
                    0.0 if not self.app.user.depth['bids'][i][0] else self.app.gui.fp(self.app.user.depth['bids'][i][0] * self.app.user.depth['bids'][i][1]),
                    0.0 if not self.app.user.depth['asks'][i][0] else self.app.gui.fp(self.app.user.depth['asks'][i][0]),
                    0.0 if not self.app.user.depth['asks'][i][1] else self.app.gui.fq(self.app.user.depth['asks'][i][1]),
                    0.0 if not self.app.user.depth['asks'][i][0] else self.app.gui.fp(self.app.user.depth['asks'][i][0] * self.app.user.depth['asks'][i][1]),
                ))
            else:
                self.tree.insert('', 'end', 'depth_' + str(i), values=(0.0, 0.0, 0.0, 0.0, 0.0, 0.0))

        self.tree.pack(fill=tk.X)

    def view_depth(self):

        if self.app.user.depth != dict():
            bids_num = len(self.app.user.depth['bids'])
            asks_num = len(self.app.user.depth['asks'])

            if bids_num > 5:
                bids_num = 5
            if asks_num > 5:
                asks_num = 5
            try:
                for i in range(asks_num):
                    self.tree.set(item='depth_' + str(i), column='ask_price', value=self.app.gui.fp(self.app.user.depth['asks'][i][0]))
                    self.tree.set(item='depth_' + str(i), column='ask_qty', value=self.app.gui.fq(self.app.user.depth['asks'][i][1]))
                    self.tree.set(item='depth_' + str(i), column='ask_sum', value=self.app.gui.fp(self.app.user.depth['asks'][i][0] * self.app.user.depth['asks'][i][1]))

                for i in range(bids_num):
                    self.tree.set(item='depth_' + str(i), column='bid_price', value=self.app.gui.fp(self.app.user.depth['bids'][i][0]))
                    self.tree.set(item='depth_' + str(i), column='bid_qty', value=self.app.gui.fq(self.app.user.depth['bids'][i][1]))
                    self.tree.set(item='depth_' + str(i), column='bid_sum', value=self.app.gui.fp(self.app.user.depth['bids'][i][0] * self.app.user.depth['bids'][i][1]))
            except Exception as e:
                self.app.errors.error(129, e)


class OrdersWindow(tk.Toplevel):

    def __init__(self, apply, root, app):
        super().__init__(root)
        self.app = app
        self.tree = None
        if apply:
            self.init_window()
        else:
            self.destroy()

    def init_window(self):
        self.title('Orders window')
        self.geometry('300x260' + self.app.gui.rand_xy())
        self.resizable(False, False)

        tool_bar = tk.Frame(self, bg='#ffffff', bd=0, width=300, height=33)
        tool_bar.pack(side=tk.TOP, fill=tk.X)

        tk.Label(tool_bar, text='Orders', bg='#ffffff', font='Arial 10 bold').place(x=10, y=10)

        treebar = tk.Frame(self, bg='#ffffff', bd=0, width=300, height=260)
        treebar.pack(side=tk.LEFT, fill=tk.BOTH)

        self.tree = ttk.Treeview(treebar)

        ttk.Button(tool_bar, text='Cancel', command=self.init_cancel).place(x=220, y=10, width=70, height=23)

        self.tree['columns'] = ('side', 'price', 'filled', 'amount', 'sum')
        self.tree.column('#0', width=0, minwidth=0, stretch=tk.NO)
        self.tree.column('side', width=60, minwidth=50)
        self.tree.column('price', width=60, minwidth=50, stretch=tk.NO)
        self.tree.column('filled', width=60, minwidth=50, stretch=tk.NO)
        self.tree.column('amount', width=60, minwidth=50, stretch=tk.NO)
        self.tree.column('sum', width=60, minwidth=50, stretch=tk.NO)

        self.tree.heading('side', text='Side', anchor=tk.W)
        self.tree.heading('price', text='Price', anchor=tk.W)
        self.tree.heading('filled', text='Filled', anchor=tk.W)
        self.tree.heading('amount', text='Amount', anchor=tk.W)
        self.tree.heading('sum', text='Sum', anchor=tk.W)

        for i in range(len(self.app.user.orders)):
            self.tree.insert('', 'end', self.app.user.orders[i]['id'], text=self.app.user.orders[i]['id'],
                             values=(self.app.user.orders[i]['side'],
                                     self.app.gui.fp(self.app.user.orders[i]['price']),
                                     self.app.gui.fq((lambda x: 0.0 if x is None else x)(self.app.user.orders[i]['filled'])),
                                     self.app.gui.fq((lambda x: 0.0 if x is None else x)(self.app.user.orders[i]['filled']) + (
                                         lambda x: 0.0 if x is None else x)(self.app.user.orders[i]['remaining'])),
                                     round(self.app.user.orders[i]['price'] * (lambda x: 0.0 if x is None else x)(
                                         self.app.user.orders[i]['amount']), 8)))
        self.tree.pack(fill=tk.BOTH)

    def init_cancel(self):
        res = self.app.common.cancel_order(order_id=self.tree.item(self.tree.focus())['text'])

    def view_orders(self):
        self.tree.delete(*self.tree.get_children())

        # for i in app_o.tree.get_children():
        #     app_o.tree.delete(i)
        try:
            for i in range(len(self.app.user.orders)):
                self.tree.insert('', 'end', self.app.user.orders[i]['id'], text=self.app.user.orders[i]['id'],
                              values=(self.app.user.orders[i]['side'],
                                      self.app.gui.fp(self.app.user.orders[i]['price']),
                                      self.app.gui.fq((lambda x: 0.0 if x is None else x)(self.app.user.orders[i]['filled'])),
                                      self.app.gui.fq((lambda x: 0.0 if x is None else x)(self.app.user.orders[i]['filled']) + (lambda x: 0.0 if x is None else x)(self.app.user.orders[i]['remaining'])),
                                      self.app.gui.fp(self.app.user.orders[i]['price'] * (lambda x: 0.0 if x is None else x)(self.app.user.orders[i]['amount']))))
        except Exception as e:
            self.app.errors.error(133, e)


class TradesWindow(tk.Toplevel):

    def __init__(self, apply, root, app):
        super().__init__(root)
        self.app = app
        self.tree = None
        if apply:
            self.init_window()
        else:
            self.destroy()

    def init_window(self):
        self.title('Trades window')
        self.geometry('300x260'+self.app.gui.rand_xy())
        self.resizable(False, False)

        tool_bar = tk.Frame(self, bg='#ffffff', bd=0, width=300, height=33)
        tool_bar.pack(side=tk.TOP, fill=tk.X)

        tk.Label(tool_bar, text='Trades', bg='#ffffff', font='Arial 10 bold').place(x=10, y=10)

        treebar = tk.Frame(self, bg='#ffffff', bd=0, width=300, height=260)
        treebar.pack(side=tk.LEFT, fill=tk.BOTH)

        self.tree = ttk.Treeview(treebar)

        self.tree['columns'] = ('time', 'side', 'price', 'amount', 'sum')
        self.tree.column('#0', width=0, minwidth=0, stretch=tk.NO)
        self.tree.column('time', width=68, minwidth=50, stretch=tk.NO)
        self.tree.column('side', width=40, minwidth=40, stretch=tk.NO)
        self.tree.column('price', width=64, minwidth=50, stretch=tk.NO)
        self.tree.column('amount', width=64, minwidth=50, stretch=tk.NO)
        self.tree.column('sum', width=64, minwidth=50, stretch=tk.NO)

        self.tree.heading('time', text='Time', anchor=tk.W)
        self.tree.heading('side', text='Side', anchor=tk.W)
        self.tree.heading('price', text='Price', anchor=tk.W)
        self.tree.heading('amount', text='Amount', anchor=tk.W)
        self.tree.heading('sum', text='Sum', anchor=tk.W)

        for i in range(len(self.app.user.trades)):
            self.tree.insert('', 'end', 'trades_' + str(i),
                             values=(strftime('%m/%d %H:%M', localtime(self.app.user.trades[i]['timestamp']/1000)),
                                     self.app.user.trades[i]['side'],
                                     self.app.gui.fp(self.app.user.trades[i]['price']),
                                     self.app.gui.fq((lambda x: 0.0 if x is None else x)(self.app.user.trades[i]['amount'])),
                                     self.app.gui.fp((lambda x: 0.0 if x is None else x)(self.app.user.trades[i]['cost']))))
        self.tree.pack(fill=tk.BOTH)

    def view_trades(self):
        self.tree.delete(*self.tree.get_children())

        # for i in app_t.tree.get_children():
        #     app_t.tree.delete(i)

        try:
            for i in range(len(self.app.user.trades)):
                self.tree.insert('', 'end', 'trades_' + str(i),
                                  values=(strftime('%m/%d %H:%M', localtime(self.app.user.trades[i]['timestamp'] / 1000)),
                                          self.app.user.trades[i]['side'],
                                          self.app.gui.fp(self.app.user.trades[i]['price']),
                                          self.app.gui.fq((lambda x: 0.0 if x is None else x)(self.app.user.trades[i]['amount'])),
                                          self.app.gui.fp((lambda x: 0.0 if x is None else x)(self.app.user.trades[i]['cost'])))
                                  )
        except Exception as e:
            self.app.errors.error(136, e)


class ClocksWindow(tk.Toplevel):

    def __init__(self, apply, root, app):
        super().__init__(root)
        self.app = app
        self.day = self.hms = None
        if apply:
            self.init_window()
        else:
            self.destroy()

        Thread(target=self.update_time, daemon=True).start()

    def init_window(self):
        self.title('Clock')
        self.geometry('192x108'+self.app.gui.rand_xy())
        self.resizable(False, False)

        outer_frame = tk.Frame(self, bd=0, bg='#ffffff', width=192, height=108)
        outer_frame.pack(side=tk.LEFT, expand=tk.YES, fill=tk.BOTH)

        bar = outer_frame

        self.day = tk.Label(bar, bg='#ffffff', text='01/01/01', font='Arial 24 bold')
        self.day.place(x=12, y=16)
        self.hms = tk.Label(bar, bg='#ffffff', text='00:00:00', font='Arial 24 bold')
        self.hms.place(x=12, y=52)

    def update_time(self):
        while True:
            try:
                if self.winfo_exists():
                    self.day.configure(text=strftime("%Y/%m/%d"))
                    self.hms.configure(text=strftime("%H:%M:%S.") + str(time()).split('.')[1][0:2])
                sleep(0.05)
            except Exception as e:
                self.app.errors.error(151, e)


class TerminalWindow(tk.Toplevel):

    def __init__(self, apply, root, app):
        super().__init__(root)
        self.app = app
        if apply:
            self.init_window()
        else:
            self.destroy()

    def init_window(self):
        self.title('Terminal')
        self.geometry('300x200'+self.app.gui.rand_xy())
        self.resizable(False, False)

        tool_bar = tk.Frame(self, bd=0, bg='#ffffff', width=300, height=200)
        tool_bar.pack(side=tk.LEFT, expand=tk.YES, fill=tk.BOTH)

        y = 10
        tk.Label(tool_bar, bg='#ffffff', text='FUNDS:', font='Arial 10 bold').place(x=10, y=y)

        y += 25
        self.quote_asset = tk.Label(tool_bar, bg='#ffffff', text='Quote')
        self.quote_asset.place(x=10, y=y)
        self.base_asset = tk.Label(tool_bar, bg='#ffffff', text='Base')
        self.base_asset.place(x=150, y=y)
        self.entry_quote = ttk.Entry(tool_bar)
        self.entry_quote.place(x=60, y=y, width=80)
        self.entry_base = ttk.Entry(tool_bar)
        self.entry_base.place(x=200, y=y, width=80)

        y += 25
        tk.Label(tool_bar, bg='#ffffff', text='BUY').place(x=10, y=y)
        tk.Label(tool_bar, bg='#ffffff', text='SELL').place(x=150, y=y)

        y += 25
        self.label_buy_price = tk.Label(tool_bar, bg='#ffffff', text='Price')
        self.label_buy_price.place(x=10, y=y)
        self.label_sell_price = tk.Label(tool_bar, bg='#ffffff', text='Price')
        self.label_sell_price.place(x=150, y=y)
        self.entry_buy_price = ttk.Entry(tool_bar)
        self.entry_buy_price.insert(0, '0')
        self.entry_buy_price.place(x=60, y=y, width=80)
        self.entry_sell_price = ttk.Entry(tool_bar)
        self.entry_sell_price.insert(0, '0')
        self.entry_sell_price.place(x=200, y=y, width=80)

        y += 25
        self.label_buy_qty = tk.Label(tool_bar, bg='#ffffff', text='Qty')
        self.label_buy_qty.place(x=10, y=y)
        self.label_sell_qty = tk.Label(tool_bar, bg='#ffffff', text='Qty')
        self.label_sell_qty.place(x=150, y=y)
        self.entry_buy_qty = ttk.Entry(tool_bar)
        self.entry_buy_qty.insert(0, '0')
        self.entry_buy_qty.place(x=60, y=y, width=80)
        self.entry_sell_qty = ttk.Entry(tool_bar)
        self.entry_sell_qty.insert(0, '0')
        self.entry_sell_qty.place(x=200, y=y, width=80)

        y += 25
        s = ttk.Style()
        s.configure('Horizontal.TScale', background='#ffffff')
        self.buy_scale_qty = tk.IntVar()
        self.sell_scale_qty = tk.IntVar()
        self.label_scale_buy = tk.Label(tool_bar, bg='#ffffff', text=0, textvariable=self.buy_scale_qty)
        self.label_scale_buy.place(x=10, y=y)
        self.label_scale_sell = tk.Label(tool_bar, bg='#ffffff', text=0, textvariable=self.sell_scale_qty)
        self.label_scale_sell.place(x=150, y=y)
        scale_buy = ttk.Scale(tool_bar, style='Horizontal.TScale', from_=0, to=100, command=self.on_buy_scale)
        scale_buy.place(x=60, y=y, width=80)
        scale_sell = ttk.Scale(tool_bar, style='Horizontal.TScale', from_=0, to=100, command=self.on_sell_scale)
        scale_sell.place(x=200, y=y, width=80)

        y += 30
        btn_buy = ttk.Button(tool_bar, text='BUY', command=self.app.common.hand_buy)
        btn_buy.place(x=10, y=y, width=130, height=25)
        btn_sell = ttk.Button(tool_bar, text='SELL', command=self.app.common.hand_sell)
        btn_sell.place(x=150, y=y, width=130, height=25)

    def on_buy_scale(self, val):
        v = int(float(val))
        self.buy_scale_qty.set(str(v) + '%')
        try:
            price = float(self.entry_buy_price.get())
            if price != '':
                qty = (float(self.entry_quote.get()) / price) * (v/100)

                around_qty = self.app.user.rules[self.app.bot.pair]['aroundQty']

                if round(qty, around_qty) * price > self.app.user.balances[self.app.user.curr_quote.upper()]['free']:
                    while round(qty, around_qty) * price > self.app.user.balances[self.app.user.curr_quote.upper()]['free']:
                        qty -= 0.1 ** around_qty

                self.entry_buy_qty.delete(0, tk.END)
                self.entry_buy_qty.insert(0, self.app.gui.fq(qty))
        except Exception as e:
            self.app.errors.error(121, e)
        return 0

    def on_sell_scale(self, val):
        v = int(float(val))
        self.sell_scale_qty.set(str(v) + '%')
        try:
            qty = float(self.entry_base.get()) * (v/100)

            around_qty = self.app.user.rules[self.app.bot.pair]['aroundQty']

            if round(qty, around_qty) > self.app.user.balances[self.app.user.curr_base.upper()]['free']:
                while round(qty, around_qty) > self.app.user.balances[self.app.user.curr_base.upper()]['free']:
                    qty -= 0.1 ** around_qty

            self.entry_sell_qty.delete(0, tk.END)
            self.entry_sell_qty.insert(0, self.app.gui.fq(qty))
        except Exception as e:
            self.app.errors.error(122, e)
        return 0

    def view_terminal(self):  # OK
        if self.app.user.balances:
            try:
                self.quote_asset.configure(text=self.app.user.curr_quote.upper())
                self.base_asset.configure(text=self.app.user.curr_base.upper())

                format_qty = '{:.8f}'

                quote_qty = str(format_qty.format(self.app.user.balances[self.app.user.curr_quote.upper()]['free']))
                base_qty = str(format_qty.format(self.app.user.balances[self.app.user.curr_base.upper()]['free']))

                self.entry_quote.delete(0, tk.END)
                self.entry_base.delete(0, tk.END)
                self.entry_quote.insert(0, quote_qty)
                self.entry_base.insert(0, base_qty)

            except Exception as e:
                self.app.errors.error(138, e)

        if self.app.user.bot_is_run:
            try:
                self.entry_buy_price.delete(0, tk.END)
                self.entry_buy_qty.delete(0, tk.END)
                self.entry_sell_price.delete(0, tk.END)
                self.entry_sell_qty.delete(0, tk.END)
                self.entry_buy_price.insert(0, self.app.gui.fp(self.app.user.buy_price))
                self.entry_buy_qty.insert(0, self.app.gui.fq(self.app.user.buy_qty))
                self.entry_sell_price.insert(0, self.app.gui.fp(self.app.user.sell_price))
                self.entry_sell_qty.insert(0, self.app.gui.fq(self.app.user.sell_qty))
            except Exception as e:
                self.app.errors.error(139, e)

    def hand_buy(self):
        order_price = float(self.entry_buy_price.get())
        order_qty = float(self.entry_buy_qty.get())
        if self.app.common.control_trade(order_price, order_qty):
            self.app.common.send_order('buy', order_price, order_qty)  ######### BUY

    def hand_sell(self):
        order_price = float(self.entry_sell_price.get())
        order_qty = float(self.entry_sell_qty.get())
        if self.app.common.control_trade(order_price, order_qty):
            self.app.common.send_order('sell', order_price, order_qty)  ######## SELL


class SettingsWindow(tk.Toplevel):

    def __init__(self, apply, root, app):
        super().__init__(root)
        self.app = app
        if apply:
            self.init_window()
        else:
            self.destroy()

    def init_window(self):

        self.title('Settings window')
        self.geometry('300x400'+self.app.gui.rand_xy())
        self.resizable(False, False)

        full_height = 440 if (self.app.user.activation.check() and not self.app.user.demo_mode) else (440 - 120)

        # Создаю внешний фрейм
        outer_frame = tk.Frame(self, bd=0, width=300, height=400)
        outer_frame.pack(side=tk.LEFT, expand=tk.YES, fill=tk.BOTH)

        # Создаю холст во внешнем фрейме
        self.canv = tk.Canvas(outer_frame, bd=0)
        self.canv.config(width=300, height=400)
        self.canv.config(scrollregion=(0, 2, 300, full_height))

        # Создаю скроллбар
        sbar = ttk.Scrollbar(outer_frame, orient='vertical', command=self.canv.yview, )
        self.canv.config(yscrollcommand=sbar.set)
        sbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canv.pack(side=tk.LEFT, expand=tk.YES, fill=tk.BOTH)

        # Создаю внутренний фрейм
        inner_frame = tk.Frame(self.canv, bd=0, bg='#ffffff', width=300, height=full_height + 5)
        self.canv.create_window((0, 0), window=inner_frame, anchor=tk.NW)

        bar = inner_frame

        y = 10
        tk.Label(bar, bg='#ffffff', text='API Keys Settings', font='Arial 10 bold').place(x=10, y=y)

        y += 25
        tk.Label(bar, bg='#ffffff', text='API Key').place(x=10, y=y)
        self.entry_key = ttk.Entry(bar)
        self.entry_key.place(x=100, y=y, width=170)

        y += 25
        tk.Label(bar, bg='#ffffff', text='API Secret').place(x=10, y=y)
        self.entry_secret = ttk.Entry(bar)
        self.entry_secret.place(x=100, y=y, width=170)

        y += 25
        tk.Label(bar, bg='#ffffff', text='Opt key').place(x=10, y=y)
        self.entry_optkey = ttk.Entry(bar)
        self.entry_optkey.place(x=100, y=y, width=170)

        if self.app.user.activation.check() and not self.app.user.demo_mode:
            y += 35
            tk.Label(bar, bg='#ffffff', text='Set number').place(x=10, y=y)
            self.entry_set = ttk.Combobox(bar, values=self.app.user.settings_list)
            self.entry_set.place(x=100, y=y, width=170)

            y += 25
            ttk.Button(bar, text='Save', command=self.app.common.save_set).place(x=10, y=y, width=80, height=23)
            ttk.Button(bar, text='Load', command=self.app.common.load_set).place(x=100, y=y, width=80, height=23)
            ttk.Button(bar, text='Delete', command=self.app.common.delete_set).place(x=190, y=y, width=80, height=23)

            y += 35
            tk.Label(bar, bg='#ffffff', text='Set 64string').place(x=10, y=y)
            self.entry_64string = ttk.Entry(bar)
            self.entry_64string.place(x=100, y=y, width=170)

            y += 25
            ttk.Button(bar, text='Encode', command=self.encode_settings).place(x=10, y=y, width=125, height=23)
            ttk.Button(bar, text='Decode', command=self.decode_settings).place(x=145, y=y, width=125, height=23)

        y += 35
        tk.Label(bar, bg='#ffffff', text='General Settings', font='Arial 10 bold').place(x=10, y=y)

        y += 25
        tk.Label(bar, bg='#ffffff', text='Exchange').place(x=10, y=y)
        self.entry_exchange = ttk.Combobox(bar, values=self.app.common.exchanges)
        self.entry_exchange.set(u'binance')
        self.entry_exchange.place(x=100, y=y, width=170)

        y += 25
        tk.Label(bar, bg='#ffffff', text='Pair').place(x=10, y=y)
        self.entry_pair = ttk.Entry(bar)
        self.entry_pair.place(x=100, y=y, width=170)

        y += 25
        tk.Label(bar, bg='#ffffff', text='Deposit').place(x=10, y=y)
        self.entry_depo = ttk.Entry(bar)
        self.entry_depo.place(x=100, y=y, width=170)

        y += 25
        tk.Label(bar, bg='#ffffff', text='Upd.time').place(x=10, y=y)
        self.entry_update_time = ttk.Entry(bar)
        self.entry_update_time.place(x=100, y=y, width=170)

        y += 35
        ttk.Button(bar, text='Apply', command=self.app.common.update_settings).place(x=10, y=y, width=125, height=23)
        ttk.Button(bar, text='Close', command=self.destroy).place(x=145, y=y, width=125, height=23)

        # Контроль колесика мыши
        # для Windows
        self.bind("<MouseWheel>", self.mouse_wheel)
        # для Linux
        self.bind("<Button-4>", self.mouse_wheel)
        self.bind("<Button-5>", self.mouse_wheel)

    def mouse_wheel(self, event):
        # воспроизведение события колесика мыши Linux or Windows
        if event.num == 5 or event.delta == -120:
            self.canv.yview_scroll(1, "units")
        if event.num == 4 or event.delta == 120:
            self.canv.yview_scroll(-1, "units")

    def get_set_data(self):
        data = dict()

        data['api_key'] = self.entry_key.get()
        data['api_secret'] = self.entry_secret.get()
        data['opt_key'] = self.entry_optkey.get()
        data['exchange'] = self.entry_exchange.get().lower()
        data['depo'] = float(self.entry_depo.get())
        data['pair'] = self.entry_pair.get().lower()
        data['upd_time'] = float(self.entry_update_time.get())

        if self.app.user.activation.check() and not self.app.user.demo_mode:
            data['num_set'] = self.entry_set.get()
        return data

    def encode_settings(self):
        data = self.get_set_data()
        json_string = json.dumps(data)

        data_string = b64encode(json_string.encode())

        self.entry_64string.delete(0, tk.END)
        self.entry_64string.insert(0, data_string.decode('utf-8'))

    def decode_settings(self):

        data_string = self.entry_64string.get()
        json_string = b64decode(data_string)

        data = json.loads(json_string)

        self.app.bot.upd(data)
        self.app.common.update_settings()
        self.view_settings()

    def view_settings(self):

        data = self.app.bot.get_set_data()

        self.entry_key.delete(0, tk.END)
        self.entry_secret.delete(0, tk.END)
        self.entry_optkey.delete(0, tk.END)
        self.entry_exchange.delete(0, tk.END)
        self.entry_pair.delete(0, tk.END)
        self.entry_update_time.delete(0, tk.END)

        self.entry_key.insert(0, data['api_key'] if 'api_key' in data else '')
        self.entry_secret.insert(0, data['api_secret'] if 'api_secret' in data else '')
        self.entry_optkey.insert(0, data['opt_key'] if 'opt_key' in data else '')
        self.entry_exchange.insert(0, data['exchange'].capitalize() if 'exchange' in data else '')
        self.entry_depo.insert(0, data['depo'] if 'depo' in data else '0.0')
        self.entry_pair.insert(0, data['pair'] if 'pair' in data else '')
        self.entry_update_time.insert(0, data['upd_time'] if 'upd_time' in data else '0.0')

        if self.app.user.activation.check():
            self.entry_set.delete(0, tk.END)
            self.entry_set.insert(0, data['num_set'] if 'num_set' in data else '')


class ChartWindow(tk.Toplevel):

    def __init__(self, apply, root, app):
        super().__init__(root)
        self.app = app
        if apply:
            self.init_window()
            self.draw()
        else:
            self.destroy()

    def init_window(self):
        self.title('Candlestick chart')
        self.geometry('400x300'+self.app.gui.rand_xy())
        self.resizable(False, False)
        self.bar = tk.Frame(self, bg='#ffffff', bd=0, width=400, height=300)
        self.bar.pack(side=tk.TOP, fill=tk.BOTH)
        self.canvas = tk.Canvas(self.bar, bg='#ffffff', bd=0, width=400, height=300)
        self.canvas.pack(fill=tk.BOTH, expand=1)
        self.canvas.create_line(10, 10, 390, 10, fill="#dddddd")
        self.canvas.create_line(10, 66, 390, 66, fill="#dddddd")
        self.canvas.create_line(10, 122, 390, 122, fill="#dddddd")
        self.canvas.create_line(10, 178, 390, 178, fill="#dddddd")
        self.canvas.create_line(10, 234, 390, 234, fill="#dddddd")
        self.canvas.create_line(390, 10, 390, 290, fill="#dddddd")
        self.canvas.create_line(10, 290, 390, 290, fill="#dddddd")

    def draw(self):

        ohlc_raw = self.app.kline.kline_1m[-30:]
        ohlc = dict()
        ohlc['time'] = list()
        ohlc['open'] = list()
        ohlc['high'] = list()
        ohlc['low'] = list()
        ohlc['close'] = list()
        for i in range(len(ohlc_raw)):
            ohlc['time'].append(ohlc_raw[i].t)
            ohlc['open'].append(ohlc_raw[i].o)
            ohlc['high'].append(ohlc_raw[i].h)
            ohlc['low'].append(ohlc_raw[i].l)
            ohlc['close'].append(ohlc_raw[i].c)
        if ohlc == dict():
            ohlc['time'].append(0)
            ohlc['open'].append(0)
            ohlc['high'].append(0)
            ohlc['low'].append(0)
            ohlc['close'].append(0)
        min_prices = list()
        max_prices = list()

        if self.app.user.orders:
            for order in self.app.user.orders:
                if order['side'] == 'buy':
                    min_prices.append(order['price'])
                if order['side'] == 'sell':
                    max_prices.append(order['price'])
        if len(ohlc_raw) > 0:

            min_prices.append(min(ohlc['low']))
            max_prices.append(max(ohlc['high']))
            fig_low, fig_high, ystep, n = self.__look_ranges(min(min_prices), max(max_prices))
            xstep = 380 // len(ohlc['time'])
            bar_width = xstep / 2
            pp = (fig_high - fig_low) / 280

            self.canvas.delete('my_chart')

            for i in range(len(ohlc['time'])):
                x1 = x2 = 10 + i * xstep + xstep / 2
                y1 = self.__get_y(fig_high, ohlc['low'][i], pp)
                y2 = self.__get_y(fig_high, ohlc['high'][i], pp)
                self.canvas.create_line(x1, y1, x2, y2, fill="#cccccc", tags='my_chart')

                x1 = 10 + i * xstep + xstep / 2 - bar_width / 2
                x2 = 10 + i * xstep + xstep / 2 + bar_width / 2
                y1 = self.__get_y(fig_high, ohlc['open'][i], pp)
                y2 = self.__get_y(fig_high, ohlc['close'][i], pp)
                color = '#3399cc' if ohlc['close'][i] > ohlc['open'][i] else '#ff3300'
                self.canvas.create_rectangle(x1, y1, x2, y2, outline="#cccccc", fill=color, width=1, tags='my_chart')

            x = 390
            y = self.__get_y(fig_high, ohlc['close'][-1], pp)
            self.canvas.create_text(x, y-1, anchor=tk.E, font='Arial 8', text='Last ' + self.app.gui.fp(ohlc['close'][-1]) + '►', tags='my_chart')

            self.canvas.create_text(100, 20, anchor=tk.W, font='Arial 9', text=self.app.bot.pair.upper()+' 1m', tags='my_chart')
            self.canvas.create_text(20, 20, anchor=tk.W, font='Arial 9', text=str(fig_high), tags='my_chart')
            self.canvas.create_text(20, 280, anchor=tk.W, font='Arial 9', text=str(fig_low), tags='my_chart')
            self.canvas.create_text(20, 66, anchor=tk.W, font='Arial 9', text=str(round(fig_high - 2 * ystep, 9)), fill='#666666', tags='my_chart')
            self.canvas.create_text(20, 122, anchor=tk.W, font='Arial 9', text=str(round(fig_high - 4 * ystep, 9)), fill='#666666', tags='my_chart')
            self.canvas.create_text(20, 178, anchor=tk.W, font='Arial 9', text=str(round(fig_high - 6 * ystep, 9)), fill='#666666', tags='my_chart')
            self.canvas.create_text(20, 234, anchor=tk.W, font='Arial 9', text=str(round(fig_high - 8 * ystep, 9)), fill='#666666', tags='my_chart')

            for order in self.app.user.orders:
                y = self.__get_y(fig_high, order['price'], pp)
                if order['side'] == 'buy':
                    self.canvas.create_text(390, y-1, anchor=tk.E, font='Arial 9', text='Buy Order '+self.app.gui.fp(order['price'])+'▲ —', fill='#003366', tags='my_chart')
                elif order['side'] == 'sell':
                    self.canvas.create_text(390, y-1, anchor=tk.E, font='Arial 9', text='Sell Order '+self.app.gui.fp(order['price'])+'▼ —', fill='#663300', tags='my_chart')

            self.canvas.pack(fill=tk.BOTH, expand=1)

    @staticmethod
    def __look_ranges(m, M):
        s = (round(log10(M - m)) - 1) if M - m > 0 else 0
        l = m - m % 10 ** s
        h = M - M % 10 ** s + 10 ** s
        step = (h - l) / 10
        return round(l, 9), round(h, 9), step, s - 1

    @staticmethod
    def __get_y(fh, p, pp):
        return (fh - p) / pp + 10


class DebugWindow(tk.Toplevel):

    def __init__(self, apply, root, app):
        super().__init__(root)
        self.app = app
        if apply:
            self.init_window()
        else:
            self.destroy()

    def init_window(self):
        self.title('Debug window')
        self.geometry('260x400'+self.app.gui.rand_xy())
        self.resizable(False, False)

        label_params = tk.Label(self, text='Params', font='Arial 10 bold')
        label_params.place(x=10, y=10)

        self.box = tk.Text(self, font='Arial 10', wrap=tk.WORD)
        sbar = tk.Scrollbar(self.box)
        sbar['command'] = self.box.yview
        self.box['yscrollcommand'] = sbar.set
        self.box.place(x=10, y=35, width=240, height=360)
        sbar.pack(side=tk.RIGHT, fill=tk.Y)

        req = dict()

        req['app_ver'] = self.app.user.ver
        req['app_build'] = self.app.user.build
        req['app_shared_key'] = self.app.user.shared_key
        req['app_demo_mode'] = self.app.user.demo_mode
        req['bot__________'] = ''
        req['bot_exchange'] = self.app.bot.exchange
        req['bot_pair'] = self.app.bot.pair
        req['bot_order_life'] = self.app.bot.order_life
        req['bot_depo'] = self.app.bot.depo
        req['bot_upd_time'] = self.app.bot.upd_time
        req['bot_pause'] = self.app.bot.pause
        req['pos__________'] = ''
        req['pos_price'] = self.app.position.price
        req['pos_qty'] = self.app.position.qty
        req['pos_exchange'] = self.app.position.exchange
        req['pos_pair'] = self.app.position.pair
        try:
            req['rules________'] = ''
            req['rules_min_price'] = self.app.user.rules[self.app.bot.pair]['minPrice']
            req['rules_max_price'] = self.app.user.rules[self.app.bot.pair]['maxPrice']
            req['rules_min_qty'] = self.app.user.rules[self.app.bot.pair]['minQty']
            req['rules_max_qty'] = self.app.user.rules[self.app.bot.pair]['maxQty']
            req['rules_min_sum'] = self.app.user.rules[self.app.bot.pair]['minSum']
            req['rules_max_sum'] = self.app.user.rules[self.app.bot.pair]['maxSum']
        except:
            pass
        req['user__________'] = ''
        req['user_api_init'] = self.app.user.api_is_init
        req['user_bot_init'] = self.app.user.bot_is_init
        req['user_bot_run'] = self.app.user.bot_is_run
        req['user_pos_init'] = self.app.user.pos_is_init
        req['user_kl_init'] = self.app.user.kl_is_init
        req['user_st_init'] = self.app.user.st_is_init
        req['user_last_price'] = self.app.user.last_price
        req['user_curr_base'] = self.app.user.curr_base
        req['user_curr_quote'] = self.app.user.curr_quote
        req['user_sell_trend_time'] = strftime('%y-%m-%d %H:%M', localtime(self.app.user.sell_trend_time))
        req['user_sell_trend_price'] = self.app.user.sell_trend_price
        req['user_start_buy_trade'] = strftime('%y-%m-%d %H:%M', localtime(self.app.user.start_buy_trading))
        req['user_start_sell_trade'] = strftime('%y-%m-%d %H:%M', localtime(self.app.user.start_sell_trading))

        list_keys = list(req.keys())
        list_keys.sort()

        param_string = ''
        for item in list_keys:
            param_string += item + ': ' + str(req[item]) + '\n'

        self.box.insert(tk.END, param_string)
        self.box.configure(state='disabled')
        self.box.yview_moveto(1)


class InfoWindow(tk.Toplevel):

    def __init__(self, apply, root, app):
        super().__init__(root)
        self.app = app

        self.big_logo = tk.PhotoImage(data='R0lGODlhQABAAKIAAHKfzwAzZjNmmQpIhGaZZpnMZv///xAQECH/C05FVFNDQVBFMi4wAwEAAAAh+QQEAAAAACwAAAAAQABAAAAD/2i63P4wykmrvTjrzbv/YCiOZGmeqDUA7JCGg8ACgvt68VzfuOD7Nt5mEAMGhRqiEvk5MEHOpycqDViv2Kx2y8WCuuAw+Csum8nmdBdtJbjf8Lh87s6yA/S8/m3/ZAuAgYKDhIWAfR5/houMh15+WI2ShYhDA4qTmQVZRElKmJqSnEsqOQKgoYxZMjVHETksp5GABwepgbWBqzquDzM0l7O1uanDtptYsCwUsUB/xsSZ0LacP8sTP86R06Hc1dkU2TXP0IPHuILeyeLh2cFXtMOE0dHxxN8/7T/vVrjn5sYKRcPnQ582eLcaERRgcNyshIsWUlASg18AiKrWUaxA0VMixojJNpYiguqjrpCdMpB8aFLQqEQsWzq6ckfmoEocVonbybPnD5wbdPoc6hOoBjVIt9xJinQp0zROn5aRQrWq1atYs2rdyrWr169gw4odSzZDAgA7')

        if apply:
            self.__init_window()
        else:
            self.destroy()

    def __init_window(self):
        self.title('About')
        self.geometry('260x300'+self.app.gui.rand_xy())
        self.resizable(False, False)

        tool_bar = tk.Frame(self, bg='#ffffff', bd=0, width=260, height=300)
        tool_bar.pack(side=tk.TOP, fill=tk.BOTH)

        y = 10
        tk.Label(tool_bar, image=self.big_logo, bd=0).place(x=10, y=0)
        tk.Label(tool_bar, text=self.app.user.name + ' '+self.app.user.ver, bg='#ffffff', font='Arial 10 bold').place(x=90, y=y)

        y += 20
        tk.Label(tool_bar, text='Build '+self.app.user.build, bg='#ffffff', font='Arial 10').place(x=90, y=y)

        y += 40
        tk.Label(tool_bar, text='Trading terminal. All exchanges', bg='#ffffff', font='Arial 10').place(x=10, y=y)

        y += 20
        tk.Label(tool_bar, text='in one application. ', bg='#ffffff', font='Arial 10').place(x=10, y=y)

        y += 40
        tk.Label(tool_bar, text='YouTube:', bg='#ffffff', font='Arial 10').place(x=10, y=y)

        label_youtube = tk.Label(tool_bar, text='youtu.be/xAWvQv-8tdE', fg='blue', cursor="hand2", bg='#ffffff', font='Arial 10')
        label_youtube.place(x=69, y=y)
        label_youtube.bind("<Button-1>", self.callback_youtube)

        y += 20
        tk.Label(tool_bar, text='GitHub: ', bg='#ffffff', font='Arial 10').place(x=10, y=y)

        label_github = tk.Label(tool_bar, text='github.com/savinkirillnick/...', fg='blue', cursor="hand2", bg='#ffffff', font='Arial 10')
        label_github.place(x=58, y=y)
        label_github.bind("<Button-1>", self.callback_github)

        y += 40
        tk.Label(tool_bar, text='Registration and download last versions', bg='#ffffff', font='Arial 10').place(x=10, y=y)

        y += 20
        tk.Label(tool_bar, text='Telegram:', bg='#ffffff', font='Arial 10').place(x=10, y=y)

        label_telegram = tk.Label(tool_bar, text='@savin_account_manager_bot', fg='blue', cursor="hand2", bg='#ffffff', font='Arial 10')
        label_telegram.place(x=71, y=y)
        label_telegram.bind("<Button-1>", self.callback_telegram)

        y += 40
        tk.Label(tool_bar, text='Developed by Kirill Savin', bg='#ffffff', font='Arial 10').place(x=10, y=y)

        y += 20
        tk.Label(tool_bar, text='2017-2024', bg='#ffffff', font='Arial 10').place(x=10, y=y)

    @staticmethod
    def callback_youtube(event):
        webbrowser.open_new('https://www.youtube.com/watch?v=xAWvQv-8tdE')

    @staticmethod
    def callback_github(event):
        webbrowser.open_new('https://github.com/savinkirillnick/terminal')

    @staticmethod
    def callback_telegram(event):
        webbrowser.open_new('https://web.telegram.org/k/#@savin_account_manager_bot')

