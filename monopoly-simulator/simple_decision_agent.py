import action_choices

def handle_negative_cash_balance(player, current_gameboard):
    return -1 # we don't try; a more graceful agent may try mortgaging/selling.
    # if you attempt an action, you should return 1. The simulator does an additional check to see if you were able
    # to restore cash balance to 0 or above; if not, bankruptcy proceedings begin.


def make_pre_roll_initial_move(player, current_gameboard, allowable_moves):
    if action_choices.skip_turn in allowable_moves:
        action_choices.skip_turn()
    else:
        raise Exception

def make_pre_roll_continuing_move(player, current_gameboard, allowable_moves):
    if action_choices.skip_turn in allowable_moves:
        action_choices.skip_turn()
    else:
        raise Exception

def make_out_of_turn_initial_move(player, current_gameboard, allowable_moves):
    if action_choices.skip_turn in allowable_moves:
        action_choices.skip_turn()
    else:
        raise Exception

def make_out_of_turn_continuing_move(player, current_gameboard, allowable_moves):
    if action_choices.skip_turn in allowable_moves:
        action_choices.skip_turn()
    else:
        raise Exception

def make_post_roll_move(player, current_gameboard, allowable_moves):
    if action_choices.concluded_actions in allowable_moves:
        action_choices.concluded_actions()
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


def _build_decision_agent_methods_dict():
    ans = dict()
    ans['handle_negative_cash_balance'] = handle_negative_cash_balance
    ans['make_pre_roll_initial_move'] = make_pre_roll_initial_move
    ans['make_pre_roll_continuing_move'] = make_pre_roll_continuing_move
    ans['make_out_of_turn_initial_move'] =  make_out_of_turn_initial_move
    ans['make_out_of_turn_continuing_move'] = make_out_of_turn_continuing_move
    ans['make_post_roll_move'] = make_post_roll_move
    ans['make_buy_property_decision'] = make_buy_property_decision
    ans['make_bid'] = make_bid
    return ans


decision_agent_methods = _build_decision_agent_methods_dict() # this is the main data structure that is needed by gameplay


