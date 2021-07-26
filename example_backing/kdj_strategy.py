# coding:utf-8
# @Time    : 2021-07
# @Author  : D

"""
KDJ策略：
    K线上穿D线做多
    K线下穿D线做空
"""

from talib import _ta_lib as ta
import BackTestApi
import kline_data


class DBackTest(BackTestApi.BackTest):
    def trade_test(self, df, n_list):
        """ 参数、变量 """
        fastk_period = n_list[0]
        slowk_period = n_list[1]
        slowd_period = n_list[2]

        """ 指标计算 """
        df["slowk"], df["slowd"] = ta.STOCH(df["high"], df["low"], df["close"], fastk_period=fastk_period,
                                            slowk_period=slowk_period, slowd_period=slowd_period)
        # df["slowj"] = 3 * df["slowk"] - 2 * df["slowd"]

        """ 模拟回测 """
        money_result = []
        for i in range(len(df)):
            # 常量
            ntime = df.iloc[i]["ntime"]
            close = float(df.iloc[i]["close"])
            k = df.iloc[i]["slowk"]
            d = df.iloc[i]["slowd"]

            """ 逻辑START """
            if k and d:
                if self.status == 1:
                    if k < d:
                        self.close_sell(close, ntime)
                        self.open_sell(close, ntime)
                elif self.status == -1:
                    if k > d:
                        self.close_buy(close, ntime)
                        self.open_buy(close, ntime)
                else:
                    if k > d:
                        self.open_buy(close, ntime)
                    elif k < d:
                        self.open_sell(close, ntime)
            """ 逻辑END """

            # 净值曲线
            usd = self.usdt_num + self.eth_num * close
            money_result.append(usd)
            # 统计月化收益
            self.tj_month(ntime, usd)
        return money_result


def run():
    bt = DBackTest()
    bt.__init__(usdt_num=30000.0, trade_usdt=30000.0, rate=0.001)
    bt.order_bool = False
    kd = kline_data.KlineData()
    df = kd.return_df(symbol="ETHUSDT", interval="1m", s="2021-04-12 00:00:00", e="2021-07-12 00:00:00")
    bt.test(df, [0.021, 0.022, 0.077])
    bt.cap_show()


if __name__ == '__main__':
    run()
