# coding:utf-8
# https://github.com/HuaRongSAO/talib-document
# matype: 0=SMA, 1=EMA, 2=WMA, 3=DEMA, 4=TEMA, 5=TRIMA, 6=KAMA, 7=MAMA, 8=T3
# @Time    : 2019-10
# @Author  : D

import BackTestApi
# LIB
import talib
import numpy as np
import matplotlib.pyplot as plt
# API
# from . import BackTestApi


""" END 重叠研究 START """


# 布林带
class BBandsBackTest(BackTestApi.BackTest):
    def trade_test(self, data, n_list):
        # n_1, n_2
        n_1 = n_list[0]
        n_2 = n_list[1]
        # arr
        time_arr = np.array([temp[0] for temp in data])
        price_arr = np.array([float(temp[4]) for temp in data])
        # upperband, middleband, lowerband = BBANDS(close, timeperiod=5, nbdevup=2, nbdevdn=2, matype=0)
        up, mid, down = talib.BBANDS(price_arr, n_1, n_2, n_2)
        # his_time, up, mid, down, close
        data_arr = np.hstack((time_arr.reshape(-1, 1), up.reshape(-1, 1), mid.reshape(-1, 1), down.reshape(-1, 1),
                              price_arr.reshape(-1, 1)))
        moneyResult = []
        for each in data_arr:
            # str -> float
            his_time = each[0]
            close_price = float(each[-1])
            up = float(each[1])
            down = float(each[3])
            # 判断交易方向
            if self.status == 0:
                if close_price > up:
                    self.open_buy(close_price, his_time)
                elif close_price < down:
                    self.open_sell(close_price, his_time)
            elif self.status == 1:
                if close_price < down:
                    self.close_sell(close_price, his_time)
                    self.open_sell(close_price, his_time)
            elif self.status == -1:
                if close_price > up:
                    self.close_buy(close_price, his_time)
                    self.open_buy(close_price, his_time)
            # 资金曲线
            usdt = self.usdt_num + self.eth_num * close_price
            moneyResult.append(usdt)
        return moneyResult


# 单指数移动均线
class EmaBackTest(BackTestApi.BackTest):
    def trade_test(self, data, n_list):
        # n_1
        n_1 = n_list[0]
        # arr
        time_arr = np.array([temp[0] for temp in data])
        price_arr = np.array([float(temp[4]) for temp in data])
        # real = EMA(close, timeperiod=30)
        ema_arr = talib.EMA(price_arr, n_1)
        data_arr = np.hstack((time_arr.reshape(-1, 1), ema_arr.reshape(-1, 1), price_arr.reshape(-1, 1)))
        moneyResult = []
        for each in data_arr:
            # str -> float
            his_time = each[0]
            close_price = float(each[-1])
            ema = float(each[1])
            # 判断交易方向
            if self.status == 0:
                if close_price > ema:
                    self.open_buy(close_price, his_time)
                elif close_price < ema:
                    self.open_sell(close_price, his_time)
            elif self.status == 1:
                if close_price < ema:
                    self.close_sell(close_price, his_time)
                    self.open_sell(close_price, his_time)
            elif self.status == -1:
                if close_price > ema:
                    self.close_buy(close_price, his_time)
                    self.open_buy(close_price, his_time)
            # 资金曲线
            usdt = self.usdt_num + self.eth_num * close_price
            moneyResult.append(usdt)
        return moneyResult


# 双指数移动均线
class DEmaBackTest(BackTestApi.BackTest):
    def trade_test(self, data, n_list):
        # n_1
        n_1 = n_list[0]
        # arr
        time_arr = np.array([temp[0] for temp in data])
        price_arr = np.array([float(temp[4]) for temp in data])
        # real = DEMA(close, timeperiod=30)
        dema_arr = talib.DEMA(price_arr, n_1)
        data_arr = np.hstack((time_arr.reshape(-1, 1), dema_arr.reshape(-1, 1), price_arr.reshape(-1, 1)))
        moneyResult = []
        for each in data_arr:
            # str -> float
            his_time = each[0]
            close_price = float(each[-1])
            dema = float(each[1])
            # 判断交易方向
            if self.status == 0:
                if close_price > dema:
                    self.open_buy(close_price, his_time)
                elif close_price < dema:
                    self.open_sell(close_price, his_time)
            elif self.status == 1:
                if close_price < dema:
                    self.close_sell(close_price, his_time)
                    self.open_sell(close_price, his_time)
            elif self.status == -1:
                if close_price > dema:
                    self.close_buy(close_price, his_time)
                    self.open_buy(close_price, his_time)
            # 资金曲线
            usdt = self.usdt_num + self.eth_num * close_price
            moneyResult.append(usdt)
        return moneyResult


