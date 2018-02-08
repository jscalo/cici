# Cici

Cici is a cryptocurrency trading bot written in Python and based on the GDAX API. Based on parameters in a config file it can trade using lots of different strategies based on up to four simple or weighted moving averages. Cici will send an SMS (via Twilio) when it makes a trade.

I wrote a blog post about my experiences [here](https://blog.madebywindmill.com/my-foray-into-algorithmic-crypto-trading-beac9113de36) that might help understand the project. You'll need a server to host it on.

### Obvious Disclaimer
This project is provided without warranty. Hopefully you're not dumb enough to dump your life savings into a volatile speculative market. But if you do, I'm not responsible for the results. Unless you make a lot of dough. In that case you can buy me a beer.

### Running Cici

Requirements:
* A GDAX API key
* A Twilio API key
* Some mula in your GDAX account

To run Cici:

`python cici.py --configFile Example-config.json`

If you're not running it from `rc.local`, et al you might want to:

`nohup python cici.py --configFile Example-config.json &`

When Cici starts up, it asks GDAX for your account balance. If there's money in your USD account it assumes you want to buy and will buy when the strategy allows. If there's no USD but there is coin in the cryptocurrency specified in the config file, it will assume you want to sell and will do so, again when the strategy allows.

**Be careful: Cici uses all-or-nothing logic. If there's USD, it buys with all of it. If there's coin, it sells all of it.**

### The Config File

_productID_

The product that you want to trade on GDAX. E.g. "BTC-USD".

_logFile_

A path to a file that Cici will log to.

_phone_

The phone number that Cici will SMS when a trade happens.

_maPeriodHours_

The interval in hours of the moving average period.

_ma1Count, ma2Count, ma3Count, ma4Count_

Cici supports either two or four moving average period lengths. `ma1Count` and `ma2Count` are the period lengths for short term trends. `ma3Count` and `ma4Count` are period lengths for long term trands. If only `ma1Count` and `ma2Count` are provided, the bot will try to sell whenever `ma1Value > ma2Value` and buy when `ma1Value < ma2Value`. If `ma3Count` and `ma4Count` are specified, then the bot will only trade when `ma3Value > ma4Value`.

_maWeight_

Setting `maWeight` to positive values above 1.0 will emphasize prices closer to the end of the window. Setting `maWeight` to negative values will emphasize prices closer to the beginning of the window. Setting `maWeight` to 1.0 makes it a simple moving average.

_maRatio_

Setting `maRatio` to > 0.0 will keep Cici from making a trade unless the values of the two short term averages have a variance of more than this ratio. For example, if `maRatio` is 0.002, Cici is waiting to sell, and the ma1 value is 134.77 while the ma2 value is 134.55, Cici won't sell even though ma1 > ma2 because (134.77 - 134.55)/134.77 = 0.0016 which is less than `maRatio` of 0.002. Using a `maRatio` may help avoid "whipsaw trading".

### FAQ

**I'm confused. How do I get help?**

Sorry, this project is provided with NO support so please don't email me for help.

**How should I report a bug?**

I _do_ want to know about outright bugs so file an issue if you find one.

**What's the best strategy?**

I wish I knew. If you find it, please let me know.

**Is it possible to test the bot before running it "live"?**

GDAX used to offer a sandbox version of their API but I haven't been able to get it to work. Instead you can set `debug` to `True` in `cici.py`. When run in debug mode, the bot will simulate buying and selling but will not actually execute any trades.

**Why does Cici use market orders?**

Limit orders are great since there are often no fees, but there's also no guarantee that the order will actually get executed so instead I've opted to use market orders and eat the fees.

**Your Python code sucks.**

OK first off that's not really a question. But hey, I'm a Swift/Obj-C programmer by trade so yeah my Python skills aren't that great. But I'm always learning so feel free to suggest improvements.