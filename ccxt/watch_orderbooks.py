import ccxt.pro as ccxtpro
import asyncio
import csv
import os
import time
from datetime import datetime, timezone
import shutil

csv_dir = "csv_orderbooks_two"

if os.path.exists(csv_dir) and os.path.isdir(csv_dir):
    shutil.rmtree(csv_dir)
    print(f"Deleted directory: {csv_dir}")
else:
    print(f"Directory does not exist: {csv_dir}")

os.makedirs(csv_dir, exist_ok=True)

# 时间格式化函数：13位时间戳 → 时:分:秒.ms
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

async def watch_one_symbol(exchange, exchange_id, symbol):
    while True:
        ob = await exchange.watch_order_book(symbol)
        symbol_clean = symbol.replace("/", "_").replace(":", "_")
        csv_file = f'{csv_dir}/orderbook_inner_{exchange_id}_{symbol_clean}.csv'

        # print(f"[{exchange_id}] {symbol} {ob['asks'][0] if ob['asks'] else 'No ask'}")

        save_orderbook_top2_to_csv(ob, csv_file)

# 单个交易所聚合 ticker 订阅协程
async def watch_orderbooks(exchange_id, symbols):
    exchange_class = getattr(ccxtpro, exchange_id)
    exchange = exchange_class({'enableRateLimit': False})
    await exchange.load_markets()  # 必须加载市场

    try:
        if exchange.has['watchOrderBookForSymbols']:

            while True:
                ob = await exchange.watchOrderBookForSymbols(symbols)
                symbol = ob['symbol'].replace("/", "_").replace(":", "_")
                csv_file = f'{csv_dir}/orderbook_{exchange_id}_{symbol}.csv'

                # print(ob['asks'][0], ob['symbol'])
                save_orderbook_top2_to_csv(ob, csv_file)
                # for symbol, ticker in tickers.items():
                #     save_ticker_to_csv(exchange_id, symbol, ticker)
        else:
            print(f"🟡 {exchange_id} does not support watchTickers, skipping")
            inner_tasks = []

            for symbol in symbols:
                # tasks.append(asyncio.create_task(watch_orderbook(exchange_id, symbol)))
                print("inner start ", symbol)
                task = asyncio.create_task(watch_one_symbol(exchange, exchange_id, symbol))
                inner_tasks.append(task)
                await asyncio.sleep(1)  # 👈 延迟启动，避免被限速封 IP 等问题
            try:
                await asyncio.gather(*inner_tasks)
            except KeyboardInterrupt:
                print("\n🔴 Ctrl+C received. Cancelling tasks...")
                for task in inner_tasks:
                    task.cancel()
                await asyncio.gather(*inner_tasks, return_exceptions=True)
    except asyncio.CancelledError:
        print(f"🟡 Cancelled: {exchange_id}")
    except Exception as e:
        print(f"🔴 Error in {exchange_id}: {e}")
    finally:
        await exchange.close()
        print(f"✅ Closed {exchange_id}")

import json
async def main():

    with open("../selector/top100_exchange_symbols.json", "r", encoding="utf-8") as f:
        ex_syms = json.load(f)

    # print(ex_syms)
    

    tasks = [
    ]

    skips = ["digifinex", "bitmart"]

    for exchange_id in ex_syms:
        if exchange_id in skips:
            print("skip ", exchange_id)
            continue
        print(f"start {exchange_id}")
        task = asyncio.create_task(watch_orderbooks(exchange_id, ex_syms[exchange_id]))
        tasks.append(task)
        await asyncio.sleep(1)  # 👈 延迟启动，避免被限速封 IP 等问题
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