# 三指数移动均线
class TEmaBackTest(BackTestApi.BackTest):
    def trade_test(self, data, n_list):
        # n_1
        n_1 = n_list[0]
        # arr
        time_arr = np.array([temp[0] for temp in data])
        price_arr = np.array([float(temp[4]) for temp in data])
        # real = TEMA(close, timeperiod=30)
        tema_arr = talib.TEMA(price_arr, n_1)
        data_arr = np.hstack((time_arr.reshape(-1, 1), tema_arr.reshape(-1, 1), price_arr.reshape(-1, 1)))
        moneyResult = []
        for each in data_arr:
            # str -> float
            his_time = each[0]
            close_price = float(each[-1])
            tema = float(each[1])
            # 判断交易方向
            if self.status == 0:
                if close_price > tema:
                    self.open_buy(close_price, his_time)
                elif close_price < tema:
                    self.open_sell(close_price, his_time)
            elif self.status == 1:
                if close_price < tema:
                    self.close_sell(close_price, his_time)
                    self.open_sell(close_price, his_time)
            elif self.status == -1:
                if close_price > tema:
                    self.close_buy(close_price, his_time)
                    self.open_buy(close_price, his_time)
            # 资金曲线
            usdt = self.usdt_num + self.eth_num * close_price
            moneyResult.append(usdt)
        return moneyResult


# 希尔伯特瞬时变换
class HtTrendBackTest(BackTestApi.BackTest):
    def trade_test(self, data, n_list):
        # arr
        time_arr = np.array([temp[0] for temp in data])
        price_arr = np.array([float(temp[4]) for temp in data])
        # real = HT_TRENDLINE(close)
        trend_arr = talib.HT_TRENDLINE(price_arr)
        data_arr = np.hstack((time_arr.reshape(-1, 1), trend_arr.reshape(-1, 1), price_arr.reshape(-1, 1)))
        moneyResult = []
        for each in data_arr:
            # str -> float
            his_time = each[0]
            close_price = float(each[-1])
            trend = float(each[1])
            # 判断交易方向
            if self.status == 0:
                if close_price > trend:
                    self.open_buy(close_price, his_time)
                elif close_price < trend:
                    self.open_sell(close_price, his_time)
            elif self.status == 1:
                if close_price < trend:
                    self.close_sell(close_price, his_time)
                    self.open_sell(close_price, his_time)
            elif self.status == -1:
                if close_price > trend:
                    self.close_buy(close_price, his_time)
                    self.open_buy(close_price, his_time)
            # 资金曲线
            usdt = self.usdt_num + self.eth_num * close_price
            moneyResult.append(usdt)
        return moneyResult


# KAMA 自适应均线
class KamaBackTest(BackTestApi.BackTest):
    def trade_test(self, data, n_list):
        # n_1
        n_1 = n_list[0]
        # arr
        time_arr = np.array([temp[0] for temp in data])
        price_arr = np.array([float(temp[4]) for temp in data])
        # real = KAMA(close, timeperiod=30)
        kama_arr = talib.KAMA(price_arr, n_1)
        data_arr = np.hstack((time_arr.reshape(-1, 1), kama_arr.reshape(-1, 1), price_arr.reshape(-1, 1)))
        moneyResult = []
        for each in data_arr:
            # str -> float
            his_time = each[0]
            close_price = float(each[-1])
            kama = float(each[1])
            # 判断交易方向
            if self.status == 0:
                if close_price > kama:
                    self.open_buy(close_price, his_time)
                elif close_price < kama:
                    self.open_sell(close_price, his_time)
            elif self.status == 1:
                if close_price < kama:
                    self.close_sell(close_price, his_time)
                    self.open_sell(close_price, his_time)
            elif self.status == -1:
                if close_price > kama:
                    self.close_buy(close_price, his_time)
                    self.open_buy(close_price, his_time)
            # 资金曲线
            usdt = self.usdt_num + self.eth_num * close_price
            moneyResult.append(usdt)
        return moneyResult


