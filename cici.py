import gdax_api, time, os, twil, sys, requests, logging, getopt, json, copy
from strategy import Strategy
from gdax_values import GDAXValues

#####################################

def setupLogging():
    global logger
    logger = logging.getLogger('CiciLogger')
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler(logFile)
    formatter = logging.Formatter('%(asctime)s] %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    # Set logging for requests and urllib3 which apparently uses INFO
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

def printAndSMS(message):
    logMessage(message)
    twil.sendSMS(message)

def logMessage(message):
    global logger
    print(message)
    logger.info(message)

def logStatus():
    if currentValues.waitingOnLongMA():
        logMessage('Waiting on long SMA. %s' % currentValues.desc())
    elif status == kWaitingToBuyStatus:
        logMessage('Waiting to buy. %s' % currentValues.desc())
    else:
        logMessage('Waiting to sell. %s' % currentValues.desc())

#####################################

def readConfig():
    global productID, logFile, status, strategy
    configFile = None
    options, remainder = getopt.getopt(sys.argv[1:], '', ['configFile='])
    for opt, arg in options:
        if opt == '--configFile':
            configFile = str(arg)
    if configFile is None:
        logMessage('Missing configFile param')
        sys.exit()

    config = json.load(open(configFile))
    if 'productID' in config:
        productID = config['productID']
    logFile = config['logFile']

    twil.phNum = config['phone']
    gdax_api.apiKey = config['apiKey']
    gdax_api.apiPass = config['apiPass']
    gdax_api.apiSecret = config['apiSecret']

    strategy = Strategy.fromConfig(config)

def determineStartingStatus():
    # If there's USD in the account on startup, assume we're ready to buy.
    global status
    startingFunds = gdax_api.getAccountFundsFor('USD')
    if startingFunds > 5.00:
        status = kWaitingToBuyStatus
        logMessage('Waiting to buy with starting funds: $%.02f' % startingFunds)
    else:
        status = kWaitingToSellStatus
        logMessage('Waiting to sell with starting funds: $%.02f' % startingFunds)


#####################################

def buy():
    global status, currentValues, lastValues
    accountFunds = gdax_api.getAccountFundsFor('USD')
    purchaseFunds = accountFunds * (1 - gdaxFee)
    appxFees = purchaseFunds * gdaxFee
    if debug:
        logMessage('BUYING %s at: $%0.2f - Cost: $%0.2f - ~Fees: $%0.2f' % (productID[:3], currentValues.price, purchaseFunds, appxFees))
        status = kWaitingToSellStatus
        lastValues = copy.copy(currentValues)
    else:
        printAndSMS('BUYING %s at: $%0.2f - Cost: $%0.2f - ~Fees: $%0.2f' % (productID[:3], currentValues.price, purchaseFunds, appxFees))
        order = gdax_api.buyMarket(productID, '{:.2f}'.format(purchaseFunds))
        if gdax_api.orderDidSucceed(order):
            printAndSMS('SUCCESS -- pending order ID: %s' % order['id'])
            status = kWaitingToSellStatus
            lastValues = copy.copy(currentValues)
        else:
            printAndSMS('ORDER FAILED!')
    logStatus()

def sell():
    global status, currentValues, lastValues
    size = gdax_api.getAccountFundsFor(productID[:3])
    appxFees = currentValues.price * size * gdaxFee
    appxNet = currentValues.price * size - appxFees
    sizeLessFess = size * (1 - gdaxFee)
    if debug:
        logMessage('SELLING %s at: $%0.2f - Size: %0.5f - ~Fees: $%0.2f - ~Net: $%0.2f' % (productID[:3], currentValues.price, sizeLessFess, appxFees, appxNet))
        status = kWaitingToBuyStatus
        lastValues = copy.copy(currentValues)
    else:
        printAndSMS('SELLING %s at: $%0.2f - Size: %0.5f - ~Fees: $%0.2f - ~Net: $%0.2f' % (productID[:3], currentValues.price, sizeLessFess, appxFees, appxNet))
        order = gdax_api.sellMarket(productID, '{:.5f}'.format(sizeLessFess))
        if gdax_api.orderDidSucceed(order):
            printAndSMS('SUCCESS -- pending order ID: %s' % order['id'])
            status = kWaitingToBuyStatus
            lastValues = copy.copy(currentValues)
        else:
            printAndSMS('ORDER FAILED!')
    logStatus()


#####################################

logger = None
logFile = None
debug = True
lastStatusLogTime = 0
sleepInterval = 60
statusLogInterval = 3600

productID = 'LTC-USD'
strategy = Strategy()
currentValues = GDAXValues()
lastValues = GDAXValues()
kWaitingToBuyStatus = 0
kWaitingToSellStatus = 1
status = None  # kWaitingToBuyStatus or kWaitingToSellStatus
gdaxFee = 0.0031  # actually it's .3% but overshoot to avoid errors

os.environ['TZ'] = 'US/Pacific'

readConfig()
setupLogging()

logMessage('Cici is starting up...')
print('Strategy: %s' % strategy.desc())
if debug:
    logMessage('DEBUG MODE IS ON')
    sleepInterval = 5
    statusLogInterval = 5

determineStartingStatus()

while True:

    try:
        candles = gdax_api.getCandles(productID, strategy.intervalSecs)

        # Sort them chrono instead of the reverse that's provided
        candles = list(reversed(candles))

        currentValues.update(candles, strategy, productID)

        if status == kWaitingToBuyStatus and strategy.shouldBuy(currentValues):
            buy()
        elif status == kWaitingToSellStatus and strategy.shouldSell(currentValues):
            sell()

        if time.time() - lastStatusLogTime > statusLogInterval:
            logStatus()
            lastStatusLogTime = time.time()

    except requests.exceptions.ConnectionError:
        logMessage('No Internet?')
    except ValueError as e:
        logMessage('ValueError exception: %s' % repr(e))
    except Exception as e:
        logMessage('Generic exception: %s' % repr(e))

    time.sleep(sleepInterval)
