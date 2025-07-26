import ccxt.pro as ccxtpro
import asyncio
import csv
import os
import time
from datetime import datetime, timezone

# 自动创建 csv 目录
os.makedirs("csv", exist_ok=True)

# 时间格式化函数：13位时间戳 → 时:分:秒.ms
def format_time_from_timestamp(ts):
    dt = datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
    return dt.strftime('%H:%M:%S.') + f'{int(dt.microsecond / 1000):03d}'

# 保存行情到每个 symbol 的共享文件中（来自不同交易所）
def save_ticker_to_csv(exchange_id, symbol, ticker):
    timestamp_ms = ticker.get('timestamp') or int(time.time() * 1000)
    formatted_time = format_time_from_timestamp(timestamp_ms)
    symbol_clean = symbol.replace("/", "_").replace(":", "_")
    csv_file = f'csv/{symbol_clean}.csv'
    write_header = not os.path.exists(csv_file)

    row = [
        timestamp_ms,
        formatted_time,
        exchange_id,
        symbol,
        ticker.get('bid'),
        ticker.get('bidVolume'),
        ticker.get('ask'),
        ticker.get('askVolume'),
        ticker.get('last'),
        ticker.get('baseVolume'),
        ticker.get('quoteVolume'),
    ]

    with open(csv_file, mode='a', newline='') as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow([
                'timestamp', 'time', 'exchange', 'symbol',
                'bid', 'bidVolume',
                'ask', 'askVolume',
                'lastPrice',
                'baseVolume', 'quoteVolume'
            ])
        writer.writerow(row)

# 单个交易所聚合 ticker 订阅协程
async def watch_tickers(exchange_id, symbols):
    exchange_class = getattr(ccxtpro, exchange_id)
    exchange = exchange_class({'enableRateLimit': False})

    await exchange.load_markets()  

    try:
        if hasattr(exchange, 'watchTickers'):
            while True:
                tickers = await exchange.watchTickers(symbols)
                for symbol, ticker in tickers.items():
                    # print(
                    #     f"[{exchange_id}]",
                    #     exchange.iso8601(exchange.milliseconds()),
                    #     symbol,
                    #     f"bid: {ticker.get('bid')}",
                    #     f"ask: {ticker.get('ask')}"
                    # )
                    save_ticker_to_csv(exchange_id, symbol, ticker)
        else:
            print(f"🟡 {exchange_id} does not support watchTickers, skipping")
    except asyncio.CancelledError:
        print(f"🟡 Cancelled: {exchange_id}")
    except Exception as e:
        print(f"🔴 Error in {exchange_id}: {e}")
    finally:
        await exchange.close()
        print(f"✅ Closed {exchange_id}")

# 主函数
async def main():
    symbols = [
        "ALGO/USDT:USDT",
        "ADA/USDT:USDT",
        "AAVE/USDT:USDT",
        "ACH/USDT:USDT",
    ]

    exchange_ids = ['okx', 'binance', 'bybit', 'bitget', 'gateio']

    tasks = [
        asyncio.create_task(watch_tickers(exchange_id, symbols))
        for exchange_id in exchange_ids
    ]

    try:
        await asyncio.gather(*tasks)
    except KeyboardInterrupt:
        print("\n🔴 Ctrl+C received. Cancelling tasks...")
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        print("✅ All connections closed.")

if __name__ == '__main__':
    asyncio.run(main())