# MaType 移动平均线
class MaBackTest(BackTestApi.BackTest):
    def trade_test(self, data, n_list):
        # n_1
        n_1 = n_list[0]
        # arr
        time_arr = np.array([temp[0] for temp in data])
        price_arr = np.array([float(temp[4]) for temp in data])
        # real = MA(close, timeperiod=30, matype=0)
        ma_arr = talib.MA(price_arr, n_1)
        data_arr = np.hstack((time_arr.reshape(-1, 1), ma_arr.reshape(-1, 1), price_arr.reshape(-1, 1)))
        moneyResult = []
        for each in data_arr:
            # str -> float
            his_time = each[0]
            close_price = float(each[-1])
            ma = float(each[1])
            # 判断交易方向
            if self.status == 0:
                if close_price > ma:
                    self.open_buy(close_price, his_time)
                elif close_price < ma:
                    self.open_sell(close_price, his_time)
            elif self.status == 1:
                if close_price < ma:
                    self.close_sell(close_price, his_time)
                    self.open_sell(close_price, his_time)
            elif self.status == -1:
                if close_price > ma:
                    self.close_buy(close_price, his_time)
                    self.open_buy(close_price, his_time)
            # 资金曲线
            usdt = self.usdt_num + self.eth_num * close_price
            moneyResult.append(usdt)
        return moneyResult


# MAMA 自适应均线
class MamaBackTest(BackTestApi.BackTest):
    def trade_test(self, data, n_list):
        # arr
        time_arr = np.array([temp[0] for temp in data])
        price_arr = np.array([float(temp[4]) for temp in data])
        # mama, fama = MAMA(close, fastlimit=0, slowlimit=0)
        mama, fama = talib.MAMA(price_arr)
        data_arr = np.hstack((time_arr.reshape(-1, 1), mama.reshape(-1, 1), fama.reshape(-1, 1),
                              price_arr.reshape(-1, 1)))
        moneyResult = []
        for each in data_arr:
            # str -> float
            his_time = each[0]
            close_price = float(each[-1])
            ma1 = float(each[1])
            ma2 = float(each[2])
            # 判断交易方向
            if self.status == 0:
                if close_price > ma1 and close_price > ma2:
                    self.open_buy(close_price, his_time)
                elif close_price < ma1 and close_price < ma2:
                    self.open_sell(close_price, his_time)
            elif self.status == 1:
                if close_price < ma1 and close_price < ma2:
                    self.close_sell(close_price, his_time)
                    self.open_sell(close_price, his_time)
            elif self.status == -1:
                if close_price > ma1 and close_price > ma2:
                    self.close_buy(close_price, his_time)
                    self.open_buy(close_price, his_time)
            # 资金曲线
            usdt = self.usdt_num + self.eth_num * close_price
            moneyResult.append(usdt)
        return moneyResult


# 抛物线指标
class SarBackTest(BackTestApi.BackTest):
    def trade_test(self, data, n_list):
        # n_1, n_2
        n_1 = n_list[0]
        n_2 = n_list[1]
        # arr
        time_arr = np.array([temp[0] for temp in data])
        price_arr = np.array([float(temp[4]) for temp in data])
        high_arr = np.array([float(temp[2]) for temp in data])
        low_arr = np.array([float(temp[3]) for temp in data])
        # real = SAR(high, low, acceleration=0, maximum=0)
        sar_arr = talib.SAR(high_arr, low_arr, n_1, n_2)
        data_arr = np.hstack((time_arr.reshape(-1, 1), sar_arr.reshape(-1, 1), price_arr.reshape(-1, 1)))
        moneyResult = []
        self.month_list = []
        pre = ["200001", 30000.0]
        for each in data_arr:
            # str -> float
            his_time = each[0]
            close_price = float(each[-1])
            sar = float(each[1])
            # 判断交易方向
            if self.status == 0:
                if close_price > sar:
                    self.open_buy(close_price, his_time)
                elif close_price < sar:
                    self.open_sell(close_price, his_time)
            elif self.status == 1:
                if close_price < sar:
                    self.close_sell(close_price, his_time)
                    self.open_sell(close_price, his_time)
            elif self.status == -1:
                if close_price > sar:
                    self.close_buy(close_price, his_time)
                    self.open_buy(close_price, his_time)
            # 资金曲线
            usdt = self.usdt_num + self.eth_num * close_price
            moneyResult.append(usdt)
            # 统计月化收益
            if each[0][-8:] == "01075900":
                self.month_list.append([pre[0], (usdt - pre[1]) / 30000.0])
            elif each[0][-8:] == "01080000":
                pre = [each[0][:6], usdt]
        return moneyResult


