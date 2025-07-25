import ccxt.pro as ccxtpro
import asyncio

# 定义全局变量用于统计
count_orderbooks = 0
count_tickers = 0
total_exchanges = 0
count_orderbook = 0
count_ticker = 0

async def check_exchange(exchange_id):
    global count_orderbooks, count_tickers, count_orderbook, count_ticker, total_exchanges
    try:
        cls = getattr(ccxtpro, exchange_id)
        exchange = cls({'enableRateLimit': True})
        await exchange.load_markets()

        has_orderbooks = exchange.has.get('watchOrderBookForSymbols', False)
        has_tickers = exchange.has.get('watchTickers', False)
        has_orderbook = exchange.has.get('watchOrderBook', False)
        has_ticker = exchange.has.get('watchTicker', False)

        if has_orderbooks:
            count_orderbooks += 1
        if has_tickers:
            count_tickers += 1
        if has_orderbook:
            count_orderbook += 1
        if has_ticker:
            count_ticker += 1

        total_exchanges += 1

        print(f'{exchange_id:<22} | OrderBookForSymbols: {"✅" if has_orderbooks else "❌"} | '
              f'watchTickers: {"✅" if has_tickers else "❌"} | '
              f'has_orderbook: {"✅" if has_orderbook else "❌"} | '
              f'has_ticker: {"✅" if has_ticker else "❌"}')

        await exchange.close()

    except Exception as e:
        print(f'{exchange_id:<22} | ❌ ERROR: {str(e)}')
    finally:
        await exchange.close()

async def main():
    await asyncio.gather(*[check_exchange(id) for id in ccxtpro.exchanges])
    print("\n--- ✅ 支持统计结果 ---")
    print(f'总交易所数量: {total_exchanges}')
    print(f'支持 watchOrderBookForSymbols 的交易所: {count_orderbooks}')
    print(f'支持 watchTickers 的交易所: {count_tickers}')
    print(f'支持 watchOrderBook 的交易所: {count_orderbook}')
    print(f'支持 watchTicker 的交易所: {count_ticker}')

# 运行主任务
asyncio.run(main())
