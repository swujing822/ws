import ccxt.pro as ccxtpro
import asyncio

class MyCoinbase(ccxtpro.gateio):
    def handle_message(self, client, message):
        print("📨 Raw incoming message:")
        print(message)  # 原始 WebSocket 消息打印
        super().handle_message(client, message)  # 调用原始解析逻辑

# 自定义类，继承某个交易所
class MyCoinbase(ccxtpro.ascendex):
    def handle_message(self, client, message):
        print("📨 Raw incoming message:")
        print(message)  # 原始 WebSocket 消息打印
        super().handle_message(client, message)  # 调用原始解析逻辑

async def example():
    exchange = MyCoinbase({'enableRateLimit': True, 'verbose': False})
    await exchange.watch_ticker('ACH/USDT:USDT')
    await exchange.close()

asyncio.run(example())
