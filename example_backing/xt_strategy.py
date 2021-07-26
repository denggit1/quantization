# coding:utf-8
# @Time    : 2020-04
# @Author  : D

"""
策略：
    突破百分比
"""

import BackTestApi
import time
import numpy as np
import matplotlib.pyplot as plt


# 回测对象
class DBackTest(BackTestApi.BackTest):
    def trade_test(self, data, n_list):
        # 箱线数目 箱体限制 离开箱体
        boll_a = n_list[0]
        price_rate = n_list[1]
        leave_rate = n_list[2]
        # 止损止盈
        los_rate = n_list[3]
        win_rate = n_list[4]
        # 小时聚合
        hour_kline = []
        box_max, high_v, low_v = None, None, None
        offset = False
        open_price = None
        # 回测计算
        pre = ["200001", 30000.0]
        self.month_list = []
        moneyResult, self.timeResult = [], []
        for i in range(len(data)):
            # 数据充足时
            if len(hour_kline) >= boll_a:
                ntime, open, high, low, close = data[i][0], float(data[i][1]), float(data[i][2]), \
                                                float(data[i][3]), float(data[i][4])
                # 持多单时
                if self.status == 1:
                    # 当前价格 小于 Low_V*（1-离开箱体波动）：平多开空  -  BoxMax 小于 价格*百分比
                    if close < low_v * (1.0 - leave_rate) and box_max < low_v * price_rate and offset:
                        open_price = low_v * (1.0 - leave_rate)
                        # print(ntime, close, open_price, "\t\t{:.2f}%".format(200 * abs(close - open_price) / (close + open_price)))
                        self.close_sell(open_price, ntime)
                        self.open_sell(open_price, ntime)
                    else:
                        win_price = open_price * (1.0 + win_rate)
                        los_price = open_price * (1.0 - los_rate)
                        if low <= los_price:
                            self.close_sell(los_price, ntime)
                            open_price = None
                            offset = False
                        elif high >= win_price:
                            self.close_sell(win_price, ntime)
                            open_price = None
                            offset = False
                # 持空单时
                elif self.status == -1:
                    # 当前价格 大于 High_V*（1+离开箱体波动）：平空开多  -  BoxMax 小于 价格*百分比
                    if close > high_v * (1.0 + leave_rate) and box_max < high_v * price_rate and offset:
                        open_price = high_v * (1.0 + leave_rate)
                        # print(ntime, close, open_price, "\t\t{:.2f}%".format(200 * abs(close - open_price) / (close + open_price)))
                        self.close_buy(open_price, ntime)
                        self.open_buy(open_price, ntime)
                    else:
                        win_price = open_price * (1.0 - win_rate)
                        los_price = open_price * (1.0 + los_rate)
                        if high >= los_price:
                            self.close_buy(los_price, ntime)
                            open_price = None
                            offset = False
                        elif low <= win_price:
                            self.close_buy(win_price, ntime)
                            open_price = None
                            offset = False
                # 持平单时
                else:
                    # 当前价格 大于 High_V*（1+离开箱体波动）：开多  -  BoxMax 小于 价格*百分比
                    if close > high_v * (1.0 + leave_rate) and box_max < high_v * price_rate and offset:
                        open_price = high_v * (1.0 + leave_rate)
                        # print(ntime, close, open_price, "\t\t{:.2f}%".format(200 * abs(close - open_price) / (close + open_price)))
                        self.open_buy(open_price, ntime)
                    # 当前价格 小于 Low_V*（1-离开箱体波动）：开空  -  BoxMax 小于 价格*百分比
                    elif close < low_v * (1.0 - leave_rate) and box_max < low_v * price_rate and offset:
                        open_price = low_v * (1.0 - leave_rate)
                        # print(ntime, close, open_price, "\t\t{:.2f}%".format(200 * abs(close - open_price) / (close + open_price)))
                        self.open_sell(open_price, ntime)
                # usdt
                usdt = self.usdt_num + self.eth_num * float(data[i][4])
                moneyResult.append(usdt)
                self.timeResult.append(data[i][0])
                # 统计月化收益
                if data[i][0][-8:] == "01075900":
                    self.month_list.append([pre[0], (usdt - pre[1]) / 30000.0])
                elif data[i][0][-8:] == "01080000":
                    pre = [data[i][0][:6], usdt]
            # 小时聚合
            if data[i][0][-4:] == "5900":
                # 数据
                temp_arr = np.array(data[i + 1 - 60: i + 1]).astype(float)
                hour_kline.append([
                    temp_arr[0][0], temp_arr[0][1], temp_arr[:, 2].max(), temp_arr[:, 3].min(), temp_arr[-1][4]
                ])
                if len(hour_kline) >= boll_a:
                    # High_V = 第1小时到36小时的最高点 （不包含当前小时）
                    high_v = np.array(hour_kline[-boll_a:])[:, 4].max()
                    # Low_V = 第1小时到36小时的最低点  （不包含当前小时）
                    low_v = np.array(hour_kline[-boll_a:])[:, 4].min()
                    # BoxMax = High_V-Low_V;
                    box_max = high_v - low_v
                    offset = True
        return moneyResult


# 主函数
def main():
    # 19, 0.04, 0.0045, 0.04, 0.23 - BSV-USD-SWAP ok_swap
    symbol = "ethusdt"
    n_list = [50, 0.05, 0.0045, 0.04, 0.23]
    # ###
    tt = '080000'
    bt = DBackTest()
    m_list = ['202009', '202104']
    s = time.strftime('%Y%m%d%H%M%S', time.localtime(
        time.mktime(time.strptime(m_list[0] + '01' + tt, '%Y%m%d%H%M%S')) - n_list[0] * 3600))
    e = m_list[1] + '20' + tt
    bt.__init__(usdt_num=30000.0, trade_usdt=30000.0, rate=0.001)
    data = bt.db(cycle=1, startTime=s, endTime=e, cypair=symbol, table_name='bi_an')
    print(data[0], data[-1], bt.cypair)
    bt.test(data, n_list)
    money = np.array(bt.moneyResult)
    print(len(money))
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
    plt.figure(3)
    x = np.array(bt.month_list)[:, 0].astype(str)
    y = np.array(bt.month_list)[:, 1].astype(float)
    plt.bar(x, y)
    for a, b in zip(x, y):
        plt.text(a, b - 0.02 if b < 0 else b + 0.01, '%.2f' % (b * 100.0) + "%", ha='center', va='bottom', fontsize=8)
    print(y.tolist())
    plt.show()


if __name__ == '__main__':
    main()
