from src.tutorial.datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import string
from logger import Logger

# Create logs for visualisation
logger = Logger()

class Item:
    RAINFOREST_RESIN = 'RAINFOREST_RESIN'
    KELP = 'KELP'
    SQUID_INK = 'SQUID_INK'

class Trader:
    
    def run(self, state: TradingState):
        print("traderData: " + state.traderData)
        print("Observations: " + str(state.observations))

		# Orders to be placed on exchange matching engine
        result = {}

        for product in state.order_depths:
            if product == Item.RAINFOREST_RESIN:
                order_depth: OrderDepth = state.order_depths[Item.RAINFOREST_RESIN]
                rainforest_resin_orders = self.rainforest_resin_orders()
                result[Item.RAINFOREST_RESIN] = rainforest_resin_orders

            elif product == Item.KELP:
                order_depth: OrderDepth = state.order_depths[Item.KELP]
                kelp_orders = self.kelp_orders()
                result[Item.KELP] = kelp_orders

            elif product == Item.SQUID_INK:
                order_depth: OrderDepth = state.order_depths[Item.SQUID_INK]
                squid_ink_orders = self.squid_ink_orders()
                result[Item.SQUID_INK] = squid_ink_orders
    
	    # String value holding Trader state data required. 
		# It will be delivered as TradingState.traderData on next execution.
        traderData = "SAMPLE" 
        
		# Sample conversion request. Check more details below. 
        conversions = 1
        logger.flush(state, result, conversions, traderData)
        return result, conversions, traderData
    
    def rainforest_resin_orders(self, order_depth: OrderDepth, position: int, position_limit: int):
        orders: List[Order] = []
        product: Item = Item.RAINFOREST_RESIN

        # TODO: Calculate acceptable price for RAINFOREST_RESIN
        acceptable_price = 10  # Participant should calculate this value

        print("Acceptable price : " + str(acceptable_price))
        print("Buy Order depth : " + str(len(order_depth.buy_orders)) + ", Sell order depth : " + str(len(order_depth.sell_orders)))

        if len(order_depth.sell_orders) != 0:
            best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]
            if int(best_ask) < acceptable_price:
                print("BUY", str(-best_ask_amount) + "x", best_ask)
                orders.append(Order(product, best_ask, -best_ask_amount))

        if len(order_depth.buy_orders) != 0:
            best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]
            if int(best_bid) > acceptable_price:
                print("SELL", str(best_bid_amount) + "x", best_bid)
                orders.append(Order(product, best_bid, -best_bid_amount))
        
        return orders
    
    def kelp_orders(self, order_depth: OrderDepth, position: int, position_limit: int):
        orders: List[Order] = []
        product: Item = Item.KELP

        # TODO: Calculate acceptable price for KELP
        acceptable_price = 10  # Participant should calculate this value

        print("Acceptable price : " + str(acceptable_price))
        print("Buy Order depth : " + str(len(order_depth.buy_orders)) + ", Sell order depth : " + str(len(order_depth.sell_orders)))

        if len(order_depth.sell_orders) != 0:
            best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]
            if int(best_ask) < acceptable_price:
                print("BUY", str(-best_ask_amount) + "x", best_ask)
                orders.append(Order(product, best_ask, -best_ask_amount))

        if len(order_depth.buy_orders) != 0:
            best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]
            if int(best_bid) > acceptable_price:
                print("SELL", str(best_bid_amount) + "x", best_bid)
                orders.append(Order(product, best_bid, -best_bid_amount))
        
        return orders
    
    def squid_ink_orders(self, order_depth: OrderDepth, position: int, position_limit: int):
        orders: List[Order] = []
        product: Item = Item.SQUID_INK

        # TODO: Calculate acceptable price for SQUID_INK
        acceptable_price = 10  # Participant should calculate this value

        print("Acceptable price : " + str(acceptable_price))
        print("Buy Order depth : " + str(len(order_depth.buy_orders)) + ", Sell order depth : " + str(len(order_depth.sell_orders)))

        if len(order_depth.sell_orders) != 0:
            best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]
            if int(best_ask) < acceptable_price:
                print("BUY", str(-best_ask_amount) + "x", best_ask)
                orders.append(Order(product, best_ask, -best_ask_amount))

        if len(order_depth.buy_orders) != 0:
            best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]
            if int(best_bid) > acceptable_price:
                print("SELL", str(best_bid_amount) + "x", best_bid)
                orders.append(Order(product, best_bid, -best_bid_amount))
        
        return orders