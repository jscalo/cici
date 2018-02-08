import indicators
import gdax_api

class GDAXValues:
    ma1Value = 0.0
    ma2Value = 0.0
    ma3Value = None
    ma4Value = None
    price = 0.0

    def usesLongMA(self):
        return self.ma3Value is not None and self.ma4Value is not None

    def waitingOnLongMA(self):
        return self.usesLongMA() and self.ma3Value < self.ma4Value

    def desc(self):
        if self.usesLongMA():
            return 'Price: $%0.2f ma1: %0.2f ma2: %0.2f spread: %0.2f ma3: %0.2f ma4: %0.2f' % (self.price, self.ma1Value, self.ma2Value, abs(self.ma1Value - self.ma2Value), self.ma3Value, self.ma4Value)
        else:
            return 'Price: $%0.2f ma1: %0.2f ma2: %0.2f spread: %0.2f' % (self.price, self.ma1Value, self.ma2Value, abs(self.ma1Value - self.ma2Value))

    def maRatio(self):
        return abs((self.ma1Value - self.ma2Value)/self.ma1Value)

    def update(self, candles, strategy, productID):
        if self.usesLongMA():
            self.ma3Value = indicators.sma(candles, strategy.intervalSecs, strategy.ma3Count)
            self.ma4Value = indicators.sma(candles, strategy.intervalSecs, strategy.ma4Count)

        self.ma1Value = indicators.wma(strategy.maWeight, candles, strategy.intervalSecs, strategy.ma1Count)
        self.ma2Value = indicators.wma(strategy.maWeight, candles, strategy.intervalSecs, strategy.ma2Count)
        self.price = gdax_api.getPrice(productID)
