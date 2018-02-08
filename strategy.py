# Note: max count supported by GDAX is 80 when interval is 4 hours, max of 320 when 1 hour.

class Strategy:
    ma1Count = 0
    ma2Count = 0
    ma3Count = None
    ma4Count = None
    maWeight = 1.0
    maRatio = 0.0
    intervalSecs = 0

    @classmethod
    def fromConfig(cls, config):
        strategy = Strategy()
        strategy.ma1Count = config['ma1Count']
        strategy.ma2Count = config['ma2Count']
        strategy.ma3Count = config['ma3Count']
        strategy.ma4Count = config['ma4Count']
        strategy.maWeight = config['maWeight']
        strategy.maRatio = config['maRatio']
        strategy.intervalSecs = config['maPeriodHours'] * 3600
        return strategy

    def usesLongMA(self):
        return self.ma3Count is not None and self.ma4Count is not None

    def desc(self):
        if self.usesLongMA():
            return 'ma1Count: %d; ma2Count: %d; ma3Count: %d; ma4Count: %d; maWeight: %0.2f; maRatio: %0.3f; interval: %d hours' % (self.ma1Count, self.ma2Count, self.ma3Count, self.ma4Count, self.maWeight, self.maRatio, self.intervalSecs / 3600)
        else:
            return 'ma1Count: %d; ma2Count: %d; maWeight: %.02f; maRatio: %.03f, interval: %d hours' % (self.ma1Count, self.ma2Count, self.maWeight, self.maRatio,  self.intervalSecs / 3600)

    def shouldBuy(self, values):
        if self.usesLongMA() and values.ma3Value < values.ma4Value:
            return False
        if values.maRatio() < self.maRatio:
            return False
        return values.ma1Value > values.ma2Value

    def shouldSell(self, values):
        if self.usesLongMA() and values.ma3Value < values.ma4Value:
            return False
        if values.maRatio() < self.maRatio:
            return False
        return values.ma1Value < values.ma2Value
