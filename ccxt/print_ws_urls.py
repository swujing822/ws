import ccxt.pro as ccxtpro
import asyncio
import json

output_file = 'exchange_ws_urls.json'
rows = []

async def fetch_ws_urls(exchange_id):
    try:
        cls = getattr(ccxtpro, exchange_id)
        exchange = cls()
        ws_urls = exchange.urls['api']  # 如果你想专门获取 ws 类型，可调整这里

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
    # 写入 JSON 文件
    with open(output_file, 'w', encoding='utf-8') as jsonfile:
        json.dump(rows, jsonfile, ensure_ascii=False, indent=2)
    print(f"\n✅ WebSocket 地址已保存到: {output_file}")

asyncio.run(main())
