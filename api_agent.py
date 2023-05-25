from main import AgentRemote

remote_agent = AgentRemote("test", ["XYZ"], 10000)
last_trade = remote_agent.get_latest_trade('XYZ')
best_bid = remote_agent.get_best_bid('XYZ')
best_ask = remote_agent.get_best_ask('XYZ')
midprice = remote_agent.get_midprice('XYZ')
order_book = remote_agent.get_order_book('XYZ')
quotes = remote_agent.get_quotes('XYZ')
trades = remote_agent.get_trades('XYZ')

market_buy = remote_agent.market_buy('XYZ', 1)
market_sell = remote_agent.market_sell('XYZ', 1)
limit_buy = remote_agent.limit_buy('XYZ', 1, 1)
limit_sell = remote_agent.limit_sell('XYZ', 1, 1)

get_price_bars = remote_agent.get_price_bars('XYZ', '1D', 20)


#TODO: need to save order_ids in remtoe_agent
# cancel_order = remote_agent.cancel_order()

#TODO: register remote agent with the exchange
# cancel_all_orders = remote_agent.cancel_all_orders('XYZ')


print("last_trade", last_trade)
print("best_bid", best_bid)
print("midprice", remote_agent.get_midprice('XYZ'))
print("order_book", order_book)
print("quotes", quotes)
print("trades", trades)
print("market_buy", market_buy)
print("market_sell", market_sell)
print("limit_buy", limit_buy)
print("limit_sell", limit_sell)
# print("cancel_order", cancel_order)
# print("cancel_all_orders", cancel_all_orders)
print("get_price_bars", get_price_bars)
