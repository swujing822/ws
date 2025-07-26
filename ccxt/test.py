import ccxt.pro as ccxtpro

async def print_ws_url(exchange_id):
    cls = getattr(ccxtpro, exchange_id)
    exchange = cls()
    # 获取 WSS 地址
    ws_url = exchange.urls['api'].get('ws', 'N/A')
    # print(f"{exchange_id}: WebSocket URL -> {ws_url}")
    for u in ws_url:
        print(u, ws_url[u])
    await exchange.close()

import asyncio
asyncio.run(print_ws_url('binance'))
