# coding:utf-8
# @Time    : 2018-12
# @Author  : D

"""
策略参数寻优
"""

from json import loads
import time
from pathlib import Path
from multiprocessing import Process, Lock, Pool, cpu_count, Manager
import sys
import traceback
sys.path.append('D:\\test\\DateTimeDirs\\2021\\backing')
import KlineData as kline_data
# 选择策略
from kdj_strategy import DBackTest


class FindWin(object):
    def run2(self, name, for_count, lock, v, data, n_1, n_2, n_3):
        try:
            # 统计时间
            t1 = time.time()
            # 核心计算
            bt = DBackTest()
            bt.__init__(usdt_num=30000.0, trade_usdt=30000.0, rate=0.001)
            bt.print_bool = False
            bt.order_bool = False
            bt.test(data, [n_1, n_2, n_3])
            # 统计时间
            t2 = time.time()
            # 统计所有时间
            if not v.value: v.value = (t2 - t1) * for_count
            # 异常处理
            if bt.maximum == 0: bt.maximum = 0.1
            if bt.max_mr == 0: bt.max_mr = 0.1
            end_price = float(data.iloc[-1][4])
            test_list = [n_1, n_2, n_3,
                         bt.maximum,
                         bt.maximum / bt.default_usdt,
                         bt.usdt_num + bt.eth_num * end_price - bt.default_usdt,
                         (bt.usdt_num + bt.eth_num * end_price - bt.default_usdt) / bt.maximum,
                         bt.max_mr,
                         (bt.usdt_num + bt.eth_num * end_price - bt.default_usdt) / bt.max_mr,
                         bt.trade_count, bt.win_rate, bt.continuity_loss]
            del bt
        except Exception as e:
            t1, t2 = 0, 0
            test_list = []
            error = traceback.format_exc()
            # error = error.replace(" ", "").replace("\n", " ")
            print(e, error)
        # 锁
        lock.acquire()
        with open('0_{}.csv'.format(name), 'r') as f: t = f.read()
        with open('0_{}.csv'.format(name), 'w') as f: f.write(t + ','.join([str(x) for x in test_list]) + '\n')
        v.value -= (t2 - t1)
        lock.release()
        # 输出
        print(n_1, n_2, n_3, '本次耗时：', t2 - t1, '剩余耗时：%s分' % (v.value / 60.0))

    def run(self, name):
        # 读取
        with open("b_ini.txt", "r") as f:
            temp = f.read().split("\n")
        list_n1 = loads(temp[0])
        list_n2 = loads(temp[1])
        list_n3 = loads(temp[2])
        # 变量, 数据
        kd = kline_data.KlineData()
        data = kd.return_df(symbol=name, interval="1m", s="2021-01-01 00:00:00", e="2021-07-01 00:00:00")
        # 第一次循环计算次数
        with open('0_{}.csv'.format(name), 'w') as f:
            f.write('N1,N2,N3,最大回撤金额,回撤金额：本金,总盈亏法币数,'
                    '盈亏法币：回撤金额,结算单回撤,盈利：结算,买卖次数,总胜率,连续亏损最大次数\n')
        for_count = len(
            range(list_n1[0], list_n1[1] + 1, list_n1[2])) * len(
            range(list_n2[0], list_n2[1] + 1, list_n2[2])) * len(
            range(list_n3[0], list_n3[1] + 1, list_n3[2]))
        lock = Manager().Lock()
        v = Manager().Value("f", 0.0)
        print("CPU:", cpu_count())
        pool = Pool(processes=cpu_count()-1)
        # 主运算程序
        for n_1 in range(list_n1[0], list_n1[1] + 1, list_n1[2]):
            for n_2 in range(list_n2[0], list_n2[1] + 1, list_n2[2]):
                for n_3 in range(list_n3[0], list_n3[1] + 1, list_n3[2]):
                    pool.apply_async(self.run2, args=(name, for_count, lock, v, data, n_1, n_2, n_3))
        pool.close()
        pool.join()


if __name__ == '__main__':
    name = Path(__file__).name.split(".")[0]
    fw = FindWin()
    fw.run(name)
