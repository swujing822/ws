import ccxt.pro as ccxtpro
print('CCXT version', ccxtpro.__version__)
print('Supported exchanges:', ccxtpro.exchanges)

import asyncio
import csv
import os
from datetime import datetime, timezone
from datetime import datetime, timezone
import csv
import os

def format_time_from_timestamp(ts):
    dt = datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
    return dt.strftime('%H:%M:%S.') + f'{int(dt.microsecond / 1000):03d}'

def save_orderbook_top2_to_csv(ob, csv_file):
    if ob.get('timestamp') is None:
        timestamp_ms = int(time.time() * 1000)
    else:
        timestamp_ms = ob['timestamp']

    bids = ob.get('bids', [])
    asks = ob.get('asks', [])
    formatted_time = format_time_from_timestamp(timestamp_ms)

    row = [
        timestamp_ms,
        formatted_time,
        ob.get('symbol'),
        bids[0][0] if len(bids) > 0 else None,
        bids[0][1] if len(bids) > 0 else None,
        bids[1][0] if len(bids) > 1 else None,
        bids[1][1] if len(bids) > 1 else None,
        asks[0][0] if len(asks) > 0 else None,
        asks[0][1] if len(asks) > 0 else None,
        asks[1][0] if len(asks) > 1 else None,
        asks[1][1] if len(asks) > 1 else None,
    ]

    write_header = not os.path.exists(csv_file)
    with open(csv_file, mode='a', newline='') as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow([
                'timestamp', 'time', 'symbol',
                'bid1_price', 'bid1_volume',
                'bid2_price', 'bid2_volume',
                'ask1_price', 'ask1_volume',
                'ask2_price', 'ask2_volume'
            ])
        writer.writerow(row)


# 每个交易所的订阅协程
async def watch_orderbook_loop(exchange_id, symbol):
    exchange_class = getattr(ccxtpro, exchange_id)
    exchange = exchange_class()
    csv_file = f'orderbook_{exchange_id}_{symbol.replace("/", "")}.csv'

    try:
        while True:
            # ticker = await exchange.watch_ticker(symbol)
            # print(exchange_id, exchange.iso8601(exchange.milliseconds()), ticker['ask'], ticker['bid'])

            ob = await exchange.watchOrderBook(symbol)

            print(exchange_id, exchange.milliseconds(), ob.get('timestamp'))
            # save_orderbook_top2_to_csv(ob, csv_file)
    except asyncio.CancelledError:
        print(f"🟡 Cancelled: {exchange_id}")
    except Exception as e:
        print(f"🔴 Error in {exchange_id}: {e}")
    finally:
        await exchange.close()
        print(f"✅ Closed {exchange_id}")
import time

# 主函数并发运行多个交易所
async def main():
    symbols = [
        "1INCH/USDT:USDT",
        "A/USDT:USDT",
        "AAVE/USDT:USDT",
        "ACE/USDT:USDT",
        "ACH/USDT:USDT",
        "ACT/USDT:USDT",
        "ADA/USDT:USDT",
        "AERGO/USDT:USDT",
        "AERO/USDT:USDT",
        "AEVO/USDT:USDT",
        "AGLD/USDT:USDT",
        "AGT/USDT:USDT",
        "AI16Z/USDT:USDT",
        "AIN/USDT:USDT",
        "AIXBT/USDT:USDT",
        "ALCH/USDT:USDT",
        "ALGO/USDT:USDT",
        "ALT/USDT:USDT",
        "ANIME/USDT:USDT"
    ]
    exchange_ids = ['binanceusdm', 'blofin', 'kucoinfutures', 'bingx', 'mexc', 'binance', 'phemex', 'bybit', 'bitrue', 'bitmart', 'xt', 'bitget', 'gateio', 'gate']
    # exchange_ids = ['bitfinex']


    tasks = [
        asyncio.create_task(watch_orderbook_loop(exchange_id, symbol))
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
