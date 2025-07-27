import ccxt.pro as ccxtpro
import asyncio
import json

# 定义统计变量
results = []
summary = {
    'total_exchanges': 0,
    'count_orderbooks': 0,
    'count_tickers': 0,
    'count_orderbook': 0,
    'count_ticker': 0
}

async def check_exchange(exchange_id):
    try:
        cls = getattr(ccxtpro, exchange_id)
        exchange = cls({'enableRateLimit': True})
        await exchange.load_markets()

        has_orderbooks = exchange.has.get('watchOrderBookForSymbols', False)
        has_tickers = exchange.has.get('watchTickers', False)
        has_orderbook = exchange.has.get('watchOrderBook', False)
        has_ticker = exchange.has.get('watchTicker', False)

        summary['total_exchanges'] += 1
        summary['count_orderbooks'] += int(has_orderbooks)
        summary['count_tickers'] += int(has_tickers)
        summary['count_orderbook'] += int(has_orderbook)
        summary['count_ticker'] += int(has_ticker)

        results.append({
            'exchange': exchange_id,
            'watchOrderBookForSymbols': has_orderbooks,
            'watchTickers': has_tickers,
            'watchOrderBook': has_orderbook,
            'watchTicker': has_ticker
        })

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
    for key, value in summary.items():
        print(f'{key}: {value}')

    # 写入 JSON 文件
    output = {
        'exchanges': results,
        'summary': summary
    }
    with open('exchange_features.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

# 运行主任务
asyncio.run(main())
