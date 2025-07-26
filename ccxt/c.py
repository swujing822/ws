import ccxt.async_support as ccxt
import asyncio

symbols = [
    # "1INCH-USDT", "A-USDT", "AAVE-USDT", "ACE-USDT", "ACH-USDT", "ACT-USDT",
    "ADA-USDT", "AERGO-USDT", "AERO-USDT", "AEVO-USDT", "AGLD-USDT", "AGT-USDT",
    "AI16Z-USDT", "AIN-USDT", "AIXBT-USDT", "ALCH-USDT", "ALGO-USDT", "ALT-USDT",
    "ANIME-USDT"
]

contract_symbols = [s.replace("-", "/") + ":USDT" for s in symbols]
total_needed = len(contract_symbols)
min_required = int(total_needed * 0.9)

supported_exchanges = []

async def check_exchange(exchange_id):
    exchange = None
    try:
        cls = getattr(ccxt, exchange_id)
        exchange = cls({'enableRateLimit': True})
        await exchange.load_markets()

        # 筛选合约市场
        swap_markets = {k: v for k, v in exchange.markets.items() if v.get('type') == 'swap'}
        matches = [s for s in contract_symbols if s in swap_markets]

        if len(matches) >= min_required:
            supported_exchanges.append(exchange_id)
            print(f"✅ {exchange_id} 支持 {len(matches)}/{total_needed} 个 symbols")

    except Exception as e:
        print(f"❌ {exchange_id} error: {e}")

    finally:
        if exchange is not None:
            try:
                await exchange.close()
            except Exception:
                pass  # 忽略 close 报错

async def main():
    tasks = [check_exchange(eid) for eid in ccxt.exchanges]
    await asyncio.gather(*tasks)

    print("\n✅ 支持 ≥90% 合约的交易所：")
    print(supported_exchanges)

asyncio.run(main())