# 三重指数移动平均线
class TrixBackTest(BackTestApi.BackTest):
    def trade_test(self, data, n_list):
        # n_1
        n_1 = n_list[0]
        # arr
        time_arr = np.array([temp[0] for temp in data])
        price_arr = np.array([float(temp[4]) for temp in data])
        # real = T3(close, timeperiod=5, vfactor=0)
        trix_arr = talib.T3(price_arr, n_1)
        data_arr = np.hstack((time_arr.reshape(-1, 1), trix_arr.reshape(-1, 1), price_arr.reshape(-1, 1)))
        moneyResult = []
        for each in data_arr:
            # str -> float
            his_time = each[0]
            close_price = float(each[-1])
            trix = float(each[1])
            # 判断交易方向
            if self.status == 0:
                if close_price > trix:
                    self.open_buy(close_price, his_time)
                elif close_price < trix:
                    self.open_sell(close_price, his_time)
            elif self.status == 1:
                if close_price < trix:
                    self.close_sell(close_price, his_time)
                    self.open_sell(close_price, his_time)
            elif self.status == -1:
                if close_price > trix:
                    self.close_buy(close_price, his_time)
                    self.open_buy(close_price, his_time)
            # 资金曲线
            usdt = self.usdt_num + self.eth_num * close_price
            moneyResult.append(usdt)
        return moneyResult


# 三角形移动平均线
class TriMaBackTest(BackTestApi.BackTest):
    def trade_test(self, data, n_list):
        # n_1
        n_1 = n_list[0]
        # arr
        time_arr = np.array([temp[0] for temp in data])
        price_arr = np.array([float(temp[4]) for temp in data])
        # real = TRIMA(close, timeperiod=30)
        tri_arr = talib.TRIMA(price_arr, n_1)
        data_arr = np.hstack((time_arr.reshape(-1, 1), tri_arr.reshape(-1, 1), price_arr.reshape(-1, 1)))
        moneyResult = []
        for each in data_arr:
            # str -> float
            his_time = each[0]
            close_price = float(each[-1])
            tri = float(each[1])
            # 判断交易方向
            if self.status == 0:
                if close_price > tri:
                    self.open_buy(close_price, his_time)
                elif close_price < tri:
                    self.open_sell(close_price, his_time)
            elif self.status == 1:
                if close_price < tri:
                    self.close_sell(close_price, his_time)
                    self.open_sell(close_price, his_time)
            elif self.status == -1:
                if close_price > tri:
                    self.close_buy(close_price, his_time)
                    self.open_buy(close_price, his_time)
            # 资金曲线
            usdt = self.usdt_num + self.eth_num * close_price
            moneyResult.append(usdt)
        return moneyResult


# 加权移动平均线
class WmaBackTest(BackTestApi.BackTest):
    def trade_test(self, data, n_list):
        # n_1
        n_1 = n_list[0]
        # arr
        time_arr = np.array([temp[0] for temp in data])
        price_arr = np.array([float(temp[4]) for temp in data])
        # real = WMA(close, timeperiod=30)
        wma_arr = talib.WMA(price_arr, n_1)
        data_arr = np.hstack((time_arr.reshape(-1, 1), wma_arr.reshape(-1, 1), price_arr.reshape(-1, 1)))
        moneyResult = []
        for each in data_arr:
            # str -> float
            his_time = each[0]
            close_price = float(each[-1])
            wma = float(each[1])
            # 判断交易方向
            if self.status == 0:
                if close_price > wma:
                    self.open_buy(close_price, his_time)
                elif close_price < wma:
                    self.open_sell(close_price, his_time)
            elif self.status == 1:
                if close_price < wma:
                    self.close_sell(close_price, his_time)
                    self.open_sell(close_price, his_time)
            elif self.status == -1:
                if close_price > wma:
                    self.close_buy(close_price, his_time)
                    self.open_buy(close_price, his_time)
            # 资金曲线
            usdt = self.usdt_num + self.eth_num * close_price
            moneyResult.append(usdt)
        return moneyResult


