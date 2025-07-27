import ccxt.pro as ccxtpro
import asyncio
import csv
import os
import time
from datetime import datetime, timezone
import shutil
from utils.save_csv import *

csv_dir = "csv_orderbook"

clean_dir(csv_dir)

# ⏺️ 单个交易所单个 symbol 的订阅协程
async def watch_orderbook(exchange_id, symbol):
    exchange_class = getattr(ccxtpro, exchange_id)
    exchange = exchange_class({'enableRateLimit': False})
    await exchange.load_markets()
    try:
        while True:
            ob = await exchange.watch_order_book(symbol)
            symbol_clean = symbol.replace("/", "_").replace(":", "_")
            csv_file = f'{csv_dir}/orderbook_{exchange_id}_{symbol_clean}.csv'

            print(f"[{exchange_id}] {symbol} {ob['asks'][0] if ob['asks'] else 'No ask'}")

            save_orderbook_top2_to_csv(ob, csv_file)
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
        "AAVE/USDT:USDT",
        "AEVO/USDT:USDT"
    ]

    exchange_ids = [
        "ascendex"
    ]
    # try:
    #     await watch_orderbook(exchange_ids[0], symbols[0])
    # except Exception as e:
    #     print(f"🔴 Error : {e}")

    tasks = []
    for exchange_id in exchange_ids:
        for symbol in symbols:
            # tasks.append(asyncio.create_task(watch_orderbook(exchange_id, symbol)))
            print("start ", symbol)
            task = asyncio.create_task(watch_orderbook(exchange_id, symbol))
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
