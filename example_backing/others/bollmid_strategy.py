# coding:utf-8
# @Time    : 2019-06
# @Author  : D

import pymysql
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


class BackTest(object):
    def __init__(self, eth_num=0.0, usdt_num=30000.0, trade_usdt=30000.0, rate=0.0006, slippage=0.0,
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
        self.bondResult = []
        self.bond = 0
        self.cypair = 'none'
        self.mr = []
        self.open_list = []
        self.max_usdt = 0.0
        self.min_usdt = usdt_num
        self.ct = False

    # 数据库数据，参数分钟线（默认1分钟线）
    def db(self, cycle=1, startTime='20191216080000', endTime='20191217080000',
           cypair='ethusdt', table_name='ioc', dbPwd='mysql'):
        conn = pymysql.connect(host="127.0.0.1", port=3306, user='root', passwd=dbPwd, db='test')
        cur = conn.cursor()
        sql = 'select ntime,`open`,high,low,`close` from ' + table_name + ' where cyPair=%s AND ntime>=' + startTime + \
              ' AND ntime<' + endTime + ' ORDER BY ntime ASC;'
        cur.execute(sql, cypair)
        oldData = cur.fetchall()
        data = []
        for i in range(0, len(oldData), cycle):
            temp_arr = np.array(oldData[i: i + cycle])
            temp_time = temp_arr[0][0]
            temp_open = temp_arr[0][1]
            temp_high = temp_arr[:, 2].astype(float).max()
            temp_low = temp_arr[:, 3].astype(float).min()
            temp_close = temp_arr[-1][-1]
            data.append([temp_time, temp_open, temp_high, temp_low, temp_close])
        conn.close()
        self.cypair = cypair
        return data

    def db2(self, cycle=1, startTime='20191216080000', endTime='20191217080000',
            cypair='ethusdt', table_name='ioc', dbPwd='mysql'):
        df = pd.read_csv(r"C:\Users\Administrator\Desktop\data\{}.csv".format(cypair))
        df = df[df["time"] > "2021-01-01 00:00:00"]
        df["time"] = pd.to_datetime(df["time"], format="%Y-%m-%d %H:%M:%S")
        df.set_index("time", inplace=True)
        df["N-C"] = (df["dapi_next"] - df["dapi_current"]) / (df["dapi_next"] + df["dapi_current"]) * 2
        # tohlc
        df["time"] = df.index.strftime('%Y%m%d%H%M%S')
        df["open"] = df["N-C"]
        df["high"] = df["N-C"]
        df["low"] = df["N-C"]
        df["close"] = df["N-C"]
        df = df[["time", "open", "high", "low", "close", "N-C"]]
        oldData = df.values.tolist()
        data = []
        for i in range(0, len(oldData), cycle):
            temp_arr = np.array(oldData[i: i + cycle])
            temp_time = temp_arr[0][0]
            temp_open = temp_arr[0][1]
            temp_high = temp_arr[:, 2].astype(float).max()
            temp_low = temp_arr[:, 3].astype(float).min()
            temp_close = temp_arr[-1][-1]
            data.append([temp_time, temp_open, temp_high, temp_low, temp_close])
        self.cypair = cypair
        return data

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
        self.open_list = ["open_sell", price]

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
        pre = ["200001", 30000.0]
        self.month_list = []
        priceList = np.array([float(temp[4]) for temp in data[:n_1]])
        moneyResult = []
        self.timeResult = []
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
                if priceList[-1] < zh:
                    self.close_sell(priceList[-1], data[i][0])
            elif self.status == -1:
                # 上穿布林带
                if priceList[-1] > zh:
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

    def test(self, data, n_list):
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
        i = np.argmax(
            (np.maximum.accumulate(money) - money))
        # 开始位置
        try:
            j = np.argmax(money[:i])
        except:
            j = i
        self.max_mr = money[int(j)] - money[int(i)]
        # 结束位置
        self.compute_orders()
        self.moneyResult = moneyResult

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


def run():
    # 19, 0.04, 0.0045, 0.04, 0.23 - BSV-USD-SWAP ok_swap
    symbol = "BTCUSDT"
    n_list = [5000, 2]
    print(symbol, n_list)
    # ###
    tt = '080000'
    bt = BackTest()
    m_list = ['202001', '202105']
    s = time.strftime('%Y%m%d%H%M%S', time.localtime(
        time.mktime(time.strptime(m_list[0] + '01' + tt, '%Y%m%d%H%M%S')) - n_list[0] * 60))
    e = m_list[1] + '27' + tt
    bt.__init__(usdt_num=30000.0, rate=0.0006)
    data = bt.db(cycle=1, startTime=s, endTime=e, cypair=symbol, table_name='bi_an')
    print(data[0], data[-1], bt.cypair)
    bt.test(data, n_list)
    money = np.array(bt.moneyResult)
    print(len(money))
    """ 组合开启 """
    """ 组合结束 """
    # write
    with open(r"C:\Users\Administrator\Desktop\order.csv", "w") as f:
        f.write("\n".join([",".join([str(temp) for temp in each]) for each in bt.orders]))
    with open(r"C:\Users\Administrator\Desktop\result.txt", "w") as f:
        f.write("{}\n{}".format(str(money.tolist()), str(bt.timeResult)))
    print(money[-1] - money[0], bt.maximum)
    len_mon = len(money)
    plt.figure(1)
    plt.plot(money)
    plt.xticks(range(0, len_mon, len_mon // 12), ['1901', '1902', '1903', '1904', '1905', '1906',
                                                  '1907', '1908', '1909', '1910', '1911', '1912'])
    plt.figure(2)
    moneyResult = bt.mr
    plt.plot(moneyResult)
    i = np.argmax(
        (np.maximum.accumulate(moneyResult) - moneyResult))
    # 开始位置
    try:
        j = np.argmax(moneyResult[:i])
    except:
        j = i
    maximum = moneyResult[int(j)] - moneyResult[int(i)]
    print(maximum)
    # plt.figure(3)
    # x = np.array(bt.month_list)[:, 0].astype(str)
    # y = np.array(bt.month_list)[:, 1].astype(float)
    # plt.bar(x, y)
    # for a, b in zip(x, y):
    #     plt.text(a, b - 0.02 if b < 0 else b + 0.01, '%.2f' % (b * 100.0) + "%", ha='center', va='bottom', fontsize=8)
    # print(y.tolist())
    plt.show()


if __name__ == '__main__':
    run()
