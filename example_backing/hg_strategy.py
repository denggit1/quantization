# coding:utf-8
# @Time    : 2020-08
# @Author  : D

"""
简单海龟策略：
    K线连续突破做多
    K线连续跌破做空
"""

from talib import _ta_lib as ta
import BackTestApi
import numpy as np
import kline_data


class DBackTest(BackTestApi.BackTest):
    def get_turtle_sign(self, priceList, n_2):
        # 开多， 开空， N/2平空， N/2平多
        max_price_n = priceList.max()
        min_price_n = priceList.min()
        max_price_n2 = priceList[-n_2:].max()
        min_price_n2 = priceList[-n_2:].min()
        # 判断信号
        if self.status == 0:
            if priceList[-1] == max_price_n:
                self.sign = '1'
            elif priceList[-1] == min_price_n:
                self.sign = '-1'
        elif self.status == 1:
            if priceList[-1] == min_price_n2:
                if priceList[-1] == min_price_n:
                    self.sign = '0-1'
                else:
                    self.sign = '0'
        elif self.status == -1:
            if priceList[-1] == max_price_n2:
                if priceList[-1] == max_price_n:
                    self.sign = '01'
                else:
                    self.sign = '0'

    def trade_test(self, data, n_list):
        # n_1, n_2
        n_1 = n_list[0]
        n_2 = n_list[1]
        # ##
        pre = [data[0][0][:6], self.default_usdt]
        self.month_list = []
        # 回测计算
        priceList = np.array(data[:n_1])[:, 4].astype(float)
        moneyResult = []
        self.timeResult = []
        for i in range(n_1, len(data)):
            # 坐标定位 >> n_1
            priceList = np.append(priceList, float(data[i][4]))
            priceList = np.delete(priceList, 0)
            # 获取信号至self.sign
            self.get_turtle_sign(priceList, n_2)
            # 判断交易方向
            if self.status == 0:
                if self.sign == '1':
                    self.open_buy(priceList[-1], data[i][0])
                elif self.sign == '-1':
                    self.open_sell(priceList[-1], data[i][0])
            elif self.status == 1:
                if self.sign == '0-1':
                    self.close_sell(priceList[-1], data[i][0])
                    self.open_sell(priceList[-1], data[i][0])
                elif self.sign == '0':
                    self.close_sell(priceList[-1], data[i][0])
            elif self.status == -1:
                if self.sign == '01':
                    self.close_buy(priceList[-1], data[i][0])
                    self.open_buy(priceList[-1], data[i][0])
                elif self.sign == '0':
                    self.close_buy(priceList[-1], data[i][0])
            # 资金
            usdt = self.usdt_num + self.eth_num * priceList[-1]
            moneyResult.append(usdt)
            self.timeResult.append(data[i][0])
            # 统计月化收益
            if data[i][0][-8:] == "01075900":
                self.month_list.append([pre[0], (usdt - pre[1]) / 30000.0])
            elif data[i][0][-8:] == "01080000":
                pre = [data[i][0][:6], usdt]
        return moneyResult


def run():
    # 1
    bt = DBackTest()
    bt.__init__(usdt_num=100000.0, trade_usdt=50000.0, rate=0.000)
    kd = kline_data.KlineData()
    df = kd.return_df(symbol="ETHUSDT", interval="1m", s="2020-08-01 00:00:00", e="2021-07-23 00:00:00")
    data = df[["ntime", "open", "high", "low", "close"]].values
    bt.test(data, [3000, 1700])
    bt.cap_show()


if __name__ == '__main__':
    run()
