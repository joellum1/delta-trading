from datamodel import OrderDepth, UserId, TradingState, Order, Symbol, Listing, Trade, Observation, ProsperityEncoder
from typing import List, Any
import string
import jsonpickle
import heapq
import json
import pandas as pd

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
    CROISSANT = 'CROISSANT'
    JAM = 'JAM'
    DJEMBE = 'DJEMBE'
    PICNIC_BASKET1 = 'PICNIC_BASKET1'
    PICNIC_BASKET2 = 'PICNIC_BASKET2'

class Trader:
    def __init__(self):
        self.VALUE = {}
        self.LIMIT = {
            'RAINFOREST_RESIN': 50,
            'KELP': 50,
            'SQUID_INK': 50,
            'CROISSANT': 250,
            'JAM': 350,
            'DJEMBE': 60,
            'PICNIC_BASKET1': 60,
            'PICNIC_BASKET2': 100
        }
        # update based on trades!
        # portfolio value = cash + value of stocks but fixed for simplicity
        # no change when buying, if sell for profit, then increase but if sell for loss decrease
        self.portfolio_size = 44340
        self.risk_percent = 0.01
        self.stop_loss_percent = 0.02
        self.df = pd.read_csv('round-2-island-data-bottle/prices_round_2_day_-1.csv', sep=";")

    def moving_average(self, product: str):
        short_window = 50
        long_window = 200

        product_df = self.df[self.df['product'] == product].copy()
        product_df = product_df.sort_values(by='timestamp')

        product_df['short_ma'] = product_df['mid_price'].rolling(window=short_window, min_periods=1).mean()
        product_df['long_ma'] = product_df['mid_price'].rolling(window=long_window, min_periods=1).mean()
        return product['short_ma'], product_df['long_ma']

    # update the data frame so that average values can be calculated
    def update_df(self, product: str, timestamp, bid_price, ask_price):
        mid_price = (bid_price + ask_price) / 2
        new_row = {
            'timestamp': timestamp,
            'product': product,
            'bid price': bid_price,
            'mid price': mid_price,
            'ask price': ask_price
        }
        self.df.concat([self.df, pd.DataFrame([new_row])], ignore_index=True)

    # calculate how much of an item we should buy
    def position_size(self, entry_price):
        stop_loss_price = entry_price * (1 - self.stop_loss_percent)
        risk_per_trade = self.portfolio_size * self.risk_percent
        risk_per_share = entry_price - stop_loss_price
        
        if risk_per_share == 0:
            return 0
        return risk_per_trade / risk_per_share
    
    def make_orders(self, product: str, order_depth: OrderDepth, position: int, position_limit: int, timestamp):
        short_ma, long_ma = self.moving_average(self, product)

        add_buy_vol = 0
        add_sell_vol = 0

        orders: List[Order] = []
        best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]
        best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]
        mid_price = (best_ask + best_bid) / 2
        self.update_df(self, product, timestamp, best_bid, best_ask)
        # buy
        if (short_ma > long_ma):
            buy_position = min(self.position_size(self, best_ask), position_limit - position)
            orders.append(Order(product, mid_price, buy_position))
            add_buy_vol += buy_position

        # sell
        if (short_ma < long_ma):
            sell_position = min(self.position_size(self, best_bid), position_limit - position)
            orders.append(Order(product, mid_price, -sell_position))
            add_sell_vol += sell_position
        
        return orders

    def croissant_orders(self, order_depth: OrderDepth, position: int, position_limit: int, acceptable_price: int):
        orders: List[Order] = []
        product: Item = Item.CROISSANT

        print("CROISSANT")
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

    def run(self, state: TradingState):
        # Get data from previous iteration
        trader_data = {}
        if state.traderData != None and state.traderData != "": trader_data = jsonpickle.decode(state.traderData)

		# Orders to be placed on exchange matching engine
        result = {}

        if Item.RAINFOREST_RESIN in state.order_depths:
            resin_position = state.position[Item.RAINFOREST_RESIN] if Item.RAINFOREST_RESIN in state.position else 0
            
            result[Item.RAINFOREST_RESIN] = self.make_orders(
                order_depth=state.order_depths[Item.RAINFOREST_RESIN],
                position=resin_position,
                position_limit=self.LIMIT[Item.RAINFOREST_RESIN],
                timestamp=state.timestamp
            )

        if Item.KELP in state.order_depths:
            kelp_position = state.position[Item.KELP] if Item.KELP in state.position else 0
            
            result[Item.KELP] = self.make_orders(
                order_depth=state.order_depths[Item.KELP],
                position=kelp_position,
                position_limit=self.LIMIT[Item.KELP],
                timestamp=state.timestamp
            )

        if Item.SQUID_INK in state.order_depths:
            ink_position = state.position[Item.SQUID_INK] if Item.SQUID_INK in state.position else 0
            
            result[Item.SQUID_INK] = self.make_orders(
                order_depth=state.order_depths[Item.SQUID_INK],
                position=ink_position,
                position_limit=self.LIMIT[Item.SQUID_INK],
                timestamp=state.timestamp
            )

        if Item.CROISSANT in state.order_depths:
            croissant_position = state.position[Item.CROISSANT] if Item.CROISSANT in state.position else 0

            # Calculate acceptable price
            # croissant_ap = 1
            
            # result[Item.CROISSANT] = self.croissant_orders(
            #     order_depth=state.order_depths[Item.CROISSANT],
            #     position=croissant_position,
            #     position_limit=self.LIMIT[Item.CROISSANT],
            #     acceptable_price=croissant_ap
            # )
            result[Item.CROISSANT] = self.make_orders(
                product=Item.CROISSANT,
                order_depth=state.order_depths[Item.CROISSANT],
                position=croissant_position,
                position_limit=self.LIMIT[Item.CROISSANT],
                timestamp=state.timestamp
            )

        if Item.JAM in state.order_depths:
            jam_position = state.position[Item.JAM] if Item.JAM in state.position else 0
            
            result[Item.JAM] = self.make_orders(
                order_depth=state.order_depths[Item.JAM],
                position=jam_position,
                position_limit=self.LIMIT[Item.JAM],
                timestamp=state.timestamp
            )

        if Item.DJEMBE in state.order_depths:
            djembe_position = state.position[Item.DJEMBE] if Item.DJEMBE in state.position else 0
            
            result[Item.DJEMBE] = self.make_orders(
                order_depth=state.order_depths[Item.DJEMBE],
                position=djembe_position,
                position_limit=self.LIMIT[Item.DJEMBE],
                timestamp=state.timestamp
            )

        if Item.PICNIC_BASKET1 in state.order_depths:
            basket1_position = state.position[Item.PICNIC_BASKET1] if Item.PICNIC_BASKET1 in state.position else 0
            
            result[Item.PICNIC_BASKET1] = self.make_orders(
                order_depth=state.order_depths[Item.PICNIC_BASKET1],
                position=basket1_position,
                position_limit=self.LIMIT[Item.PICNIC_BASKET1],
                timestamp=state.timestamp
            )

        if Item.PICNIC_BASKET2 in state.order_depths:
            basket2_position = state.position[Item.PICNIC_BASKET2] if Item.PICNIC_BASKET2 in state.position else 0
            
            result[Item.PICNIC_BASKET2] = self.make_orders(
                order_depth=state.order_depths[Item.PICNIC_BASKET2],
                position=basket2_position,
                position_limit=self.LIMIT[Item.PICNIC_BASKET2],
                timestamp=state.timestamp
            )

        # Store trader data with new information
        traderData = jsonpickle.encode(trader_data)
        
		# Sample conversion request. Check more details below. 
        conversions = 1

        # Log data for visualisation efforts
        logger.flush(state, result, conversions, traderData)

        return result, conversions, traderData