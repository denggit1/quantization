# coding:utf-8
# @Time    : 2021-05
# @Author  : D

"""
获取 K线 bar 数据
"""

import time
import requests
import pandas as pd
from threading import Thread, Lock, BoundedSemaphore


class KlineData(object):
    def __init__(self):
        self.symbol = "BTCUSDT"
        self.interval = "1m"
        self.max_limit = 2108
        self.kline_count = 0
        self.minute = None
        self.limit_bool = True

    def get_kline(self, stime, data_list, lock, pool_sema):
        # 参数
        stime = int(stime)
        params = {"symbol": self.symbol, "interval": self.interval, "limit": 499,
                  "startTime": stime, "endTime": stime + (499 - 1) * 60 * 1000}
        # 多线程控制
        pool_sema.acquire()
        while True:
            try:
                # 请求及数据处理
                res = requests.get("http://fapi.binance.com/fapi/v1/klines", params=params, timeout=5)
                lock.acquire()
                data_list += res.json()
                self.kline_count -= 1
                lock.release()
                # print("数据范围，左开右闭", res.json()[0][0], res.json()[-1][0] + 60 * 1000)
                # 输出显示
                minute = time.strftime("%M")
                if self.minute != minute:
                    self.minute = minute
                    print(time.strftime("%Y-%m-%d %H:%M:%S"),
                          self.symbol, self.interval, "剩余请求次数:", self.kline_count)
                # 限频处理
                if int(res.headers.get("X-MBX-USED-WEIGHT-1m")) > self.max_limit:
                    sleep_time = time.time() // 60 * 60 + 60 - time.time()
                    if self.limit_bool:
                        self.limit_bool = False
                        print(time.strftime("%Y-%m-%d %H:%M:%S"),
                              "超出限频:", int(res.headers.get("X-MBX-USED-WEIGHT-1m")),
                              "休眠时间s：", int(sleep_time))
                    time.sleep(sleep_time)
                    self.limit_bool = True
                break
            except Exception as e: print(time.strftime("%Y-%m-%d %H:%M:%S"), "正在处理异常请求：", stime, e)
            time.sleep(1)
        pool_sema.release()

    def thread_kline(self, s="2021-07-10 00:00:00", e="2021-07-11 00:00:00"):
        # 数据与锁
        data_list, lock = [], Lock()
        # 时间转化时间戳
        stime = time.mktime(time.strptime(s, "%Y-%m-%d %H:%M:%S")) * 1000
        etime = time.mktime(time.strptime(e, "%Y-%m-%d %H:%M:%S")) * 1000
        # 线程数控制
        thread_list = []
        pool_sema = BoundedSemaphore(45)
        while stime < etime:
            thread_list.append(Thread(target=self.get_kline, args=(stime, data_list, lock, pool_sema)))
            stime += 499 * 60 * 1000
            self.kline_count += 1
        for t in thread_list: t.start()
        for t in thread_list: t.join()
        return data_list

    def return_df(self, symbol="BTCUSDT", interval="1m", s="2021-07-11 00:00:00", e="2021-07-12 00:00:00"):
        # 将品种与周期同步至此类中
        self.symbol = symbol
        self.interval = interval
        # 多线程获取数据
        data = self.thread_kline(s, e)
        df = pd.DataFrame(data, columns=[
            "open_time", "open", "high", "low", "close", "volume",
            "close_time", "amount", "number", "active_volume", "active_amount", "ignore"])
        # 毫秒转换
        df.index = pd.to_datetime(df["open_time"], unit="ms", utc=True)
        # 时区转换，增加time字符串
        df.index = df.index.tz_convert('Asia/Shanghai')
        df["ntime"] = df.index.strftime('%Y%m%d%H%M%S')
        # 时间序列排序
        df.sort_index(inplace=True)
        return df


if __name__ == '__main__':
    kd = KlineData()
    df = kd.return_df(symbol="BTCUSDT", interval="1m", s="2021-06-10 00:00:00", e="2021-06-11 00:00:00")
    print(df)
