# coding:utf-8
# @Time    : 2019-08
# @Author  : D

import pandas as pd

import BackTestApi
import kline_data
import time
import numpy as np
from multiprocessing import Process, Lock, Manager
import matplotlib.pyplot as plt


class DBackTest(BackTestApi.BackTest):
    def trade_test(self, data, n_list):
        """
        回测计算函数
        :param data: 数据
        :param n_list: 参数列表
        :return: 资金曲线
        """
        # 参数常量
        n_1 = 1440
        n_2 = 1.0
        n_3 = 1.0
        n_zero_def = n_list[0]
        n_zero = n_list[0]
        n_one = n_list[1]
        t_rate = n_list[2]
        # 回测计算
        high = np.array([float(temp[4]) for temp in data[:n_1]])
        low = np.array([float(temp[4]) for temp in data[:n_1]])
        high_price = high.max()
        low_price = low.min()
        close_price = float(data[n_1 - 1][4])
        touch = max((high_price - close_price) / close_price, (close_price - low_price) / close_price)
        up = close_price * (n_2 + touch)
        dn = close_price * (n_3 - touch)
        if touch > t_rate:
            self.ct = True
        else:
            self.ct = False
        ustime = time.strftime("%Y%m%d", time.localtime(
            time.mktime(time.strptime(data[0][0][:8], "%Y%m%d")) + 1440 * 60)) + "075900"
        # 记录
        moneyResult = []
        for i in range(n_1, len(data)):
            # 坐标定位 >> n_1
            close_price = float(data[i][4])
            # 变更日内上下轨道 075900
            if data[i][0] >= ustime:
                if self.status == 1:
                    self.close_sell(float(data[i][4]), data[i][0])
                elif self.status == -1:
                    self.close_buy(float(data[i][4]), data[i][0])
                high = np.array([float(temp[4]) for temp in data[i + 1 - n_1: i + 1]])
                low = np.array([float(temp[4]) for temp in data[i + 1 - n_1: i + 1]])
                high_price = high.max()
                low_price = low.min()
                touch = max((high_price - close_price) / close_price, (close_price - low_price) / close_price)
                up = close_price * (1 + touch)
                dn = close_price * (1 - touch)
                if touch > t_rate:
                    self.ct = True
                else:
                    self.ct = False
                self.open_list = []
                n_zero = n_zero_def
                ustime = time.strftime("%Y%m%d%H%M%S",
                                       time.localtime(
                                           time.mktime(time.strptime(data[i][0], "%Y%m%d%H%M%S")) + 1440 * 60))
            if not self.ct:
                # ### 止盈 止损 限制订单
                if self.open_list != []:
                    if self.open_list[0] == "open_buy":
                        if close_price < float(self.open_list[1]) * (1 - n_zero):
                            if self.status == 1:
                                self.close_sell(float(data[i][4]), data[i][0])
                            elif self.status == -1:
                                self.close_buy(float(data[i][4]), data[i][0])
                            self.ct = True
                        elif close_price > float(self.open_list[1]) * (1 + n_one):
                            n_zero = -0.005
                    elif self.open_list[0] == "open_sell":
                        if close_price > float(self.open_list[1]) * (1 + n_zero):
                            if self.status == 1:
                                self.close_sell(float(data[i][4]), data[i][0])
                            elif self.status == -1:
                                self.close_buy(float(data[i][4]), data[i][0])
                            self.ct = True
                        elif close_price < float(self.open_list[1]) * (1 - n_one):
                            n_zero = -0.005
                # 判断
                if self.status == 0:
                    if close_price > up:
                        self.open_buy(float(data[i][4]), data[i][0])
                    elif close_price < dn:
                        self.open_sell(float(data[i][4]), data[i][0])
                elif self.status == 1:
                    if close_price < dn:
                        self.close_sell(float(data[i][4]), data[i][0])
                        self.open_sell(float(data[i][4]), data[i][0])
                elif self.status == -1:
                    if close_price > up:
                        self.close_buy(float(data[i][4]), data[i][0])
                        self.open_buy(float(data[i][4]), data[i][0])
            # usdt
            usdt = self.usdt_num + self.eth_num * float(data[i][4])
            moneyResult.append(usdt)
            # 统计月化收益
            self.tj_month(data[i][0], usdt)
        return np.array(moneyResult)


def run():
    # 1
    bt = DBackTest()
    bt.__init__(usdt_num=30000.0, trade_usdt=30000.0, rate=0.000)
    kd = kline_data.KlineData()
    df = kd.return_df(symbol="ETHUSDT", interval="1m", s="2020-07-23 00:00:00", e="2021-07-23 00:00:00")
    data = df[["ntime", "open", "high", "low", "close"]].values
    bt.test(data, [0.01, 0.09, 0.09])
    bt.cap_show()


if __name__ == '__main__':
    run()
