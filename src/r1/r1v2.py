from datamodel import OrderDepth, UserId, TradingState, Order, Symbol, Listing, Trade, Observation, ProsperityEncoder
from typing import List
import string
# from logger import Logger
import jsonpickle
import heapq
 
from typing import Any
import json

class Logger:
    def __init__(self) -> None:
        self.logs = ""
        self.max_log_length = 3750

    def print(self, *objects: Any, sep: str = " ", end: str = "\n") -> None:
        self.logs += sep.join(map(str, objects)) + end

    def flush(self, state: TradingState, orders: dict[Symbol, list[Order]], conversions: int, trader_data: str) -> None:
        base_length = len(
            self.to_json(
                [
                    self.compress_state(state, ""),
                    self.compress_orders(orders),
                    conversions,
                    "",
                    "",
                ]
            )
        )

        # We truncate state.traderData, trader_data, and self.logs to the same max. length to fit the log limit
        max_item_length = (self.max_log_length - base_length) // 3

        print(
            self.to_json(
                [
                    self.compress_state(state, self.truncate(state.traderData, max_item_length)),
                    self.compress_orders(orders),
                    conversions,
                    self.truncate(trader_data, max_item_length),
                    self.truncate(self.logs, max_item_length),
                ]
            )
        )

        self.logs = ""

    def compress_state(self, state: TradingState, trader_data: str) -> list[Any]:
        return [
            state.timestamp,
            trader_data,
            self.compress_listings(state.listings),
            self.compress_order_depths(state.order_depths),
            self.compress_trades(state.own_trades),
            self.compress_trades(state.market_trades),
            state.position,
            self.compress_observations(state.observations),
        ]

    def compress_listings(self, listings: dict[Symbol, Listing]) -> list[list[Any]]:
        compressed = []
        for listing in listings.values():
            compressed.append([listing.symbol, listing.product, listing.denomination])

        return compressed

    def compress_order_depths(self, order_depths: dict[Symbol, OrderDepth]) -> dict[Symbol, list[Any]]:
        compressed = {}
        for symbol, order_depth in order_depths.items():
            compressed[symbol] = [order_depth.buy_orders, order_depth.sell_orders]

        return compressed

    def compress_trades(self, trades: dict[Symbol, list[Trade]]) -> list[list[Any]]:
        compressed = []
        for arr in trades.values():
            for trade in arr:
                compressed.append(
                    [
                        trade.symbol,
                        trade.price,
                        trade.quantity,
                        trade.buyer,
                        trade.seller,
                        trade.timestamp,
                    ]
                )

        return compressed

    def compress_observations(self, observations: Observation) -> list[Any]:
        conversion_observations = {}
        for product, observation in observations.conversionObservations.items():
            conversion_observations[product] = [
                observation.bidPrice,
                observation.askPrice,
                observation.transportFees,
                observation.exportTariff,
                observation.importTariff,
                observation.sugarPrice,
                observation.sunlightIndex,
            ]

        return [observations.plainValueObservations, conversion_observations]

    def compress_orders(self, orders: dict[Symbol, list[Order]]) -> list[list[Any]]:
        compressed = []
        for arr in orders.values():
            for order in arr:
                compressed.append([order.symbol, order.price, order.quantity])

        return compressed

    def to_json(self, value: Any) -> str:
        return json.dumps(value, cls=ProsperityEncoder, separators=(",", ":"))

    def truncate(self, value: str, max_length: int) -> str:
        if len(value) <= max_length:
            return value

        return value[: max_length - 3] + "..."

# Create logs for visualisation
logger = Logger()

class Item:
    RAINFOREST_RESIN = 'RAINFOREST_RESIN'
    KELP = 'KELP'
    SQUID_INK = 'SQUID_INK'

