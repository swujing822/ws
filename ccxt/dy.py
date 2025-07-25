import ccxt.pro as ccxtpro
import asyncio
import csv
import os
from datetime import datetime, timezone
import time


def format_time_from_timestamp(ts):
    dt = datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
    return dt.strftime('%H:%M:%S.') + f'{int(dt.microsecond / 1000):03d}'


def save_orderbook_top2_to_csv(exchange_id, ob_dict, csv_file):
    write_header = not os.path.exists(csv_file)
    with open(csv_file, mode='a', newline='') as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow([
                'timestamp', 'time', 'exchange', 'symbol',
                'bid1_price', 'bid1_volume', 'bid2_price', 'bid2_volume',
                'ask1_price', 'ask1_volume', 'ask2_price', 'ask2_volume'
            ])
        for symbol, ob in ob_dict.items():
            timestamp_ms = ob.get('timestamp') or int(time.time() * 1000)
            formatted_time = format_time_from_timestamp(timestamp_ms)
            bids = ob.get('bids', [])
            asks = ob.get('asks', [])
            row = [
                timestamp_ms,
                formatted_time,
                exchange_id,
                symbol,
                bids[0][0] if len(bids) > 0 else None,
                bids[0][1] if len(bids) > 0 else None,
                bids[1][0] if len(bids) > 1 else None,
                bids[1][1] if len(bids) > 1 else None,
                asks[0][0] if len(asks) > 0 else None,
                asks[0][1] if len(asks) > 0 else None,
                asks[1][0] if len(asks) > 1 else None,
                asks[1][1] if len(asks) > 1 else None,
            ]
            writer.writerow(row)


async def watch_orderbooks(exchange_id, symbols):
    exchange_class = getattr(ccxtpro, exchange_id)
    exchange = exchange_class({'enableRateLimit': True})
    csv_file = f'csv/agg_orderbooks_{exchange_id}.csv'

    try:
        if hasattr(exchange, 'watchTickers'):
            while True:
                tickers = await exchange.watchTickers(symbols)
                for symbol, ticker in tickers.items():
                    print(
                        exchange,
                        exchange.iso8601(exchange.milliseconds()),
                        symbol,
                        ticker.get('bid'),
                        ticker.get('ask')
                    )
                    # 👉 可以调用 save 函数保存 ticker 信息
        else:
            print(f"🟡 {exchange_id} does not support watchOrderBookForSymbols, skipping")
    except asyncio.CancelledError:
        print(f"🟡 Cancelled: {exchange_id}")
    except Exception as e:
        print(f"🔴 Error in {exchange_id}: {e}")
    finally:
        await exchange.close()
        print(f"✅ Closed {exchange_id}")


async def main():
    contract_symbols = [
        # "1INCH/USDT:USDT", "A/USDT:USDT", "AAVE/USDT:USDT", "ACE/USDT:USDT",
        # "ACH/USDT:USDT", "ACT/USDT:USDT", "ADA/USDT:USDT", "AERGO/USDT:USDT",
        # "AERO/USDT:USDT", "AEVO/USDT:USDT", "AGLD/USDT:USDT", "AGT/USDT:USDT",
        # "AI16Z/USDT:USDT", "AIN/USDT:USDT", "AIXBT/USDT:USDT", "ALCH/USDT:USDT",
        "ALGO/USDT:USDT", "ANIME/USDT:USDT"
    ]

    exchange_ids = [
        # 'binanceusdm', 'blofin', 'kucoinfutures', 'bingx', 'mexc',
        # 'binance', 'phemex', 'bybit', 'bitrue', 'bitmart',
        'xt', 'bitget', 'gateio', 'gate'
    ]

    tasks = [asyncio.create_task(watch_orderbooks(exchange_id, contract_symbols)) for exchange_id in exchange_ids]

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