# 中点指标
class MidpointBackTest(BackTestApi.BackTest):
    def trade_test(self, data, n_list):
        # n_1
        n_1 = n_list[0]
        # arr
        time_arr = np.array([temp[0] for temp in data])
        price_arr = np.array([float(temp[4]) for temp in data])
        # real = MIDPOINT(close, timeperiod=14)
        mid_arr = talib.MIDPOINT(price_arr, n_1)
        data_arr = np.hstack((time_arr.reshape(-1, 1), mid_arr.reshape(-1, 1), price_arr.reshape(-1, 1)))
        moneyResult = []
        for each in data_arr:
            # str -> float
            his_time = each[0]
            close_price = float(each[-1])
            mid = float(each[1])
            # 判断交易方向
            if self.status == 0:
                if close_price < mid:
                    self.open_buy(close_price, his_time)
                elif close_price > mid:
                    self.open_sell(close_price, his_time)
            elif self.status == 1:
                if close_price > mid:
                    self.close_sell(close_price, his_time)
                    self.open_sell(close_price, his_time)
            elif self.status == -1:
                if close_price < mid:
                    self.close_buy(close_price, his_time)
                    self.open_buy(close_price, his_time)
            # 资金曲线
            usdt = self.usdt_num + self.eth_num * close_price
            moneyResult.append(usdt)
        return moneyResult


# 中价指标
class MidPriceBackTest(BackTestApi.BackTest):
    def trade_test(self, data, n_list):
        # n_1
        n_1 = n_list[0]
        # arr
        time_arr = np.array([temp[0] for temp in data])
        price_arr = np.array([float(temp[4]) for temp in data])
        high_arr = np.array([float(temp[2]) for temp in data])
        low_arr = np.array([float(temp[3]) for temp in data])
        # real = MIDPRICE(high, low, timeperiod=14)
        mid_arr = talib.MIDPOINT(high_arr, low_arr, n_1)
        data_arr = np.hstack((time_arr.reshape(-1, 1), mid_arr.reshape(-1, 1), price_arr.reshape(-1, 1)))
        moneyResult = []
        for each in data_arr:
            # str -> float
            his_time = each[0]
            close_price = float(each[-1])
            mid = float(each[1])
            # 判断交易方向
            if self.status == 0:
                if close_price < mid:
                    self.open_buy(close_price, his_time)
                elif close_price > mid:
                    self.open_sell(close_price, his_time)
            elif self.status == 1:
                if close_price > mid:
                    self.close_sell(close_price, his_time)
                    self.open_sell(close_price, his_time)
            elif self.status == -1:
                if close_price < mid:
                    self.close_buy(close_price, his_time)
                    self.open_buy(close_price, his_time)
            # 资金曲线
            usdt = self.usdt_num + self.eth_num * close_price
            moneyResult.append(usdt)
        return moneyResult


""" END 米筐 START """


# 长短 均线 策略
class LongShortMaBackTest(BackTestApi.BackTest):
    def trade_test(self, data, n_list):
        # n
        n_1 = n_list[0]
        n_2 = n_list[1]
        # arr
        time_arr = np.array([temp[0] for temp in data])
        price_arr = np.array([float(temp[4]) for temp in data])
        # real = MA(close, timeperiod=30, matype=0)
        long_arr = talib.MA(price_arr, n_1)
        short_arr = talib.MA(price_arr, n_2)
        data_arr = np.hstack((time_arr.reshape(-1, 1), long_arr.reshape(-1, 1), short_arr.reshape(-1, 1),
                              price_arr.reshape(-1, 1)))
        moneyResult = []
        for each in data_arr:
            # str -> float
            his_time = each[0]
            close_price = float(each[-1])
            long = float(each[1])
            short = float(each[2])
            # 判断交易方向
            if self.status == 0:
                if short > long:
                    self.open_buy(close_price, his_time)
                elif short < long:
                    self.open_sell(close_price, his_time)
            elif self.status == 1:
                if short < long:
                    self.close_sell(close_price, his_time)
                    self.open_sell(close_price, his_time)
            elif self.status == -1:
                if short > long:
                    self.close_buy(close_price, his_time)
                    self.open_buy(close_price, his_time)
            # 资金曲线
            usdt = self.usdt_num + self.eth_num * close_price
            moneyResult.append(usdt)
        return moneyResult


