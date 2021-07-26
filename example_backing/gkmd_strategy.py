# coding:utf-8
# @Time    : 2020-12
# @Author  : D

"""
勾空MD策略：
    上突破下回调，开空
    下获利上反弹，平空
"""

import time

from talib import _ta_lib as ta
import BackTestApi
import kline_data
import numpy as np


class DBackTest(BackTestApi.BackTest):
    def open_sell(self, price, nTime, trade_usdt=None):
        # 下单量
        if not trade_usdt: trade_usdt = self.trade_usdt
        # 空仓开仓, price: float, nTime: str
        self.bond += trade_usdt
        self.usdt_num += trade_usdt
        trade_num = trade_usdt / round(price - self.slippage, 6) * (1 + self.rate)
        self.eth_num -= trade_num
        # 修改信息
        self.trade_count += 1
        self.status = -1
        # 添加订单
        self.orders.append(
            ['open_sell', nTime[:-2] + '01', round(price - self.slippage, 6),
             trade_usdt / round(price - self.slippage, 6) * (1 + self.rate),
             self.eth_num, self.usdt_num, self.eth_num + self.usdt_num / price,
             self.usdt_num + self.eth_num * price])
        self.mr.append(self.usdt_num + self.eth_num * price)
        self.mr_time.append(nTime[:-2] + '01')
        self.open_list = ["open_sell", price]
        return trade_num

    def trade_test(self, df, n_list):
        """ 参数、变量 """
        break_rate = n_list[0]
        callback_rate = n_list[1]
        profit_rate = n_list[2]
        rebound_rate = n_list[3]
        df["close"] = df["close"].astype(float)
        max_index = 0
        # 变量
        index = 0
        pre_price = df.iloc[0]["close"]
        high_price = df.iloc[0]["close"]
        low_price = df.iloc[0]["close"]
        sell_list = []
        avg_price = np.nan

        """ 指标计算 """
        pass

        """ 模拟回测 """
        money_result = []
        for i in range(len(df)):
            # 常量
            ntime = df.iloc[i]["ntime"]
            close = df.iloc[i]["close"]

            """ 逻辑START """
            # 记录高低点价格
            if close > high_price: high_price = close
            if close < low_price: low_price = close
            # 开仓条件
            open_bool = (close > pre_price * (1.0 + break_rate)) and (close < high_price * (1.0 - callback_rate))
            close_bool = (close < avg_price * (1.0 - profit_rate)) and (close > low_price * (1.0 + rebound_rate))
            # 逻辑
            if close_bool:
                self.close_buy(close, ntime)
                index = 0
                pre_price = df.iloc[0]["close"]
                high_price = close
                sell_list = []
                avg_price = np.nan
            elif open_bool:
                trade_num = self.open_sell(close, ntime, trade_usdt=self.trade_usdt * pow(2, index))
                index += 1
                pre_price = close
                low_price = close
                sell_list.append([close, trade_num])
                sell_arr = np.array(sell_list)
                avg_price = (sell_arr[:, 0] * sell_arr[:, 1]).sum() / sell_arr[:, 1].sum()
                if index > max_index: max_index = index
            """ 逻辑END """

            # 净值曲线
            usd = self.usdt_num + self.eth_num * close
            money_result.append(usd)
            # 统计月化收益
            self.tj_month(ntime, usd)

        """ 其他 """
        print("最大索引值：", max_index)

        return money_result


def run():
    init_time = time.time()
    bt = DBackTest()
    bt.__init__(usdt_num=30000.0, trade_usdt=300.0, rate=0.001)
    bt.order_bool = True
    kd = kline_data.KlineData()
    df = kd.return_df(symbol="BNBUSDT", interval="1m", s="2020-07-12 00:00:00", e="2021-07-12 00:00:00")
    # 突破、回调、盈利、反弹
    bt.test(df, [0.02, 0.005, 0.015, 0.005])
    print("回测耗时：", time.time() - init_time)
    bt.cap_show()


if __name__ == '__main__':
    run()
