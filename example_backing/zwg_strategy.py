# coding:utf-8
# @Time    : 2021-03
# @Author  : D

"""
中性网格策略：
    以起点位置布置网格
    上下各百分比
"""

import time
from talib import _ta_lib as ta
import BackTestApi
import kline_data
import numpy as np


class DBackTest(BackTestApi.BackTest):
    def open_sell(self, price, nTime, trade_usdt=None, trade_num=None):
        # 下单量
        if trade_num:
            trade_usdt = trade_num * round(price - self.slippage, 6) * (1 - self.rate)
        elif trade_usdt:
            trade_num = trade_usdt / round(price - self.slippage, 6) * (1 + self.rate)
        else:
            trade_usdt = self.trade_usdt
            trade_num = trade_usdt / round(price - self.slippage, 6) * (1 + self.rate)
        # 空仓开仓, price: float, nTime: str
        self.bond += trade_usdt
        self.usdt_num += trade_usdt
        self.eth_num -= trade_num
        # 修改信息
        self.trade_count += 1
        self.status = -1
        # 添加订单
        self.orders.append(
            ['open_sell', nTime[:-2] + '01', round(price - self.slippage, 6),
             trade_num,
             self.eth_num, self.usdt_num, self.eth_num + self.usdt_num / price,
             self.usdt_num + self.eth_num * price])
        self.mr.append(self.usdt_num + self.eth_num * price)
        self.mr_time.append(nTime[:-2] + '01')
        self.open_list = ["open_sell", price]
        return trade_num

    def open_buy(self, price, nTime, trade_usdt=None, trade_num=None):
        # 下单量
        if trade_num:
            trade_usdt = trade_num * round(price + self.slippage, 6) * (1 + self.rate)
        elif trade_usdt:
            trade_num = trade_usdt / round(price + self.slippage, 6) * (1 - self.rate)
        else:
            trade_usdt = self.trade_usdt
            trade_num = trade_usdt / round(price + self.slippage, 6) * (1 - self.rate)
        # 多仓开仓, price: float, nTime: str
        self.bond += trade_usdt
        self.usdt_num -= trade_usdt
        self.eth_num += trade_num
        # 修改信息
        self.trade_count += 1
        self.status = 1
        # 添加订单
        self.orders.append(
            ['open_buy', nTime[:-2] + '01', round(price + self.slippage, 6),
             trade_num,
             self.eth_num, self.usdt_num, self.eth_num + self.usdt_num / price,
             self.usdt_num + self.eth_num * price])
        self.mr.append(self.usdt_num + self.eth_num * price)
        self.mr_time.append(nTime[:-2] + '01')
        self.open_list = ["open_buy", price]
        return trade_num

    def close_buy(self, price, nTime, trade_num=None):
        # 下单量
        if not trade_num: trade_num = abs(self.eth_num)
        # 空仓平仓, price: float, nTime: str
        self.bond = 0
        self.usdt_num -= trade_num * round(price + self.slippage, 6) * (1 + self.rate)
        self.eth_num += trade_num
        # 修改信息
        self.trade_count += 1
        self.status = 0
        # 添加订单
        self.orders.append(
            ['close_buy', nTime[:-2] + '00', round(price + self.slippage, 6),
             trade_num, self.eth_num, self.usdt_num, self.eth_num + self.usdt_num / price,
             self.usdt_num + self.eth_num * price])
        self.mr.append(self.usdt_num + self.eth_num * price)
        self.mr_time.append(nTime[:-2] + '00')
        return trade_num

    def close_sell(self, price, nTime, trade_num=None):
        # 下单量
        if not trade_num: trade_num = abs(self.eth_num)
        # 多仓平仓, price: float, nTime: str
        self.bond = 0
        self.usdt_num += trade_num * round(price - self.slippage, 6) * (1 - self.rate)
        self.eth_num -= trade_num
        # 修改信息
        self.trade_count += 1
        self.status = 0
        # 添加订单
        self.orders.append(
            ['close_sell', nTime[:-2] + '00', round(price - self.slippage, 6),
             trade_num, self.eth_num, self.usdt_num, self.eth_num + self.usdt_num / price,
             self.usdt_num + self.eth_num * price])
        self.mr.append(self.usdt_num + self.eth_num * price)
        self.mr_time.append(nTime[:-2] + '00')
        return trade_num

    def trade_test(self, df, n_list):
        """ 参数、变量 """
        zx_rate = n_list[0]
        df["close"] = df["close"].astype(float)
        obc, osc, csc, cbc = 0, 0, 0, 0
        # 变量
        index = 0
        pre_price = df.iloc[0]["close"]

        """ 指标计算 """
        pass

        """ 模拟回测 """
        money_result = []
        for i in range(len(df)):
            # 常量
            ntime = df.iloc[i]["ntime"]
            close = df.iloc[i]["close"]

            """ 逻辑START """
            # 判断平仓
            if index >= 1:
                while close < pre_price * (1.0 + zx_rate * (index - 1)):
                    self.close_buy(pre_price * (1.0 + zx_rate * (index - 1)), ntime, trade_num=1)
                    index -= 1
                    cbc += 1
            # 判断平仓
            elif index <= -1:
                while close > pre_price * (1.0 + zx_rate * (index + 1)):
                    self.close_sell(pre_price * (1.0 + zx_rate * (index + 1)), ntime, trade_num=1)
                    index += 1
                    csc += 1
            # 判断开仓
            if close > pre_price:
                # 判断开仓
                while close > pre_price * (1.0 + zx_rate * (index + 1)):
                    self.open_sell(pre_price * (1.0 + zx_rate * (index + 1)), ntime, trade_num=1)
                    index += 1
                    osc += 1
            elif close < pre_price:
                # 判断开仓
                while close < pre_price * (1.0 + zx_rate * (index - 1)):
                    self.open_buy(pre_price * (1.0 + zx_rate * (index - 1)), ntime, trade_num=1)
                    index -= 1
                    obc += 1
            """ 逻辑END """

            # 净值曲线
            usd = self.usdt_num + self.eth_num * close
            money_result.append(usd)
            # 统计月化收益
            self.tj_month(ntime, usd)

        """ 其他 """
        self.count = int((csc + cbc) / 30)
        print("开多 {}，平多 {}，开空 {}，平空 {}\n每日频率：{}".format(obc / 30, csc / 30, osc / 30, cbc / 30, self.count))

        return money_result


def run():
    init_time = time.time()
    bt = DBackTest()
    bt.__init__(usdt_num=30000.0, trade_usdt=300.0, rate=0.0002)
    bt.order_bool = True
    kd = kline_data.KlineData()
    df = kd.return_df(symbol="AXSUSDT", interval="1m", s="2021-06-21 00:00:00", e="2021-07-21 00:00:00")
    # 突破、回调、盈利、反弹
    bt.test(df, [0.0025])
    print("回测耗时：", time.time() - init_time)
    bt.cap_show()


if __name__ == '__main__':
    run()
