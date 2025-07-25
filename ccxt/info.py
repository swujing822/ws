import ccxt.pro as ccxtpro
import asyncio
import json
async def print_one_exchange_info(exchange_id):
    try:
        exchange_class = getattr(ccxtpro, exchange_id)
        exchange = exchange_class({'enableRateLimit': True})
        await exchange.load_markets()

        # print(exchange.urls)
        for u in exchange.urls:
            print(u, json.dumps(exchange.urls[u]))

        # 判断是否支持合约产品
        has_contract = any(m.get('contract', False) for m in exchange.markets.values())

        # 支持的 watch 方法
        supports = {
            'watchTickers': hasattr(exchange, 'watchTickers'),
            'watchOrderBook': hasattr(exchange, 'watchOrderBook'),
            'watchOrderBookForSymbols': hasattr(exchange, 'watchOrderBookForSymbols'),
            'watchTrades': hasattr(exchange, 'watchTrades'),
            'watchOHLCV': hasattr(exchange, 'watchOHLCV'),
            'watchOrders': hasattr(exchange, 'watchOrders'),
        }

        print(f"📊 Exchange: {exchange_id}")
        print(f"  ✅ Has contract markets: {has_contract}")
        for feature, supported in supports.items():
            print(f"  {'✅' if supported else '❌'} {feature}")

        await exchange.close()
    except Exception as e:
        print(f"🔴 Error loading {exchange_id}: {e}")

# 修改这里，指定你要查看的交易所 ID
asyncio.run(print_one_exchange_info('gateio'))
