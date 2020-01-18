import action_choices
# all decision_agent functions MUST have this signature, and in particular, the first argument is always a player object
# all make_*_move functions must return
# a tuple, namely the function in action_choices to execute and a dictionary (the parameters to pass into the function)

# the code parameter is used to provide some state (the decision agent is free to maintain its own state/history however)
# if the code is 0, then this is the first time the player is being called upon to select a move (in this turn), otherwise
# if code is 1 it means the 'previous' move selected by the player was successful, if -1 it means it was unsuccessful
# code of -1 is usually returned when an allowable move is invoked with parameters that preempt the action from happening
# for example, the player may decide to mortgage property that is already mortgaged, which will return the failure code
# when the game actually tries to mortgage the property in action_choices.

def handle_negative_cash_balance(player, current_gameboard):
    return -1 # we don't try; a more graceful agent may try mortgaging/selling.
    # if you attempt an action, you should return 1. The simulator does an additional check to see if you were able
    # to restore cash balance to 0 or above; if not, bankruptcy proceedings begin.


def make_pre_roll_move(player, current_gameboard, allowable_moves, code):
    if action_choices.skip_turn in allowable_moves:
        return (action_choices.skip_turn, dict())
    else:
        raise Exception

# def make_pre_roll_continuing_move(player, current_gameboard, allowable_moves):
#     if action_choices.skip_turn in allowable_moves:
#         action_choices.skip_turn()
#     else:
#         raise Exception

def make_out_of_turn_move(player, current_gameboard, allowable_moves, code):
    if action_choices.skip_turn in allowable_moves:
        return (action_choices.skip_turn, dict())
    else:
        raise Exception

# def make_out_of_turn_continuing_move(player, current_gameboard, allowable_moves):
#     if action_choices.skip_turn in allowable_moves:
#         action_choices.skip_turn()
#     else:
#         raise Exception

def make_post_roll_move(player, current_gameboard, allowable_moves, code):
    if action_choices.buy_property in allowable_moves:
        params = dict()
        params['player'] = player
        params['asset'] = current_gameboard['location_sequence'][player.current_position]
        params['current_gameboard'] = current_gameboard
        return (action_choices.buy_property, params)
    elif action_choices.concluded_actions in allowable_moves:
        return (action_choices.concluded_actions, dict())
    else:
        raise Exception


def make_buy_property_decision(player, current_gameboard, asset):
    """
    :param player:
    :param current_gameboard:
    :return: true or false, depending on whether player wants to purchase asset.
    """
    decision = False
    if player.current_cash >= asset.price:
        decision = True
    return decision


def make_bid(player, current_gameboard, asset, current_bid):
    # expected return is what you wish to bid.
    # we do not use current_gameboard in our simple decision agent, but that does not mean your decision agent can't!
    if current_bid < asset.price:
        new_bid = current_bid + (asset.price-current_bid)/2
        if new_bid < player.current_cash:
            return new_bid
        else:
            return 0 # this will lead to a rejection of the bid downstream automatically
    else:
        return 0 # we never bid more than the price of the asset

    # We are aware that this can be simplified with a simple return 0 statement at the end. However in the final baseline agent
    # the return 0's would be replaced with more sophisticated rules. Think of them as placeholders.


def _build_decision_agent_methods_dict():
    ans = dict()
    ans['handle_negative_cash_balance'] = handle_negative_cash_balance
    ans['make_pre_roll_move'] = make_pre_roll_move
    ans['make_out_of_turn_move'] =  make_out_of_turn_move
    ans['make_post_roll_move'] = make_post_roll_move
    ans['make_buy_property_decision'] = make_buy_property_decision
    ans['make_bid'] = make_bid
    return ans


decision_agent_methods = _build_decision_agent_methods_dict() # this is the main data structure that is needed by gameplay


