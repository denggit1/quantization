# coding:utf-8
# @Time    : 2018-12
# @Author  : D

"""
策略回测实现模板
"""

import time
import matplotlib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from multiprocessing import Process, Lock, Manager
import KlineData as kline_data
from pandas.plotting import register_matplotlib_converters


class BackTest(object):
    def __init__(self, eth_num=0.0, usdt_num=30000.0, trade_usdt=30000.0, rate=0.001, slippage=0.0,
                 trade_count=0, status=0, sign='0', maximum=0.0):
        # 货币数目， 法币数目， 开仓数目， 手续费率， 滑点， 交易次数， 仓位状态， 信号状态， 最大回撤金额， 订单
        self.eth_num = eth_num
        self.usdt_num = usdt_num
        self.default_usdt = usdt_num
        self.trade_usdt = trade_usdt
        self.rate = rate
        self.slippage = slippage
        self.trade_count = trade_count
        self.status = status
        self.sign = sign
        self.maximum = maximum
        self.orders = []
        self.win_rate = 0
        self.continuity_loss = 0
        self.moneyResult = []
        self.timeResult = []
        self.bondResult = []
        self.bond = 0
        self.cypair = 'none'
        self.mr = []
        self.mr_time = []
        self.open_list = []
        self.max_usdt = 0.0
        self.min_usdt = usdt_num
        self.ct = False
        self.pre = ["100001", self.default_usdt]
        self.month_list = []
        self.order_bool = True
        self.print_bool = True

    def close_buy(self, price, nTime):
        # 空仓平仓, price: float
        self.bond = 0
        old_ethNum = abs(self.eth_num)
        self.usdt_num += self.eth_num * round(price + self.slippage, 6) * (1 + self.rate)
        self.eth_num = 0.0
        # 修改信息
        self.trade_count += 1
        self.status = 0
        # 添加订单
        self.orders.append(
            ['close_buy', nTime[:-2] + '00', round(price + self.slippage, 6),
             old_ethNum, self.eth_num, self.usdt_num, self.eth_num + self.usdt_num / price,
             self.usdt_num + self.eth_num * price])
        self.mr.append(self.usdt_num + self.eth_num * price)
        self.mr_time.append(nTime[:-2] + '00')

    def open_buy(self, price, nTime):
        # 多仓开仓, price: float
        self.bond += self.trade_usdt
        self.usdt_num -= self.trade_usdt
        self.eth_num += self.trade_usdt / round(price + self.slippage, 6) * (1 - self.rate)
        # 修改信息
        self.trade_count += 1
        self.status = 1
        # 添加订单
        self.orders.append(
            ['open_buy', nTime[:-2] + '01', round(price + self.slippage, 6),
             self.trade_usdt / round(price + self.slippage, 6) * (1 - self.rate),
             self.eth_num, self.usdt_num, self.eth_num + self.usdt_num / price,
             self.usdt_num + self.eth_num * price])
        self.mr.append(self.usdt_num + self.eth_num * price)
        self.mr_time.append(nTime[:-2] + '01')
        self.open_list = ["open_buy", price]

    def close_sell(self, price, nTime):
        # 多仓平仓, price: float
        self.bond = 0
        old_ethNum = abs(self.eth_num)
        self.usdt_num += self.eth_num * round(price - self.slippage, 6) * (1 - self.rate)
        self.eth_num = 0.0
        # 修改信息
        self.trade_count += 1
        self.status = 0
        # 添加订单
        self.orders.append(
            ['close_sell', nTime[:-2] + '00', round(price - self.slippage, 6),
             old_ethNum, self.eth_num, self.usdt_num, self.eth_num + self.usdt_num / price,
             self.usdt_num + self.eth_num * price])
        self.mr.append(self.usdt_num + self.eth_num * price)
        self.mr_time.append(nTime[:-2] + '00')

    def open_sell(self, price, nTime):
        # 空仓开仓, price: float, nTime: str
        self.bond += self.trade_usdt
        self.usdt_num += self.trade_usdt
        self.eth_num -= self.trade_usdt / round(price - self.slippage, 6) * (1 + self.rate)
        # 修改信息
        self.trade_count += 1
        self.status = -1
        # 添加订单
        self.orders.append(
            ['open_sell', nTime[:-2] + '01', round(price - self.slippage, 6),
             self.trade_usdt / round(price - self.slippage, 6) * (1 + self.rate),
             self.eth_num, self.usdt_num, self.eth_num + self.usdt_num / price,
             self.usdt_num + self.eth_num * price])
        self.mr.append(self.usdt_num + self.eth_num * price)
        self.mr_time.append(nTime[:-2] + '01')
        self.open_list = ["open_sell", price]

    def tj_month(self, ntime, usdt):
        # 统计月化收益
        if ntime[-8:] == "01075900":
            self.month_list.append([self.pre[0], (usdt - self.pre[1]) / self.default_usdt])
        elif ntime[-8:] == "01080000":
            self.pre = [ntime[:6], usdt]
        self.timeResult.append(ntime)

    def trade_test(self, data, n_list):
        """
        回测计算函数
        :param data: 数据
        :param n_list: 参数列表
        :return: 资金曲线
        """
        # n_1, n_2
        n_1 = n_list[0]
        n_2 = n_list[1]
        # 回测计算
        priceList = np.array([float(temp[4]) for temp in data[:n_1]])
        moneyResult = []
        for i in range(n_1, len(data)):
            # 坐标定位 >> n_1
            priceList = np.append(priceList, float(data[i][4]))
            priceList = np.delete(priceList, 0)
            # 标准差
            std = priceList.std()
            zh = priceList.mean()
            sh = zh + n_2 * std
            xh = zh - n_2 * std
            # 判断交易方向
            if self.status == 0:
                # 上穿布林带
                if priceList[-1] > sh:
                    self.open_buy(priceList[-1], data[i][0])
                # 下穿布林带
                elif priceList[-1] < xh:
                    self.open_sell(priceList[-1], data[i][0])
            elif self.status == 1:
                # 下穿布林带
                if priceList[-1] < xh:
                    self.close_sell(priceList[-1], data[i][0])
                    self.open_sell(priceList[-1], data[i][0])
            elif self.status == -1:
                # 上穿布林带
                if priceList[-1] > sh:
                    self.close_buy(priceList[-1], data[i][0])
                    self.open_buy(priceList[-1], data[i][0])
            # 资金
            usdt = self.usdt_num + self.eth_num * priceList[-1]
            self.tj_month(data[i][0], usdt)
            moneyResult.append(usdt)
        return moneyResult

    def write_order(self):
        # 订单写入到桌面
        if self.order_bool:
            with open(r"C:\Users\Administrator\Desktop\order.csv", "w") as f:
                f.write("\n".join([",".join([str(temp) for temp in each]) for each in self.orders]))

    def test(self, data, n_list):
        # v1.1 新功能，定义初始月
        try: self.pre = [data.iloc[0]["ntime"][:6], self.default_usdt]
        except: self.pre = [data[0][0][:6], self.default_usdt]
        # 回测计算
        moneyResult = self.trade_test(data, n_list)
        # 计算最大回撤
        # 结束位置
        i = np.argmax(
            (np.maximum.accumulate(moneyResult) - moneyResult))
        # 开始位置
        try:
            j = np.argmax(moneyResult[:i])
        except:
            j = i
        self.maximum = moneyResult[int(j)] - moneyResult[int(i)]
        # 计算最大回撤
        money = np.array(self.mr)
        # 结束位置
        try:
            i = np.argmax(
                (np.maximum.accumulate(money) - money))
        except:
            i = 0
        # 开始位置
        try:
            j = np.argmax(money[:i])
        except:
            j = i
        try:
            self.max_mr = money[int(j)] - money[int(i)]
        except:
            self.max_mr = 0.1
        # 结束位置
        if self.print_bool:
            try:
                print("数据起点：", data[0])
                print("数据终点：", data[-1])
            except:
                print("数据起点：", data.iloc[0]["ntime"], data.iloc[0]["close"])
                print("数据终点：", data.iloc[-1]["ntime"], data.iloc[-1]["close"])
            print("策略收益：", moneyResult[-1] - moneyResult[0])
            print("净值回撤：", self.maximum)
            print("结算回撤：", self.max_mr)
            print("月化数据：", np.array(self.month_list)[:, 1].astype(float))
        # 处理数据
        self.timeResult = pd.to_datetime(pd.Series(self.timeResult), format="%Y%m%d%H%M%S")
        self.mr_time = pd.to_datetime(pd.Series(self.mr_time), format="%Y%m%d%H%M%S")
        # 计算
        self.compute_orders()
        self.write_order()
        self.moneyResult = np.array(moneyResult)

    def ht_cap(self):
        register_matplotlib_converters()
        # 绘图
        i = 1
        matplotlib.rcParams['font.family'] = 'STSong'

        plt.figure(i)
        plt.plot(self.timeResult, self.moneyResult)
        i += 1
        plt.title("净值曲线")

        plt.figure(i)
        plt.plot(self.mr_time, self.mr)
        i += 1
        plt.title("资金曲线")

        plt.figure(i)
        plt.plot(self.mr)
        i += 1
        plt.title("顺序结算")

        plt.figure(i)
        x = np.array(self.month_list)[:, 0].astype(str)
        y = np.array(self.month_list)[:, 1].astype(float)
        plt.bar(x, y)
        for a, b in zip(x, y):
            plt.text(a, b - 0.02 if b < 0 else b + 0.01, '%.2f' % (b * 100.0) + "%",
                     ha='center', va='bottom', fontsize=8)
        i += 1
        plt.title("月化统计")

        return None

    def plt_show(self):
        plt.show()

    def cap_show(self):
        self.ht_cap()
        self.plt_show()

    def compute_orders(self):
        # 计算订单胜率、连续亏损次数
        orders_list = self.orders
        gainVol = 0
        lossVol = 0
        # 临时变量、连续亏损次数
        loss_temporary_count = 0
        loss_count = 0
        for i in range(len(orders_list)):
            if orders_list[i][0] == 'close_sell':
                if orders_list[i - 1][2] < orders_list[i][2]:
                    gainVol += 1
                    loss_temporary_count = 0
                else:
                    lossVol += 1
                    loss_temporary_count += 1
                    if loss_temporary_count > loss_count:
                        loss_count = loss_temporary_count
            elif orders_list[i][0] == 'close_buy':
                if orders_list[i - 1][2] > orders_list[i][2]:
                    gainVol += 1
                    loss_temporary_count = 0
                else:
                    lossVol += 1
                    loss_temporary_count += 1
                    if loss_temporary_count > loss_count:
                        loss_count = loss_temporary_count
        if gainVol + lossVol == 0:
            self.win_rate = 0
        else:
            self.win_rate = gainVol / (gainVol + lossVol)
        self.continuity_loss = loss_count


