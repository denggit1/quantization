# coding:utf-8
# @Time    : 2021-05
# @Author  : D

"""
经典网格策略
"""

import time

import binance_f
from RealApi import GkReal
from binance_f.model import SubscribeMessageType
from binance_f.exception.binanceapiexception import BinanceApiException
from binance_f.model.constant import OrderSide


# 单多网格
class WgReal(GkReal):
    # 初始化
    def __init__(self, api, secret):
        super().__init__(api, secret, main_bool=False, ul="tt_wg")
        self.sub_client = binance_f.SubscriptionClient(api_key=api_key, secret_key=secret_key)
        self.listen_key = self.create_stream()
        # 品种
        self.symbol = "ICPUSDT"
        self.pr, self.qr = self.get_pr_qr()
        # 常量
        self.init_trade()

    # 生成流
    @GkReal.while_func
    def create_stream(self):
        return self.request_client.start_user_data_stream()['listenKey']

    # 保持流
    @GkReal.while_func
    def keep_stream(self):
        return self.request_client.keep_user_data_stream()

    # 错误
    def order_error(self, e: 'BinanceApiException'):
        self.logger.critical("Order连接错误：{} {}".format(e.error_code, e.error_message))

    # 错误
    def tick_error(self, e: 'BinanceApiException'):
        self.logger.critical("Tick连接错误：{} {}".format(e.error_code, e.error_message))

    # 交易订单订阅
    def order_run(self):
        self.sub_client.subscribe_user_data_event(self.listen_key, self.on_order, self.order_error,
                                                  self.proxy_host, self.proxy_port)

    # 行情价格订阅
    def tick_run(self):
        self.sub_client.subscribe_symbol_ticker_event(self.symbol.lower(), self.on_tick, self.tick_error,
                                                      self.proxy_host, self.proxy_port)

    # Tick主程序
    def on_tick(self, data_type: 'SubscribeMessageType', event: 'any'):
        if data_type == SubscribeMessageType.RESPONSE:
            self.logger.critical("Tick Event ID: {}".format(event))
        elif data_type == SubscribeMessageType.PAYLOAD:
            # print(self.symbol, event.lastPrice, type(event.lastPrice))
            pass
        else:
            self.logger.critical("Tick Unknown Data")

    # Order主程序
    def on_order(self, data_type: 'SubscribeMessageType', event: 'any'):
        # 返回ID
        if data_type == SubscribeMessageType.RESPONSE:
            self.logger.critical("Order Event ID: {}".format(event))
        # 返回流
        elif data_type == SubscribeMessageType.PAYLOAD:
            # 净值，持仓
            if event.eventType == "ACCOUNT_UPDATE":
                # print("e:",event.eventType,"E:",event.eventTime,"B:",type(event.balances),"P:",type(event.positions))
                pass
            # 订单更新
            elif event.eventType == "ORDER_TRADE_UPDATE":
                # 订单状态为成交时
                if event.orderStatus == "FILLED":
                    # 订单属于此策略
                    if event.symbol == self.symbol and event.clientOrderId.startswith(self.cid_prefix):
                        if event.side == OrderSide.BUY:
                            self.sell(event.origQty, round(event.price * (1.0 + 0.002), self.pr))
                        elif event.side == OrderSide.SELL:
                            self.buy(event.origQty, round(event.price / (1.0 + 0.002), self.pr))
            # 异常key过期
            elif event.eventType == "listenKeyExpired":
                self.logger.critical("e:{}, E:{}".format(event.eventType, event.eventTime))
        # 异常
        else:
            self.logger.critical("Order Unknown Data")

    # 初始化交易信息
    def init_trade(self):
        tick = self.get_tick()
        for i in range(25):
            tick = round(tick / (1.0 + 0.002), self.pr)
            self.buy(0.2, tick)
            time.sleep(0.1)
        self.logger.critical("初始下单完成！")

    # 运行
    def run(self):
        # self.tick_run()
        self.order_run()

    # 启动
    def start(self):
        self.run()
        while True:
            time.sleep(60 * 58)
            res = self.keep_stream()
            self.logger.critical("延长有效：{}".format(res))


if __name__ == '__main__':
    api_key = ""
    secret_key = ""
    gr = WgReal(api_key, secret_key)
    gr.start()
