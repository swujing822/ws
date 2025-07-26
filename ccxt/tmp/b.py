import ccxt.pro as ccxtpro
import asyncio

count_orderbooks = 0
count_tickers = 0
total_exchanges = 0

count_orderbook = 0
count_ticker = 0

async def check_exchange(exchange_id):
    global count_orderbook, count_tickers, total_exchanges
    try:
        cls = getattr(ccxtpro, exchange_id)
        exchange = cls({'enableRateLimit': True})
        await exchange.load_markets()

        # has_orderbook = hasattr(exchange, 'watchOrderBookForSymbols')
        # has_tickers = hasattr(exchange, 'watchTickers')

        has_orderbooks = True if exchange.has['watchOrderBookForSymbols'] else False
        has_tickers = True if exchange.has['watchTickers'] else False

        has_orderbook = True if exchange.has['watchOrderBookForSymbol'] else False
        has_ticker = True if exchange.has['watchTicker'] else False

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
              f'watchTickers: {"✅" if has_tickers else "❌"} | '
              f'watchTickers: {"✅" if has_tickers else "❌"} | '

              )

        await exchange.close()

    except Exception as e:
        print(f'{exchange_id:<22} | ❌ ERROR: {str(e)}')
    finally:
        await exchange.close()
        # print(f"✅ Closed {exchange_id}")

async def main():
    await asyncio.gather(*[check_exchange(id) for id in ccxtpro.exchanges])
    print("\n--- ✅ 支持统计结果 ---")
    print(f'总交易所数量: {total_exchanges}')
    print(f'支持 watchOrderBookForSymbols 的交易所: {count_orderbook}')
    print(f'支持 watchTickers 的交易所: {count_tickers}')

asyncio.run(main())