# 平滑异同移动平均线
class MACDBackTest(BackTestApi.BackTest):
    def trade_test(self, data, n_list):
        # n
        n_1 = n_list[0]
        n_2 = n_list[1]
        n_3 = n_list[2]
        # arr
        time_arr = np.array([temp[0] for temp in data])
        price_arr = np.array([float(temp[4]) for temp in data])
        # dif, dem, histogram = MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
        macd_arr, signal_arr, hist_arr = talib.MACD(price_arr, n_1, n_2, n_3)
        data_arr = np.hstack((time_arr.reshape(-1, 1), macd_arr.reshape(-1, 1), signal_arr.reshape(-1, 1),
                              hist_arr.reshape(-1, 1), price_arr.reshape(-1, 1)))
        moneyResult = []
        for each in data_arr:
            # str -> float
            his_time = each[0]
            close_price = float(each[-1])
            macd = float(each[1])
            signal = float(each[2])
            # 判断交易方向
            if self.status == 0:
                if macd > signal:
                    self.open_buy(close_price, his_time)
                elif macd < signal:
                    self.open_sell(close_price, his_time)
            elif self.status == 1:
                if macd < signal:
                    self.close_sell(close_price, his_time)
                    self.open_sell(close_price, his_time)
            elif self.status == -1:
                if macd > signal:
                    self.close_buy(close_price, his_time)
                    self.open_buy(close_price, his_time)
            # 资金曲线
            usdt = self.usdt_num + self.eth_num * close_price
            moneyResult.append(usdt)
        return moneyResult


# 相对强弱指数
class RsiBackTest(BackTestApi.BackTest):
    def trade_test(self, data, n_list):
        # n
        n_1 = n_list[0]
        rsi_high = n_list[1]
        rsi_low = n_list[2]
        # arr
        time_arr = np.array([temp[0] for temp in data])
        price_arr = np.array([float(temp[4]) for temp in data])
        # real = RSI(close, timeperiod=14)
        rsi_arr = talib.RSI(price_arr, n_1)
        data_arr = np.hstack((time_arr.reshape(-1, 1), rsi_arr.reshape(-1, 1), price_arr.reshape(-1, 1)))
        moneyResult = []
        for each in data_arr:
            # str -> float
            his_time = each[0]
            close_price = float(each[-1])
            rsi = float(each[1])
            # 判断交易方向
            if self.status == 0:
                if rsi < rsi_low:
                    self.open_buy(close_price, his_time)
                elif rsi > rsi_high:
                    self.open_sell(close_price, his_time)
            elif self.status == 1:
                if rsi > rsi_high:
                    self.close_sell(close_price, his_time)
                    self.open_sell(close_price, his_time)
            elif self.status == -1:
                if rsi < rsi_low:
                    self.close_buy(close_price, his_time)
                    self.open_buy(close_price, his_time)
            # 资金曲线
            usdt = self.usdt_num + self.eth_num * close_price
            moneyResult.append(usdt)
        return moneyResult


