import indicators, json

def isclose(a, b, rel_tol=1e-08, abs_tol=0.0):
    return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)

intervalSecs = 3600*4
data = json.load(open("test_data.json"))

testCandles = list(reversed(data[0]))

result = indicators.sma(testCandles, 3600, 5)
answer = 166.554
if isclose(result, answer):
    print("sma test0 passed")
else:
    print("sma test0 failed. was %f; expected %f" % (result, answer))

result = indicators.sma(testCandles, 4*3600, 2)
answer = 172.64
if isclose(result, answer):
    print("sma test1 passed")
else:
    print("sma test1 failed. was %f; expected %f" % (result, answer))

testCandles = list(reversed(data[1]))

result = indicators.sma(testCandles, 3600, 4)
answer = 176.05
if isclose(result, answer):
    print("sma test2 passed")
else:
    print("sma test2 failed. was %f; expected %f" % (result, answer))

testCandles = list(reversed(data[2]))
answer = 179.189375
result = indicators.wma(4.0, testCandles, 3600, 10)
if isclose(result, answer):
    print("wma test0 passed")
else:
    print("wma test0 failed. was %f; expected %f" % (result, answer))

testCandles = list(reversed(data[3]))
answer = 181.833333
result = indicators.wma(5.0, testCandles, 2*3600, 8)
if isclose(result, answer):
    print("wma test1 passed")
else:
    print("wma test1 failed. was %f; expected %f" % (result, answer))

testCandles = list(reversed(data[0]))
answer = 170.85722222222222
result = indicators.wma(-8.0, testCandles, 3600, 8)
if isclose(result, answer):
    print("wma test2 passed")
else:
    print("wma test2 failed. was %f; expected %f" % (result, answer))

testCandles = list(reversed(data[0]))
answer = 166.877778
result = indicators.wma(8.0, testCandles, 3600, 8)
if isclose(result, answer):
    print("wma test3 passed")
else:
    print("wma test3 failed. was %f; expected %f" % (result, answer))
