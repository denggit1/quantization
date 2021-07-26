# coding:utf-8
# @Time    : 2019-12
# @Author  : D

import BackTestApi
import time
import numpy as np
import matplotlib.pyplot as plt


# 回测对象
class DBackTest(BackTestApi.BackTest):
    # 获取开平四价
    def get_four_price(self, kline_data, de_num, up_rate, dn_rate, boll_a, boll_b):
        # 计算布林指标
        data = np.array(kline_data[-boll_a:])[:, 4]
        dif = data.std() * boll_b
        mid = data.mean()
        up, dn = mid + dif, mid - dif
        # 多单价格 < min(上轨 - Do *（上轨-下轨）- DE, 1 - DE, 下轨)
        open_buy_price = min(up - dn_rate * (up - dn) - de_num, 1.0 - de_num, dn)
        # 多单平仓价格 = 上轨 - Do *（上轨-下轨）
        close_sell_price = up - dn_rate * (up - dn)
        # 空单价格 > max(下轨 + UP *（上轨-下轨）+ DE, 1 + DE，上轨)
        open_sell_price = max(dn + up_rate * (up - dn) + de_num, 1.0 + de_num, up)
        # 空单平仓价格 = 下轨 + UP *（上轨-下轨）
        close_buy_price = dn + up_rate * (up - dn)
        return open_buy_price, close_sell_price, open_sell_price, close_buy_price

    # 回测
    def trade_test(self, data, n_list):
        # 参数
        de_num = 0.001
        up_rate, dn_rate = 0.25, 0.25
        boll_a, boll_b = 90, 1.9
        # 小时聚合
        hour_kline = []
        open_buy_price, close_sell_price, open_sell_price, close_buy_price = None, None, None, None
        # 回测计算
        moneyResult, self.timeResult = [], []
        for i in range(len(data)):
            # 数据充足时
            if len(hour_kline) >= boll_a:
                ntime, open, high, low, close = data[i][0], float(data[i][1]), float(data[i][2]), \
                                                float(data[i][3]), float(data[i][4])
                if self.status == 1:
                    if high > close_sell_price:
                        self.close_sell(close_sell_price, ntime)
                elif self.status == -1:
                    if low < close_buy_price:
                        self.close_buy(close_buy_price, ntime)
                else:
                    if low < open_buy_price:
                        self.open_buy(open_buy_price, ntime)
                    elif high > open_sell_price:
                        self.open_sell(open_sell_price, ntime)
                # usdt
                usdt = self.usdt_num + self.eth_num * float(data[i][4])
                moneyResult.append(usdt)
                self.timeResult.append(data[i][0])
            # 小时聚合
            if data[i][0][-4:] == "5900":
                # 数据
                temp_arr = np.array(data[i + 1 - 60: i + 1]).astype(float)
                hour_kline.append([
                    temp_arr[0][0], temp_arr[0][1], temp_arr[:, 2].max(), temp_arr[:, 3].min(), temp_arr[-1][4]
                ])
                if len(hour_kline) >= boll_a:
                    # 计算
                    open_buy_price, close_sell_price, open_sell_price, close_buy_price = self.get_four_price(
                        hour_kline, de_num, up_rate, dn_rate, boll_a, boll_b
                    )
        return moneyResult


# 主函数
def main():
    tt = '080000'
    bt = DBackTest()
    m_list = ['202101', '202105']
    s = time.strftime('%Y%m%d%H%M%S', time.localtime(
        time.mktime(time.strptime(m_list[0] + '01' + tt, '%Y%m%d%H%M%S')) - 90 * 3600))
    e = m_list[1] + '01' + tt
    bt.__init__(usdt_num=1000000.0, trade_usdt=1000000.0, rate=0.0001)
    data = bt.db(cycle=1, startTime=s, endTime=e, cypair="usdcusdt", table_name='bi_an')
    print(data[0], data[-1], bt.cypair)
    bt.test(data, [])
    money = np.array(bt.moneyResult)
    # write
    with open(r"C:\Users\Administrator\Desktop\order.csv", "w") as f:
        f.write("\n".join([",".join([str(temp) for temp in each]) for each in bt.orders]))
    with open(r"C:\Users\Administrator\Desktop\result.txt", "w") as f:
        f.write("{}\n{}".format(str(money.tolist()), str(bt.timeResult)))
    print(money[-1] - money[0], bt.maximum)
    len_mon = len(money)
    plt.figure(1)
    plt.plot(money)
    plt.xticks(range(0, len_mon, len_mon // 24), ['19y03', '19y04', '19y05',
                                                  '19y06', '19y07', '19y08',
                                                  '19y09', '19y10', '19y11',
                                                  '19y12', '20y01', '20y02',
                                                  '20y03', '20y04', '20y05',
                                                  '20y06', '20y07', '20y08',
                                                  '20y09', '20y10', '20y11',
                                                  '20y12', '21y01', '21y02', '21y03'])
    plt.figure(2)
    moneyResult = bt.mr
    plt.plot(moneyResult)
    plt.xticks(range(0, len(moneyResult), len(moneyResult) // 24), ['2019-03-01', '2019-04-01', '2019-05-01',
                                                                    '2019-06-01', '2019-07-01', '2019-08-01',
                                                                    '2019-09-01', '2019-10-01', '2019-11-01',
                                                                    '2019-12-01', '2020-01-01', '2020-02-01',
                                                                    '2020-03-01', '2020-04-01', '2020-05-01',
                                                                    '2020-06-01', '2020-07-01', '2020-08-01',
                                                                    '2020-09-01', '2020-10-01', '2020-11-01',
                                                                    '2020-12-01', '2021-01-01', '2021-02-01'])
    i = np.argmax(
        (np.maximum.accumulate(moneyResult) - moneyResult))
    # 开始位置
    try:
        j = np.argmax(moneyResult[:i])
    except:
        j = i
    maximum = moneyResult[int(j)] - moneyResult[int(i)]
    print(maximum)
    plt.show()


if __name__ == '__main__':
    main()