# kd 指标
class StoChBackTest(BackTestApi.BackTest):
    def trade_test(self, data, n_list):
        # n
        n_1 = n_list[0]
        n_2 = n_list[1]
        n_3 = n_list[2]
        # arr
        time_arr = np.array([temp[0] for temp in data])
        price_arr = np.array([float(temp[4]) for temp in data])
        high_arr = np.array([float(temp[2]) for temp in data])
        low_arr = np.array([float(temp[3]) for temp in data])
        # k, d = STOCH(high, low, close, fastk_period=5, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
        k_arr, d_arr = talib.STOCH(high_arr, low_arr, price_arr, fastk_period=n_1, slowk_period=n_2, slowd_period=n_3)
        data_arr = np.hstack((time_arr.reshape(-1, 1), k_arr.reshape(-1, 1), d_arr.reshape(-1, 1),
                              price_arr.reshape(-1, 1)))
        moneyResult = []
        for each in data_arr:
            # str -> float
            his_time = each[0]
            close_price = float(each[-1])
            k = float(each[1])
            d = float(each[2])
            # 判断交易方向
            if self.status == 0:
                if k > d and ((k > 80 and d > 80) or (k < 20 and d < 20)):
                    self.open_buy(close_price, his_time)
                elif k < d and ((k > 80 and d > 80) or (k < 20 and d < 20)):
                    self.open_sell(close_price, his_time)
            elif self.status == 1:
                if k < d and ((k > 80 and d > 80) or (k < 20 and d < 20)):
                    self.close_sell(close_price, his_time)
                    self.open_sell(close_price, his_time)
            elif self.status == -1:
                if k > d and ((k > 80 and d > 80) or (k < 20 and d < 20)):
                    self.close_buy(close_price, his_time)
                    self.open_buy(close_price, his_time)
            # 资金曲线
            usdt = self.usdt_num + self.eth_num * close_price
            moneyResult.append(usdt)
        return moneyResult


""" END 形态识别 START """


# 三内部上涨和下跌
class Cdl3InsideBackTest(BackTestApi.BackTest):
    def trade_test(self, data, n_list):
        # arr
        time_arr = np.array([temp[0] for temp in data])
        open_arr = np.array([float(temp[1]) for temp in data])
        high_arr = np.array([float(temp[2]) for temp in data])
        low_arr = np.array([float(temp[3]) for temp in data])
        price_arr = np.array([float(temp[4]) for temp in data])
        # integer = CDL3INSIDE(open, high, low, close)
        cdl_arr = talib.CDL3INSIDE(open_arr, high_arr, low_arr, price_arr)
        data_arr = np.hstack((time_arr.reshape(-1, 1), cdl_arr.reshape(-1, 1), price_arr.reshape(-1, 1)))
        moneyResult = []
        for each in data_arr:
            # str -> float
            his_time = each[0]
            close_price = float(each[-1])
            cdl = float(each[1])
            # 判断交易方向
            if self.status == 0:
                if cdl > 0:
                    self.open_buy(close_price, his_time)
                elif cdl < 0:
                    self.open_sell(close_price, his_time)
            elif self.status == 1:
                if cdl < 0:
                    self.close_sell(close_price, his_time)
                    self.open_sell(close_price, his_time)
            elif self.status == -1:
                if cdl > 0:
                    self.close_buy(close_price, his_time)
                    self.open_buy(close_price, his_time)
            # 资金曲线
            usdt = self.usdt_num + self.eth_num * close_price
            moneyResult.append(usdt)
        return moneyResult


""" END 自定义策略 START """


# 追涨追跌策略（调仓：周期）
class YNBackTest(BackTestApi.BackTest):
    def trade_test(self, data, n_list):
        moneyResult = []
        for i in range(len(data)):
            close_price = float(data[i][4])
            diff = close_price - float(data[i][1])
            if self.status == 0:
                if diff > 0:
                    self.open_buy(close_price, data[i][0])
                elif diff < 0:
                    self.open_sell(close_price, data[i][0])
            elif self.status == 1:
                if diff < 0:
                    self.close_sell(close_price, data[i][0])
                    self.open_sell(close_price, data[i][0])
            elif self.status == -1:
                if diff > 0:
                    self.close_buy(close_price, data[i][0])
                    self.open_buy(close_price, data[i][0])
            # 资金曲线
            usdt = self.usdt_num + self.eth_num * close_price
            moneyResult.append(usdt)
        return moneyResult


