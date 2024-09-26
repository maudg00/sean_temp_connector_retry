from copy import copy
import time
import sys
from connector import ConnectorSterling

# hardcode the account
ACCOUNT = "asdf" # "ASDF" live, "JKL" demo

# expiry date of the option
DATE = '240927' # date in format %y%m%d

def buy_option(con: ConnectorSterling, amount: int, option_type: str, strike: int) -> None:
    """
    Buy a specified amount of options of a given type.

    :param con: a connection to Sterling Trader Pro
    :param amount: The amount of options to buy.
    :param option_type: The type of option to buy, either 'C' or 'P'.
    :param strike: The strike price of the option to buy.
    """

    # create a copy of amount
    quantity = copy(amount)

    # convert into a dictionary which holds everything
    contract = dict(
                    side='B',
                    symbol='',
                    account=ACCOUNT,
                    tif='D', # D for day
                    quantity=quantity,
                    destination='SENSOR', # 'SENSOR' live, 'CBOE' demo, # used to be 'VTRDOPT'
                    lmt_price=0.05,
                    open_close='O',
                    maturity=f'20{DATE}',
                    put_call=option_type,
                    underlying='SPXW',
                    cover_uncover='U',
                    instrument='O',
                    strike=15
                    )

    # Loop until we have bought the specified amount of options
    while quantity > 0:
        
        # update the symbol/strike
        contract['symbol'] = f'SPXW {DATE}{option_type}{strike}000'
        contract['strike'] = strike

        # update the quantity for the option
        contract['quantity'] = quantity

        # place the order
        ordId, status = con.send_option_limit( # pass the dictionary to the send_option_limit function
                            **contract
                            )

        # wait 5 seconds for the order to fill
        for _ in range(5):
            order_status = con.order_status(ordId)
            print(order_status)
            if order_status == 5: # means order is completely filled
                break
            time.sleep(1)

        # if the order is not filled, cancel the order
        if not con.order_status(ordId) == 5:
            con.cancel_options_order(ACCOUNT, ordId)
            time.sleep(1)
            ordId += 'cancel'
            print('order status after cancel: ', con.order_status(ordId))
            assert con.order_status(ordId) == 8
        else:
            assert con.order_status(ordId) == 5

        # check if there's any trades
        num_trades = con.fill_qty(ordId)
        if num_trades == 0:
            continue

        # print the trade to the console
        print(f"option bought {num_trades} {option_type} {strike}")

        # modify quantity and if it's greater than 0, repeat loop
        quantity -= num_trades
        
    return


if __name__ == "__main__":
    try:
        con = ConnectorSterling(verbose=False)
    except Exception as e:
        print(f"Error: {e}")
        print("Exiting program as all tries have been used. Check sterling app and other connections.")
        sys.exit(1)
    
    # buy amount options to buy
    amount = 1
    option_type = 'C' # 'P' for put, 'C' for call
    strike = 5685

    buy_option(con, amount, option_type, strike)