def run(n_list):
    # 单策略回测
    bt = BackTest()
    m_list = ['201901', '202001']
    s = time.strftime('%Y%m%d%H%M%S', time.localtime(
        time.mktime(time.strptime(m_list[0] + '01080000', '%Y%m%d%H%M%S')) - (n_list[0] - 1) * 60))
    e = m_list[1] + '01080000'
    data = []
    bt.test(data, n_list)
    len_mon = len(bt.moneyResult)
    plt.plot(range(len_mon), bt.moneyResult)
    plt.xticks(range(0, len_mon, len_mon // 12), ['1812', '1901', '1902', '1903', '1904', '1905',
                                                  '1906', '1907', '1908', '1909', '1910', '1911'])
    plt.show()


def get_cap_df(symbol, cap_list, lock, lock2):
    bt = BackTest()
    bt.__init__(usdt_num=30000.0, trade_usdt=30000.0, rate=0.001)
    kd = kline_data.KlineData()
    lock2.acquire()
    df = kd.return_df(symbol=symbol, interval="1m", s="2021-04-12 00:00:00", e="2021-07-12 00:00:00")
    lock2.release()
    data = df[["ntime", "open", "high", "low", "close"]].values
    bt.test(data, [0.021, 0.022, 0.077])
    lock.acquire()
    cap_df = pd.DataFrame(bt.moneyResult, index=bt.timeResult, columns=[symbol])
    cap_list.append(cap_df)
    lock.release()


def mul_more_run(plt_bool=True):
    # 多线程组合回测函数，寻优可由此函数变更
    cap_list, lock, lock2 = Manager().list(), Lock(), Lock()
    process_list = [Process(target=get_cap_df, args=("ETHUSDT", cap_list, lock, lock2)),
                    Process(target=get_cap_df, args=("BNBUSDT", cap_list, lock, lock2))]
    for p in process_list: p.start()
    for p in process_list: p.join()
    new_df = cap_list[0].join(cap_list[1:], how='inner')
    new_df["SUM"] = new_df.apply(lambda x: x.sum(), axis=1)
    # 计算回撤
    i = np.argmax((np.maximum.accumulate(new_df["SUM"]) - new_df["SUM"]))
    try: j = np.argmax(new_df["SUM"][:i])
    except: j = i
    print(j, i)
    print("收益", new_df["SUM"][-1] - new_df["SUM"][0])
    print("回撤", new_df["SUM"][j] - new_df["SUM"][i])
    if plt_bool:
        plt.figure(1)
        plt.plot(new_df.index, new_df["SUM"])
        plt.show()


if __name__ == '__main__':
    run([10000, 2])
