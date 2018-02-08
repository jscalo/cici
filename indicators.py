# These assume data is chrono sorted

# Simple moving average.
def sma(candles, intervalSecs, count):
    actualGranularity = granularityForInterval(intervalSecs)
    if actualGranularity == 0:
        raise RuntimeError('Granularity was 0')

    if not (float(intervalSecs) / float(actualGranularity)).is_integer():
        raise RuntimeError('Unsupported interval')

    hop = intervalSecs / actualGranularity
    startingDateSecs = candles[-1][0]
    offset = abs(int(startingDateSecs % intervalSecs) / actualGranularity)
    total = 0.0

    for i in range(0, count):
        idx = len(candles) - i*hop - offset - 1
        candle = candles[idx]
        price = candle[4]
        total += price

    return total / float(count)

# Weighted moving average. Use negative value for reverse weighting, i.e. emphasize older values more.
def wma(maxWeight, candles, intervalSecs, count):
    actualGranularity = granularityForInterval(intervalSecs)
    if actualGranularity == 0:
        raise RuntimeError('Granularity was 0')

    if not (float(intervalSecs) / float(actualGranularity)).is_integer():
        raise RuntimeError('Unsupported interval')

    absMaxWeight = abs(maxWeight)
    hop = intervalSecs / actualGranularity
    startingDateSecs = candles[-1][0]
    offset = abs(int(startingDateSecs % intervalSecs) / actualGranularity)

    total = 0.0

    totalWeight = 0.0
    weights = []
    for i in range(0, count):
        weight = 0.0
        if i > count - int(absMaxWeight):
            weight = absMaxWeight - (float(count) - float(i)) + 1.0
        else:
            weight = 1.0
        totalWeight += weight
        weights.append(weight)

    # Weights are sorted upward but we're working backward so reverse them.
    # (But if < 0 then this is a "reverse" wma, meaning emphasize values farther from T0, so leave as is.)
    if maxWeight > 0.0:
        weights = list(reversed(weights))

    for i in range(0, count):
        idx = len(candles) - i*hop - offset - 1
        candle = candles[idx]
        price = candle[4]
        total += weights[i] * price

    return total / totalWeight

def granularityForInterval(intervalSecs):
    # What's the largest supported granularity that's lower than our desired interval?
    supportedGranularities = [86400, 21600, 3600, 900, 300, 60]  # These are what GDAX supports.
    return max(filter(lambda x: x <= intervalSecs, supportedGranularities))
