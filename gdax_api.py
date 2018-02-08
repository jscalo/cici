import hmac, hashlib, time, requests, base64, json, indicators
from requests.auth import AuthBase

# Create custom authentication for Exchange
class CoinbaseExchangeAuth(AuthBase):
    def __init__(self, api_key, secret_key, passphrase):
        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase

    def __call__(self, request):
        timestamp = str(time.time())
        message = timestamp + request.method + request.path_url + (request.body or '')
        hmac_key = base64.b64decode(self.secret_key)
        signature = hmac.new(hmac_key, message, hashlib.sha256)
        signature_b64 = signature.digest().encode('base64').rstrip('\n')

        request.headers.update({
            'CB-ACCESS-SIGN': signature_b64,
            'CB-ACCESS-TIMESTAMP': timestamp,
            'CB-ACCESS-KEY': self.api_key,
            'CB-ACCESS-PASSPHRASE': self.passphrase,
            'Content-Type': 'application/json'
        })
        return request


apiURL = "https://api.gdax.com/".encode("utf-8")
apiKey = None
apiSecret = None
apiPass = None


def buyLimit(productID, price, size):
    auth = CoinbaseExchangeAuth(apiKey, apiSecret, apiPass)

    params = {}
    params["type"] = "limit"
    params["side"] = "buy"
    params["product_id"] = productID
    params["price"] = price
    params["size"] = size
    params["time_in_force"] = "GTC"

    req = requests.post(apiURL + 'orders', auth=auth, data=json.dumps(params))
    return req.json()

def buyMarket(productID, funds):
    auth = CoinbaseExchangeAuth(apiKey, apiSecret, apiPass)

    params = {}
    params["type"] = "market"
    params["side"] = "buy"
    params["product_id"] = productID
    params["funds"] = funds

    req = requests.post(apiURL + 'orders', auth=auth, data=json.dumps(params))
    return req.json()

def sellLimit(productID, price, size):
    auth = CoinbaseExchangeAuth(apiKey, apiSecret, apiPass)

    params = {}
    params["type"] = "limit"
    params["side"] = "sell"
    params["product_id"] = productID
    params["price"] = price
    params["size"] = size
    params["time_in_force"] = "GTC"

    req = requests.post(apiURL + 'orders', auth=auth, data=json.dumps(params))
    return req.json()

def sellMarket(productID, size):
    auth = CoinbaseExchangeAuth(apiKey, apiSecret, apiPass)

    params = {}
    params["type"] = "market"
    params["side"] = "sell"
    params["product_id"] = productID
    params["size"] = size

    req = requests.post(apiURL + 'orders', auth=auth, data=json.dumps(params))
    return req.json()

def getOrder(orderID):
    auth = CoinbaseExchangeAuth(apiKey, apiSecret, apiPass)
    req = requests.get(apiURL + 'orders/' + orderID, auth=auth)
    resp = req.json()
    return resp

def getPrice(productID):
    auth = CoinbaseExchangeAuth(apiKey, apiSecret, apiPass)
    req = requests.get(apiURL + 'products/' + productID + '/ticker', auth=auth)
    resp = req.json()
    return float(resp["price"])

def getCandles(productID, intervalSecs):
    actualGranularity = indicators.granularityForInterval(intervalSecs)
    if actualGranularity == 0:
        raise RuntimeError('Granularity was 0')

    auth = CoinbaseExchangeAuth(apiKey, apiSecret, apiPass)
    req = requests.get(apiURL + 'products/' + productID + '/candles', auth=auth, params={'granularity': actualGranularity})
    return req.json()

def getAccountFundsFor(currency):
        auth = CoinbaseExchangeAuth(apiKey, apiSecret, apiPass)
        req = requests.get(apiURL + 'accounts', auth=auth)
        accts = req.json()

        # accts is a list of accounts. Find the one that matches `currency`
        accts = [x for x in accts if x['currency'] == currency]
        if len(accts) == 0:
            raise IndexError('No %s Account' % currency)
        return float(accts[0]['available'])

def orderDidSucceed(order):
    if order is None:
        return False
    elif not isinstance(order, (dict)):
        return False
    else:
        return order.get('id') is not None
