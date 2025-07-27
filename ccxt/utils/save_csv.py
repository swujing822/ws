import csv
import os
import time
from datetime import datetime, timezone
import shutil

def clean_dir(csv_dir):
    if os.path.exists(csv_dir) and os.path.isdir(csv_dir):
        shutil.rmtree(csv_dir)
        print(f"Deleted directory: {csv_dir}")
    else:
        print(f"Directory does not exist: {csv_dir}")

    os.makedirs(csv_dir, exist_ok=True)


def format_time_from_timestamp(ts):
    dt = datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
    return dt.strftime('%H:%M:%S.') + f'{int(dt.microsecond / 1000):03d}'

def save_orderbook_top2_to_csv(ex_id, ob, csv_file):
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
        ex_id,
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
                'timestamp', 'time', 'exchange', 'symbol',
                'bid1_price', 'bid1_volume',
                'bid2_price', 'bid2_volume',
                'ask1_price', 'ask1_volume',
                'ask2_price', 'ask2_volume'
            ])
        writer.writerow(row)
