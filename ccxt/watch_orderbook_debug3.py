import ccxt.pro as ccxtpro
import asyncio
import csv
import os
import time
from datetime import datetime, timezone
import shutil

csv_dir = "csv_orderbook_two"

if os.path.exists(csv_dir) and os.path.isdir(csv_dir):
    shutil.rmtree(csv_dir)
    print(f"Deleted directory: {csv_dir}")
else:
    print(f"Directory does not exist: {csv_dir}")

os.makedirs(csv_dir, exist_ok=True)

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
        csv_file = f'{csv_dir}/orderbook_{exchange_id}_{symbol_clean}.csv'

        # print(f"[{exchange_id}] {symbol} {ob['asks'][0] if ob['asks'] else 'No ask'}")

        save_orderbook_top2_to_csv(ob, csv_file)

# ⏺️ 单个交易所单个 symbol 的订阅协程
async def watch_orderbook(exchange_id, symbols):
    exchange_class = getattr(ccxtpro, exchange_id)
    exchange = exchange_class({'enableRateLimit': False})
    await exchange.load_markets()

    # sub_symbols = [
    #     "ALGO/USDT:USDT",
    #     "ADA/USDT:USDT",
    #     "AAVE/USDT:USDT",
    #     "ACH/USDT:USDT",
    # ]

    try:
        tasks = []

        for symbol in symbols:
            # tasks.append(asyncio.create_task(watch_orderbook(exchange_id, symbol)))
            print("start ", symbol)
            task = asyncio.create_task(watch_one_symbol(exchange, exchange_id, symbol))
            tasks.append(task)
            # await asyncio.sleep(1)  # 👈 延迟启动，避免被限速封 IP 等问题
        try:
            await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            print("\n🔴 Ctrl+C received. Cancelling tasks...")
            for task in tasks:
                task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)
    except asyncio.CancelledError:
        print(f"🟡 Cancelled: {exchange_id} {symbol}")
    except Exception as e:
        print(f"🔴 Error in {exchange_id} {symbol}: {e}")
    finally:
        await exchange.close()
        print(f"✅ Closed {exchange_id} {symbol}")

# ⏺️ 主函数
async def main():
    symbols = [
        "ALGO/USDT:USDT"
    ]

    symbols = [
    
    "DOGE/USDT:USDT",
    "DOGS/USDT:USDT",
    ]

    

    exchange_ids = [
        "gateio"
    ]

    await watch_orderbook(exchange_ids[0], symbols)

    # tasks = []
    # for exchange_id in exchange_ids:
    #     for symbol in symbols:
    #         # tasks.append(asyncio.create_task(watch_orderbook(exchange_id, symbol)))
    #         print("start ", symbol)
    #         task = asyncio.create_task(watch_orderbook(exchange_id, symbol))
    #         tasks.append(task)
    #         await asyncio.sleep(1)  # 👈 延迟启动，避免被限速封 IP 等问题

    # try:
    #     await asyncio.gather(*tasks)
    # except KeyboardInterrupt:
    #     print("\n🔴 Ctrl+C received. Cancelling tasks...")
    #     for task in tasks:
    #         task.cancel()
    #     await asyncio.gather(*tasks, return_exceptions=True)
    #     print("✅ All connections closed.")

if __name__ == '__main__':
    asyncio.run(main())
