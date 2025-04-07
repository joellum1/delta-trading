from src.tutorial.datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import string
from logger import Logger
import jsonpickle

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
            rainforest_resin_orders = self.rainforest_resin_orders(
                state.order_depths[Item.RAINFOREST_RESIN],
                state.position[Item.RAINFOREST_RESIN],
                rainforest_resin_position
            )
            
            result[Item.RAINFOREST_RESIN] = rainforest_resin_orders

        if Item.KELP in state.order_depths:
            kelp_position = state.position[Item.KELP] if Item.KELP in state.position else 0
            kelp_orders = self.kelp_orders(
                state.order_depths[Item.KELP],
                state.position[Item.KELP],
                kelp_position
            )

            result[Item.KELP] = kelp_orders

        if Item.SQUID_INK in state.order_depths:
            squid_ink_position = state.position[Item.SQUID_INK] if Item.SQUID_INK in state.position else 0
            squid_ink_orders = self.squid_ink_orders(
                state.order_depths[Item.SQUID_INK],
                state.position[Item.SQUID_INK],
                squid_ink_position
            )

            result[Item.SQUID_INK] = squid_ink_orders
    
        # Store trader data with new information
        traderData = jsonpickle.encode(trader_data)
        
		# Sample conversion request. Check more details below. 
        conversions = 1

        # Log data for visualisation efforts
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
    
    def kelp_orders(self, order_depth: OrderDepth, position: int, position_limit: int):
        orders: List[Order] = []
        product: Item = Item.KELP

        # TODO: Calculate acceptable price for KELP
        acceptable_price = 10  # Participant should calculate this value

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
    
    def squid_ink_orders(self, order_depth: OrderDepth, position: int, position_limit: int):
        orders: List[Order] = []
        product: Item = Item.SQUID_INK

        # TODO: Calculate acceptable price for SQUID_INK
        acceptable_price = 10  # Participant should calculate this value

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