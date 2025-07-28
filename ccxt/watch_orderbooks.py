import ccxt.pro as ccxtpro
import asyncio
import csv
import os
import time
from datetime import datetime, timezone
import shutil
from utils.save_csv import *

csv_dir = "csv_orderbooks_two3"

clean_dir(csv_dir)

csv_symbol_dir = "csv_orderbooks_symbol3"

clean_dir(csv_symbol_dir)

async def watch_one_symbol(exchange, exchange_id, symbol, max_retries=3):
    retry_count = 0
    while retry_count < max_retries:
        try:
            ob = await exchange.watch_order_book(symbol)
            retry_count = 0  # 成功订阅后重置重试计数器

            symbol_clean = symbol.replace("/", "_").replace(":", "_")
            csv_file = f'{csv_dir}/inner_orderbook_{exchange_id}_{symbol_clean}.csv'
            # timestamp_ms = ob['timestamp']

            save_orderbook_top2_to_csv(exchange_id, ob, csv_file)

            csv_symbol_file = f'{csv_symbol_dir}/ob_{symbol_clean}.csv'
            save_orderbook_top2_to_csv(exchange_id, ob, csv_symbol_file)
        except Exception as e:
            retry_count += 1
            print(f"🔴 Failed to subscribe {symbol} on {exchange_id}: {e} [retry {retry_count}/{max_retries}]")
            await asyncio.sleep(1)

    print(f"❌ Exiting {exchange_id} - {symbol} subscription after {max_retries} failed attempts.")

# async def watch_one_symbol(exchange, exchange_id, symbol):
#     while True:
#         try:
#             ob = await exchange.watch_order_book(symbol)
#             symbol_clean = symbol.replace("/", "_").replace(":", "_")
#             csv_file = f'{csv_dir}/inner_orderbook_{exchange_id}_{symbol_clean}.csv'
#             timestamp_ms = ob['timestamp']
#             # print(f"{ob['nonce']} {ob['timestamp']} {format_time_from_timestamp(timestamp_ms)} [{exchange_id}] {symbol} {ob['asks'][0]}")
#             # print(ob['symbol'])

#             save_orderbook_top2_to_csv(ob, csv_file)
#         except Exception as e:
#             print(f"🔴 Failed to subscribe {symbol} on {exchange_id}: {e}")
#             await asyncio.sleep(1)
#             continue

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
                # save_orderbook_top2_to_csv(ob, csv_file)
                save_orderbook_top2_to_csv(exchange_id, ob, csv_file)

                csv_symbol_file = f'{csv_symbol_dir}/ob_{symbol}.csv'
                save_orderbook_top2_to_csv(exchange_id, ob, csv_symbol_file)
                # for symbol, ticker in tickers.items():
                #     save_ticker_to_csv(exchange_id, symbol, ticker)
        else:
            print(f"🟡 {exchange_id} does not support watchOrderBookForSymbols, skipping")
            # inner_tasks = []

            # for symbol in symbols:
            #     # tasks.append(asyncio.create_task(watch_orderbook(exchange_id, symbol)))
            #     print("inner start ", symbol)
            #     task = asyncio.create_task(watch_one_symbol(exchange, exchange_id, symbol))
            #     inner_tasks.append(task)
            #     await asyncio.sleep(1)  # 👈 延迟启动，避免被限速封 IP 等问题
            # try:
            #     await asyncio.gather(*inner_tasks)
            # except KeyboardInterrupt:
            #     print("\n🔴 Ctrl+C received. Cancelling tasks...")
            #     for task in inner_tasks:
            #         task.cancel()
            #     await asyncio.gather(*inner_tasks, return_exceptions=True)
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

    with open("./exchange_profile.json", "r", encoding="utf-8") as f:
        exchange_profile = json.load(f)

    # print(exchange_profile)

    # for exchange_id in exchange_profile:
    #     has_orderbooks = exchange_profile[exchange_id]['has_orderbooks']
    #     has_tickers = exchange_profile[exchange_id]['has_tickers']
    #     has_orderbook = exchange_profile[exchange_id]['has_orderbook']
    #     has_ticker = exchange_profile[exchange_id]['has_ticker']

    #     print(f'{exchange_id:<22} | OrderBookForSymbols: {"✅" if has_orderbooks else "❌"} | '
    #           f'watchTickers: {"✅" if has_tickers else "❌"} | '
    #           f'has_orderbook: {"✅" if has_orderbook else "❌"} | '
    #           f'has_ticker: {"✅" if has_ticker else "❌"}')

    # print(ex_syms)
    #     "AAVE/USDT:USDT",
    # "ACT/USDT:USDT",
    # "ADA/USDT:USDT",

    tasks = []
    inner_tasks = []


    skips = ["digifinex", "bitmart", 'lbank', 'bitrue']

    # selected = ["ascendex", 'bybit']
    selected = ["ascendex"]


    exchanges = []

    for exchange_id in ex_syms:
        if exchange_id in skips:
            print("skip ", exchange_id)
            continue
        # if exchange_id not in selected:
        #     print("skip ", exchange_id)
        #     continue
                
        symbols = ex_syms[exchange_id]
        if not exchange_profile[exchange_id]['has_orderbooks']:
        # if len(symbols) > 0:
            try:
                exchange_class = getattr(ccxtpro, exchange_id)
                exchange = exchange_class({'enableRateLimit': False})
                await exchange.load_markets()  # 必须加载市场
                exchanges.append(exchange)
                for symbol in symbols:
                    print("inner start ", exchange_id, symbol, '...')

                    task = asyncio.create_task(watch_one_symbol(exchange, exchange_id, symbol))
                    tasks.append(task)
                    # await asyncio.sleep(2)
            except asyncio.CancelledError:
                print(f"🟡 Cancelled: {exchange_id}")
            except Exception as e:
                print(f"🔴 Error in {exchange_id}: {e}")
            # finally:
            #     await exchange.close()
            #     print(f"✅ Closed {exchange_id}")
        else:
            print(f"start {exchange_id} >>>>>>>>>>>>>>>")
            task = asyncio.create_task(watch_orderbooks(exchange_id, symbols))
            tasks.append(task)
            await asyncio.sleep(1)  # 👈 延迟启动，避免被限速封 IP 等问题
    try:
        # await asyncio.gather(*tasks)
        await asyncio.gather(*tasks, return_exceptions=True)

    except KeyboardInterrupt:
        print("\n🔴 Ctrl+C received. Cancelling tasks...")
        # for ex in exchanges:
        #     print("111111111 close ", ex)

        #     ex.close()
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        print("✅ All connections closed.")
    finally:
        for ex in exchanges:
            print("222222222 close ", ex)
            await ex.close()
            print(f"✅ Closed {ex}")

if __name__ == '__main__':
    asyncio.run(main())
