#!/usr/bin/env python

# fetch my crypto prices
# 




import argparse
import decimal
import json
import os
import requests
import ruamel.yaml as yaml

from binance.client import Client

decimal.getcontext().prec = 5

COINBASE_URL = 'https://api.coinmarketcap.com/v1/ticker/?limit=0'

class CryptCoinException(Exception):
    pass

class CryptoCoin(object):
    def __init__(self, sym, amount=0):
        self._sym = sym
        self._amount = amount
        self._tick = None
        
    @property
    def sym(self):
        return self._sym

    @property
    def ticker(self):
        return self._tick

    @ticker.setter
    def ticker(self, inc):
        self._tick = inc

    @property
    def amount(self):
        return self._amount

    @amount.setter
    def amount(self, num):
        self._amount = num

    def __str__(self):
        return "CryptoCoin: {} amount: {}".format(self.sym, self.amount)

    def __repr__(self):
        return "CryptoCoin: {} amount: {}".format(self.sym, self.amount)

    def to_dollars(self):
        if self._tick is None:
            raise CryptCoinException('Ticker not found for this coin.')

        return decimal.Decimal(self.ticker['price_usd']) * decimal.Decimal(self.amount)

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbosity", help="Increase output verbosity")
    parser.add_argument("-f", "--file", help="pass in yaml a file")

    return parser.parse_args()


def get_tickers(assets, start=0, limit=100):
    '''fetch the ticker symbols 100 at a time and stop once we have them all'''
    tickers = []
    tmp_tickers = requests.get(COINBASE_URL + '?limit={}&start={}'.format(limit, start))
    while tmp_tickers.ok:
        for tick in json.loads(tmp_tickers.text):
            for asset in assets:
                if tick['symbol'].lower() == asset.sym.lower():
                    tickers.append(tick)
                    asset.ticker = tick
    
        if all([asset.ticker is not None for asset in assets]):
            break
        start += 100
        tmp_tickers = requests.get(COINBASE_URL + '?limit={}&start={}'.format(limit, start))

def main():
    assets = []
    args = parse_args()
    if args.file is not None:
        data = yaml.safe_load(open(args.file))
        assets = [CryptoCoin(d['symbol'], d['amount']) for d in data['assets']]

    bclient = Client(os.environ['BINANCE_API_KEY'], os.environ['BINANCE_API_SECRET_KEY'])
    acc = bclient.get_account()
    assets.extend([CryptoCoin(z['asset'], float(z['free'])) for z in acc['balances'] if float(z['free']) != 0.0 or float(z['locked']) != 0.0 ])
    get_tickers(assets)

    total = 0
    for asset in assets:
        dollar = asset.to_dollars()
        total += dollar
        print "Symbol: {}: USD: {}".format(asset.sym, dollar)
    print "Total Assets: {}: Total: {}".format(len(assets), total)

    # Fetch binance coins and amounts


if __name__ == '__main__':
    main()
