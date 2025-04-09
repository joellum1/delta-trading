from src.tutorial.datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import string
from logger import Logger
import jsonpickle
import heapq

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
        order_depth,
        buy_volume,
        sell_volume,
        min_bid,
        max_ask
    ) -> (List[Order], int, int):
        curr_position = position + buy_volume - sell_volume

        buy_quantity = self.LIMIT[product] - (position + buy_volume)
        sell_quantity = self.LIMIT[product] - (position + sell_volume)

        orders = []
        
        # if there is more to sell, create buy orders
        if curr_position > 0:
            to_sell = []
            for price, volume in order_depth.buy_orders.items():
                if price >= min_bid:
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

        if curr_position < 0:
            to_buy = []
            for price, volume in order_depth.sell_orders.items():
                if price <= max_ask:
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
    
    def run(self, state: TradingState):
        # Get data from previous iteration
        trader_data = {}
        if state.get(traderData) != None and state.traderData != "":
            trader_data = jsonpickle.decode(state.traderData)

        print("traderData: " + state.traderData)
        print("Observations: " + str(state.observations))

		# Orders to be placed on exchange matching engine
        result = {}

        if Item.RAINFOREST_RESIN in state.order_depths:
            rainforest_resin_position = state.position[Item.RAINFOREST_RESIN] if Item.RAINFOREST_RESIN in state.position else 0
            rainforest_resin_acceptable_price = 10000     # Rainforest resin is said to be stable in price
            rainforest_resin_orders = self.rainforest_resin_orders(
                order_depth=state.order_depths[Item.RAINFOREST_RESIN],
                position=state.position[Item.RAINFOREST_RESIN],
                position_limit=rainforest_resin_position,
                acceptable_price=rainforest_resin_acceptable_price
            )
            
            result[Item.RAINFOREST_RESIN] = rainforest_resin_orders

        if Item.KELP in state.order_depths:
            kelp_position = state.position[Item.KELP] if Item.KELP in state.position else 0
            kelp_acceptable_price = self.calc_kelp_ap(
                order_depth=state.order_depths[Item.KELP], 
                trader_data=trader_data
            )
            kelp_orders = self.kelp_orders(
                order_depth=state.order_depths[Item.KELP],
                position=state.position[Item.KELP],
                position_limit=kelp_position,
                acceptable_price=kelp_acceptable_price
            )

            result[Item.KELP] = kelp_orders

        if Item.SQUID_INK in state.order_depths:
            squid_ink_position = state.position[Item.SQUID_INK] if Item.SQUID_INK in state.position else 0
            squid_ink_acceptable_price = 10     # TODO: Calculate acceptable price for squid ink
            squid_ink_orders = self.squid_ink_orders(
                order_depth=state.order_depths[Item.SQUID_INK],
                position=state.position[Item.SQUID_INK],
                position_limit=squid_ink_position,
                acceptable_price=squid_ink_acceptable_price
            )

            result[Item.SQUID_INK] = squid_ink_orders
    
        # Store trader data with new information
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
        orders: List[Order] = []
        product: Item = Item.KELP

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
    
    def calc_kelp_ap(self, order_depth: OrderDepth, trader_data):
        # TODO: Calculate acceptable price for kelp
        return 0
    
    def squid_ink_orders(self, order_depth: OrderDepth, position: int, position_limit: int, acceptable_price: int):
        orders: List[Order] = []
        product: Item = Item.SQUID_INK

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