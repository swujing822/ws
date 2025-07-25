import ccxt.pro as ccxtpro
import asyncio

async def check_symbol(exchange_id):
    exchange_class = getattr(ccxtpro, exchange_id)
    exchange = exchange_class()
    await exchange.load_markets()
    # print(exchange.symbols)

    c = 0
    for symbol in exchange.symbols:
        market = exchange.markets[symbol]
        if market['type'] == 'spot':
            continue
        c +=1
        print(f"{c} {exchange_id} {symbol} → type: {market['type']}, contract: {market['contract']}")
        
    await exchange.close()

# asyncio.run(check_symbol('bitfinex'))

import ccxt.pro as ccxtpro
print('CCXT version', ccxtpro.__version__)
print('Supported exchanges:', len(ccxtpro.exchanges), ccxtpro.exchanges)