class Trader:

    def __init__(self):
        self.VALUE = {
            'RAINFOREST_RESIN': 10000,
            'KELP': 2000,
            'SQUID_INK': 2000
        }
        self.LIMIT = {
            'RAINFOREST_RESIN': 50,
            'KELP': 50,
            'SQUID_INK': 50
        }

    # want to be at position 0!
    def clear_orders(
        self,
        product: str,
        order_depth: OrderDepth,
        position: int,
        buy_volume: int,
        sell_volume: int,
        min_bid: int,   # Minimum price we would take to sell to someone
        max_ask: int    # Maximum price we would pay to buy from someone
    ) -> (List[Order], int, int):
        curr_position = position + buy_volume - sell_volume

        buy_quantity = self.LIMIT[product] - (position + buy_volume)
        sell_quantity = self.LIMIT[product] - (position + sell_volume)

        orders = []
        
        # if there is more to sell, create buy orders
        if curr_position > 0:
            to_sell = []
            for price, volume in order_depth.buy_orders.items():
                if price > min_bid:
                    heapq.heappush(to_sell, (-price, volume))
            while (sell_quantity > 0 and to_sell):
                price, volume = heapq.heappop(to_sell)
                price = -price
                # can sell volume amount
                if (sell_quantity >= volume):
                    orders.append(Order(product, price, -volume))
                    sell_quantity -= volume
                    sell_volume += volume
                else:
                    orders.append(Order(product, price, -sell_quantity))
                    sell_volume += sell_quantity
                    break
        
        # if we've bought a bunch, create sell orders
        if curr_position < 0:
            to_buy = []
            for price, volume in order_depth.sell_orders.items():
                if price < max_ask:
                    heapq.heappush(to_buy, (price, volume))
            while (buy_quantity > 0 and to_buy):
                price, volume = heapq.heappop(to_buy)
                if (buy_quantity >= volume):
                    orders.append(Order(product, price, volume))
                    buy_quantity -= volume
                    buy_volume += volume
                else:
                    orders.append(Order(product, price, buy_quantity))
                    buy_volume += buy_quantity
                    break

        return orders, buy_volume, sell_volume
    
    def fill_market_orders(self, product: str, order_depth: OrderDepth, position: int, position_limit: int, acceptable_price: int):
        orders: List[Order] = []
        position_limit = self.LIMIT[product]
        add_buy_vol = 0
        add_sell_vol = 0

        if len(order_depth.sell_orders) != 0:
            best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]
            best_ask_amount = abs(best_ask_amount)  # Convert to positive value
            if int(best_ask) < acceptable_price:
                print("BUY", str(best_ask_amount) + "x", best_ask)
                ask_qty = min(best_ask_amount, position_limit - position)
                
                if ask_qty > 0: # Check if we have room to buy
                    orders.append(Order(product, best_ask, ask_qty))
                    add_buy_vol += ask_qty

        if len(order_depth.buy_orders) != 0:
            best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]
            if int(best_bid) > acceptable_price:
                print("SELL", str(best_bid_amount) + "x", best_bid)
                bid_qty = min(best_bid_amount, position_limit - position)

                if bid_qty > 0: # Check if we have room to sell
                    orders.append(Order(product, best_bid, -bid_qty))
                    add_sell_vol += bid_qty
                    
        return orders, add_buy_vol, add_sell_vol
    
    def run(self, state: TradingState):
        # Get data from previous iteration
        trader_data = {}
        if state.traderData != None and state.traderData != "":
            trader_data = jsonpickle.decode(state.traderData)

        print("traderData: " + state.traderData)
        print("Observations: " + str(state.observations))

		# Orders to be placed on exchange matching engine
        result = {}

        if Item.RAINFOREST_RESIN in state.order_depths:
            rainforest_resin_position = state.position[Item.RAINFOREST_RESIN] if Item.RAINFOREST_RESIN in state.position else 0
            # rainforest_resin_acceptable_price = 10000     # Rainforest resin is said to be stable in price
            rainforest_resin_orders = self.rainforest_resin_orders(
                order_depth=state.order_depths[Item.RAINFOREST_RESIN],
                position=rainforest_resin_position,
                position_limit=self.LIMIT[Item.RAINFOREST_RESIN],
                acceptable_price=self.VALUE[Item.RAINFOREST_RESIN]
            )
            
            result[Item.RAINFOREST_RESIN] = rainforest_resin_orders

        if Item.KELP in state.order_depths:
            kelp_position = state.position[Item.KELP] if Item.KELP in state.position else 0

            prev_bid_ask = trader_data.get(state.timestamp - 100, None)
            if prev_bid_ask is not None:
                prev_bid, prev_ask = prev_bid_ask
                self.VALUE[Item.KELP] = (prev_bid + prev_ask) / 2

            result[Item.KELP] = self.kelp_orders(
                order_depth=state.order_depths[Item.KELP],
                position=kelp_position,
                position_limit=self.LIMIT[Item.KELP],
                acceptable_price=self.VALUE[Item.KELP]
            )

        if Item.SQUID_INK in state.order_depths:
            squid_ink_position = state.position[Item.SQUID_INK] if Item.SQUID_INK in state.position else 0
            
            prev_bid_ask = trader_data.get(state.timestamp - 100, None)
            if prev_bid_ask is not None:
                prev_bid, prev_ask = prev_bid_ask
                self.VALUE[Item.SQUID_INK] = (prev_bid + prev_ask) / 2

            result[Item.SQUID_INK] = self.squid_ink_orders(
                order_depth=state.order_depths[Item.SQUID_INK],
                position=squid_ink_position,
                position_limit=self.LIMIT[Item.SQUID_INK],
                acceptable_price=self.VALUE[Item.SQUID_INK]
            )
    
        # Store trader data with new information
        if state.order_depths[Item.KELP] is not None:
            trader_data[state.timestamp] = {}
            trader_data[state.timestamp][Item.KELP] = (list(state.order_depths[Item.KELP].buy_orders.items())[0][0], list(state.order_depths[Item.KELP].sell_orders.items())[0][0])
        
        if state.order_depths[Item.SQUID_INK] is not None:
            trader_data[state.timestamp] = {}
            trader_data[state.timestamp][Item.SQUID_INK] = (list(state.order_depths[Item.SQUID_INK].buy_orders.items())[0][0], list(state.order_depths[Item.SQUID_INK].sell_orders.items())[0][0])

        if len(trader_data) > 5000:
            del trader_data[next(iter(trader_data))]

        traderData = jsonpickle.encode(trader_data)
        
		# Sample conversion request. Check more details below. 
        conversions = 1

        # Log data for visualisation efforts
        logger.flush(state, result, conversions, traderData)

        return result, conversions, traderData
    
    def rainforest_resin_orders(self, order_depth: OrderDepth, position: int, position_limit: int, acceptable_price: int):
        orders: List[Order] = []
        product: Item = Item.RAINFOREST_RESIN

        print("Acceptable price : " + str(acceptable_price))
        print("Buy Order depth : " + str(len(order_depth.buy_orders)) + ", Sell order depth : " + str(len(order_depth.sell_orders)))

        if len(order_depth.sell_orders) != 0:
            best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]
            best_ask_amount = abs(best_ask_amount)  # Convert to positive value
            if int(best_ask) < acceptable_price:
                print("BUY", str(best_ask_amount) + "x", best_ask)
                orders.append(Order(product, best_ask, best_ask_amount))

        if len(order_depth.buy_orders) != 0:
            best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]
            if int(best_bid) > acceptable_price:
                print("SELL", str(best_bid_amount) + "x", best_bid)
                orders.append(Order(product, best_bid, -best_bid_amount))
        
        return orders
    
    def kelp_orders(self, order_depth: OrderDepth, position: int, position_limit: int, acceptable_price: int):
        product: Item = Item.KELP

        fill_orders, buy_vol, sell_vol = self.fill_market_orders(
            product=product,
            order_depth=order_depth,
            position=position,
            position_limit=position_limit,
            acceptable_price=acceptable_price
        )

        clear_orders, buy_vol, sell_vol = self.clear_orders(
            product=product,
            order_depth=order_depth,
            position=position,
            buy_volume=buy_vol,
            sell_volume=sell_vol,
            min_bid=acceptable_price,
            max_ask=acceptable_price
        )
        
        return fill_orders + clear_orders
    
    def squid_ink_orders(self, order_depth: OrderDepth, position: int, position_limit: int, acceptable_price: int):
        product: Item = Item.SQUID_INK

        print("Acceptable price : " + str(acceptable_price))
        print("Buy Order depth : " + str(len(order_depth.buy_orders)) + ", Sell order depth : " + str(len(order_depth.sell_orders)))

        fill_orders, buy_vol, sell_vol = self.fill_market_orders(
            product=product,
            order_depth=order_depth,
            position=position,
            position_limit=position_limit,
            acceptable_price=acceptable_price
        )

        clear_orders, buy_vol, sell_vol = self.clear_orders(
            product=product,
            order_depth=order_depth,
            position=position,
            buy_volume=buy_vol,
            sell_volume=sell_vol,
            min_bid=acceptable_price,
            max_ask=acceptable_price
        )
        
        return fill_orders + clear_orders