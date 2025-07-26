import ccxt.pro as ccxtpro
import asyncio
import csv

output_file = 'exchange_ws_urls.csv'
fieldnames = ['Exchange', 'Type', 'WebSocket URL']
rows = []

async def fetch_ws_urls(exchange_id):
    try:
        cls = getattr(ccxtpro, exchange_id)
        exchange = cls()
        ws_urls = exchange.urls['api']#.get('ws', {})

        print(f"\n📡 {exchange_id.upper():<20} WebSocket URLs:")
        if isinstance(ws_urls, dict):
            for key, url in ws_urls.items():
                print(f"  🔸 {key:<10}: {url}")
                rows.append({'Exchange': exchange_id, 'Type': key, 'WebSocket URL': url})
        else:
            print(f"  🔸 default   : {ws_urls}")
            rows.append({'Exchange': exchange_id, 'Type': 'default', 'WebSocket URL': ws_urls})

        await exchange.close()

    except Exception as e:
        print(f"\n⚠️  {exchange_id.upper():<20} ERROR: {str(e)}")
    finally:
        try:
            await exchange.close()
        except:
            pass

async def main():
    await asyncio.gather(*[fetch_ws_urls(id) for id in ccxtpro.exchanges])
    # 写入 CSV 文件
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"\n✅ WebSocket 地址已保存到: {output_file}")

asyncio.run(main())