# 菲阿里四价
class FalBackTest(BackTestApi.BackTest):
    def trade_test(self, data, n_list):
        # n_1 1440
        n_1 = n_list[0]
        # arr
        sh = np.array([float(temp[2]) for temp in data[:n_1]]).max()
        xh = np.array([float(temp[3]) for temp in data[:n_1]]).min()
        moneyResult = []
        # 遍历所有数据 每1440重新计算
        for i in range(n_1, len(data)):
            # 判断是否需要变更arr（到达收盘时间）
            if i % n_1 == n_1 - 1:
                # 清空所有仓位并更新上下轨
                if self.status == 1:
                    self.close_sell(float(data[i][4]), data[i][0])
                elif self.status == -1:
                    self.close_buy(float(data[i][4]), data[i][0])
                sh = np.array([float(temp[2]) for temp in data[i + 1 - n_1:i + 1]]).max()
                xh = np.array([float(temp[3]) for temp in data[i + 1 - n_1:i + 1]]).min()
            else:
                close_price = float(data[i][4])
                if self.status == 0:
                    if close_price > sh:
                        self.open_buy(close_price, data[i][0])
                    elif close_price < xh:
                        self.open_sell(close_price, data[i][0])
                elif self.status == 1:
                    if close_price < xh:
                        self.close_sell(close_price, data[i][0])
                        self.open_sell(close_price, data[i][0])
                elif self.status == -1:
                    if close_price > sh:
                        self.close_buy(close_price, data[i][0])
                        self.open_buy(close_price, data[i][0])
            # 资金曲线
            usdt = self.usdt_num + self.eth_num * float(data[i][4])
            moneyResult.append(usdt)
        return moneyResult


""" END 测试运行 START """


# 测试
def test():
    n_list = [12, 26, 9]
    start = '20181201080000'
    end = '20191217080000'
    bt = MACDBackTest()
    data = bt.db(cycle=1, startTime=start, endTime=end)
    bt.trade_test(data, n_list)


# 运行回测
def run():
    # 0.000008, 0.000100
    n_list = [0.000008, 0.000100]
    start = '20180101080000'
    end = '20201201080000'
    bt = SarBackTest()
    data = bt.db(cycle=1, startTime=start, endTime=end, cypair='ethusdt', table_name='ioc')
    bt.test(data, n_list)
    money = bt.moneyResult
    # orders
    order_arr = np.array(bt.orders)
    print(order_arr)
    order_money = order_arr[:, -1].astype(float)
    i = np.argmax(
        (np.maximum.accumulate(order_money) - order_money))
    # 开始位置
    try:
        j = np.argmax(order_money[:i])
    except:
        j = i
    order_maximum = order_money[int(j)] - order_money[int(i)]
    # 打印结果
    print('最大回撤金额：{}，回撤金额/本金：{}\n结算最大回撤金额：{}'
          '\n总盈亏法币数：{}\n盈亏法币/回撤金额：{}'
          '\n买卖次数：{}，总胜率：{}，连续亏损最大次数：{}'.format(
                bt.maximum, bt.maximum / bt.default_usdt, order_maximum,
                bt.usdt_num + bt.eth_num * float(data[-1][4]) - bt.default_usdt,
                (bt.usdt_num + bt.eth_num * float(data[-1][4]) - bt.default_usdt) / bt.maximum,
                bt.trade_count, bt.win_rate, bt.continuity_loss))
    # plt
    plt.figure(1)
    plt.plot(range(len(money)), money)
    # plt.xticks(range(0, len(money), len(money) // 23), ['1801', '1802', '1803', '1804', '1805', '1806',
    #                                                     '1807', '1808', '1809', '1810', '1811', '1812',
    #                                                     '1901', '1902', '1903', '1904', '1905', '1906',
    #                                                     '1907', '1908', '1909', '1910', '1911'])
    plt.figure(2)
    plt.plot(range(len(order_money)), order_money)
    # plt.xticks(range(0, len(order_money), len(order_money) // 23), ['1801', '1802', '1803', '1804', '1805', '1806',
    #                                                                 '1807', '1808', '1809', '1810', '1811', '1812',
    #                                                                 '1901', '1902', '1903', '1904', '1905', '1906',
    #                                                                 '1907', '1908', '1909', '1910', '1911'])
    plt.figure(3)
    x = np.array(bt.month_list)[:, 0].astype(str)
    y = np.array(bt.month_list)[:, 1].astype(float)
    plt.bar(x, y)
    for a, b in zip(x, y):
        plt.text(a, b - 0.02 if b < 0 else b + 0.01, '%.2f' % (b * 100.0) + "%", ha='center', va='bottom', fontsize=8)
    plt.show()


if __name__ == '__main__':
    run()
