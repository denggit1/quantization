# coding:utf-8
# @Time    : 2021-05
# @Author  : D

"""
勾空MD实盘：
    上突破下回调，开空
    下获利上反弹，平空
"""

import binance_f.impl.utils.urlparamsbuilder
import binance_f.impl.restapiinvoker
import binance_f.impl.websocketconnection
from binance_f import SubscriptionClient

import time
import platform
import traceback
import logging
import numpy as np
from math import log
import binance_f
from binance_f.model.constant import OrderSide, OrderType, TimeInForce


# 勾空MD实盘
class GkReal(object):
    # 初始化
    def __init__(self, api, secret, main_bool=True, ul="tt_gk"):
        # 账户
        self.api_key = api
        self.secret_key = secret
        self.request_client = binance_f.RequestClient(api_key=self.api_key, secret_key=self.secret_key)
        self.req_sleep = 3
        self.sleep = 3
        self.cid_prefix = "x-2dbDjbv3-"
        # 创建日志
        uname, log_name = ul.split("_")
        self.logger, self.proxy_host, self.proxy_port = self.create_log(uname, log_name)
        # 此类需要
        if main_bool:
            # 品种
            self.symbol = "QTUMUSDT"
            self.pr, self.qr = self.get_pr_qr()
            # 参数
            self.break_rate = 0.02 / 2
            self.callback_rate = 0.005 / 2
            self.profit_rate = 0.015 / 2
            self.rebound_rate = 0.005 / 2
            self.trade_usd = 6
            # 常量
            self.index, self.pre_price, self.high_price, self.low_price, \
            self.sell_list, self.avg_price = self.init_trade()
            # 日志记录
            self.logger.critical("参数：s_{} break_{} back_{} pro_{} reb_{} usd_{}".format(
                self.symbol, self.break_rate, self.callback_rate, self.profit_rate, self.rebound_rate, self.trade_usd))
            self.logger.critical("初始：index_{} pre_{} high_{} low_{} list_{} avg_{}".format(
                self.index, self.pre_price, self.high_price, self.low_price, self.sell_list, self.avg_price))

    # 创建日志
    @staticmethod
    def create_log(uname="tt", log_name="gk"):
        if platform.system().lower() == "windows":
            logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(message)s',
                                filename="D:\\test\\DateTimeDirs\\2021\\realing\\logs\\{}.log".format(log_name))
            logger = logging.getLogger()
            proxy_host, proxy_port = "192.168.1.13", 10809
            logger.critical("windows日志已创建，代理：{} {}".format(proxy_host, proxy_port))
        else:
            logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(message)s',
                                filename="/root/TradeDirs/freq/{}/logs/{}.log".format(uname, log_name))
            logger = logging.getLogger()
            proxy_host, proxy_port = None, None
            logger.critical("linux日志已创建，代理：{} {}".format(proxy_host, proxy_port))
        return logger, proxy_host, proxy_port

    # 异常处理
    def while_func(func):
        #
        def wp(self):
            while True:
                try:
                    res = func(self)
                    return res
                except Exception as e:
                    error = traceback.format_exc()
                    error = error.replace(" ", "").replace("\n", " ")
                    self.logger.critical("{}, {}".format(e, error))
                time.sleep(3)

        return wp

    # 获取价格
    @while_func
    def get_tick(self):
        return float(self.request_client.get_symbol_price_ticker(self.symbol)['price'])

    # 获取交易规则
    @while_func
    def get_info(self):
        return self.request_client.get_exchange_information()["symbols"]

    # 获取精度
    def get_pr_qr(self):
        info = self.get_info()
        filters = []
        for symbol in info:
            if symbol["symbol"] == self.symbol:
                filters = symbol["filters"]
        tickSize, stepSize = float(filters[0]["tickSize"]), float(filters[1]["stepSize"])
        price_round = int(round(log(tickSize, 0.1), 0))
        quantity_round = int(round(log(stepSize, 0.1), 0))
        return price_round, quantity_round

    # 查询请求
    def get_order(self, symbol, client_id):
        return self.request_client.get_order(symbol, origClientOrderId=client_id)

    # 下单请求
    def send_order(self, symbol, side, order_type, quantity, price, client_id, reduce_only):
        # side
        if side == "BUY": os = OrderSide.BUY
        elif side == "SELL": os = OrderSide.SELL
        else: os = None
        # order_type
        if order_type == "MARKET":
            ot = OrderType.MARKET
            tif = TimeInForce.INVALID
        elif order_type == "LIMIT":
            ot = OrderType.LIMIT
            tif = TimeInForce.GTC
        else:
            ot = None
            tif = None
        # request
        res = self.request_client.post_order(
            symbol, os, ot, quantity=quantity, price=price, timeInForce=tif,
            newClientOrderId=client_id, reduceOnly=reduce_only)
        return res

    # 下单查询请求
    def post_order(self, symbol, side, order_type, quantity, price, client_id, reduce_only):
        # 请求
        try: res = self.send_order(symbol, side, order_type, quantity, price, client_id, reduce_only)
        except: res = None
        # 循环
        while not res:
            try:
                order = self.get_order(self.symbol, client_id).get('clientOrderId', '')
                if not order:
                    res = self.send_order(symbol, side, order_type, quantity, price, client_id, reduce_only)
            except: res = None
            time.sleep(self.req_sleep)
        return res

    # 卖出
    def sell(self, quantity, price=None, client_id=None, reduce_only=False):
        # 客户端ID
        if not client_id: client_id = self.cid_prefix + str(int(time.time() * 1000))
        # 限价市价区分
        if price: res = self.post_order(self.symbol, "SELL", "LIMIT", quantity, price, client_id, reduce_only)
        else: res = self.post_order(self.symbol, "SELL", "MARKET", quantity, price, client_id, reduce_only)
        self.logger.critical("卖出：{}".format(res))
        return res

    # 买入
    def buy(self, quantity, price=None, client_id=None, reduce_only=False):
        # 客户端ID
        if not client_id: client_id = self.cid_prefix + str(int(time.time() * 1000))
        # 限价市价区分
        if price: res = self.post_order(self.symbol, "BUY", "LIMIT", quantity, price, client_id, reduce_only)
        else: res = self.post_order(self.symbol, "BUY", "MARKET", quantity, price, client_id, reduce_only)
        self.logger.critical("买入：{}".format(res))
        return res

    # 初始化交易信息
    def init_trade(self):
        tick_price = self.get_tick()
        # self.index, self.pre_price, self.high_price, self.low_price, self.sell_list, self.avg_price
        return 0, tick_price, tick_price, tick_price, [], np.nan

    # 执行
    def run(self):
        close = self.get_tick()
        # 记录高低点价格
        if close > self.high_price: self.high_price = close
        if close < self.low_price: self.low_price = close
        # 开平条件
        open_bool = (close > self.pre_price * (1.0 + self.break_rate)) and (
                close < self.high_price * (1.0 - self.callback_rate))
        close_bool = (close < self.avg_price * (1.0 - self.profit_rate)) and (
                close > self.low_price * (1.0 + self.rebound_rate))
        # 逻辑
        if close_bool:
            trade_num = round(np.array(self.sell_list)[:, 1].sum(), self.qr)
            self.buy(trade_num, reduce_only=True)
            # 重置
            self.index, self.pre_price, self.high_price, self.low_price, \
            self.sell_list, self.avg_price = self.init_trade()
            self.logger.critical("重置：index_{} pre_{} high_{} low_{} list_{} avg_{}".format(
                self.index, self.pre_price, self.high_price, self.low_price, self.sell_list, self.avg_price))
        elif open_bool:
            trade_num = round(self.trade_usd * pow(2, self.index) / close, self.qr)
            self.sell(trade_num)
            # 更替
            self.index, self.pre_price, self.low_price = self.index + 1, close, close
            self.sell_list.append([close, trade_num])
            sell_arr = np.array(self.sell_list)
            self.avg_price = (sell_arr[:, 0] * sell_arr[:, 1]).sum() / sell_arr[:, 1].sum()
            self.logger.critical("更替：index_{} pre_{} high_{} low_{} list_{} avg_{}".format(
                self.index, self.pre_price, self.high_price, self.low_price, self.sell_list, self.avg_price))

    # 启动
    def start(self):
        while True:
            try:
                self.run()
            except Exception as e:
                error = traceback.format_exc()
                error = error.replace(" ", "").replace("\n", " ")
                self.logger.critical("{}, {}".format(e, error))
            time.sleep(self.sleep)


if __name__ == '__main__':
    api_key = ""
    secret_key = ""
    gr = GkReal(api_key, secret_key)
    gr.start()
