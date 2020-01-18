import sys


def go_to_jail(player, current_gameboard):
    jail_position = current_gameboard['jail_position']
    player.currently_in_jail = True
    player.current_position = jail_position

def pick_card_from_community_chest(player, current_gameboard): # it will pick the card and execute the action
    # get_out_of_jail_free card is treated a little differently, since we must remove it from the card pack.
    card = current_gameboard['choice_function'](list(current_gameboard['community_chest_cards']))
    if card.name == 'get_out_of_jail_free':
        current_gameboard['community_chest_cards'].remove(card)
    card.action(player, card, current_gameboard) # all card actions must take this signature


def pick_card_from_chance(player, current_gameboard): # it will pick the card and execute the action
    # get_out_of_jail_free card is treated a little differently, since we must remove it from the card pack.
    card = current_gameboard['choice_function'](list(current_gameboard['chance_cards']))
    if card.name == 'get_out_of_jail_free':
        current_gameboard['chance_cards'].remove(card)
    card.action(player, card, current_gameboard) # all card actions must take this signature


def move_player(player, card, current_gameboard):
    new_position = card.destination.start_position
    jail_position = current_gameboard['jail_position']
    if new_position == jail_position:
        player.currently_in_jail = True
        player.current_position = new_position
    else:
        _move_player__check_for_go(player, new_position, current_gameboard)


def set_get_out_of_jail_card_status(player, card, current_gameboard):
    if card == current_gameboard['community_chest_card_objects'][card.name]:
        player.has_get_out_of_jail_community_chest_card = True
    elif card == current_gameboard['chance_card_objects'][card.name]:
        player.has_get_out_of_jail_chance_card = True
    else:
        raise Exception


def bank_cash_transaction(player, card, current_gameboard):
    player.current_cash += card.amount


def player_cash_transaction(player, card, current_gameboard):

    if card.amount_per_player < 0:
        for p in current_gameboard['players']:
            if p == player:
                continue
            if p.status != 'lost':
                p.receive_cash(-1*card.amount_per_player)
                player.current_cash -= card.amount_per_player
    elif card.amount_per_player > 0:
        for p in current_gameboard['players']:
            if p == player:
                continue
            if p.status != 'lost':
                player.receive_cash(card.amount_per_player)
                p.current_cash -= card.amount_per_player


def contingent_bank_cash_transaction(player, card, current_gameboard):
    card.contingency(player, card, current_gameboard) # the contingency function will be one of calculate_street_repair_cost or
    # calculate_general_repair_cost. Except player, their parameters have default values set.


def calculate_street_repair_cost(player, card, current_gameboard): # assesses, not just calculates
    cost_per_house = 40
    cost_per_hotel = 115
    cost = player.num_total_houses*cost_per_house+player.num_total_hotels*cost_per_hotel
    player.current_cash -= cost


def move_player__check_for_go(player, card, current_gameboard):
    new_position = card.destination.start_position
    _move_player__check_for_go(player, new_position, current_gameboard)


def move_to_nearest_utility__pay_or_buy__check_for_go(player, card, current_gameboard):

    utility_positions = current_gameboard['utility_positions']
    min_utility_position = utility_positions[0]
    min_utility_distance = _calculate_board_distance(player.current_position, utility_positions[0])
    for u in utility_positions:
        if _calculate_board_distance(player.current_position, u) < min_utility_distance:
            min_utility_distance = _calculate_board_distance(player.current_position, u)
            min_utility_position = u

    _move_player__check_for_go(player, min_utility_position, current_gameboard)
    current_loc = current_gameboard['location_sequence'][player.current_position]

    if current_loc.loc_class != 'utility':  # simple check
        print 'location is supposed to be a utility...what happened?'
        raise Exception

    if current_loc.owned_by == 'bank':
        player.process_move_consequences(current_gameboard)
        return
    else:
        amount_due = current_gameboard['current_die_total']*10
        player.current_cash -= amount_due
        current_loc.owned_by.receive_cash(amount_due)


def move_to_nearest_railroad__pay_double_or_buy__check_for_go(player, card, current_gameboard):
    railroad_positions = current_gameboard['railroad_positions']
    min_railroad_position = railroad_positions[0]
    min_railroad_distance = _calculate_board_distance(player.current_position, railroad_positions[0])
    for u in railroad_positions:
        if _calculate_board_distance(player.current_position, u) < min_railroad_distance:
            min_railroad_distance = _calculate_board_distance(player.current_position, u)
            min_railroad_position = u

    _move_player__check_for_go(player, min_railroad_position, current_gameboard)
    current_loc = current_gameboard['location_sequence'][player.current_position]


    if current_loc.loc_class != 'railroad': # simple check
        print 'location is supposed to be a railroad...what happened?'
        raise Exception


    if current_loc.owned_by == 'bank':
        player.process_move_consequences(current_gameboard)
        return
    else:
        amount_due = 2 * current_loc.calculate_railroad_dues()
        player.current_cash -=  amount_due
        current_loc.owned_by.receive_cash(amount_due)


def calculate_general_repair_cost(player, card, current_gameboard): # assesses, not just calculates
    cost_per_house = 25
    cost_per_hotel = 100
    cost = player.num_total_houses * cost_per_house + player.num_total_hotels * cost_per_hotel
    player.current_cash -= cost

def move_player_relative(player, card, current_gameboard):
    move_player_after_die_roll(player, card.new_relative_position, current_gameboard, True)

def move_player_after_die_roll(player, rel_move, current_gameboard, check_for_go=True): # this is a utility function used in gameplay, rather than card draw
    # it's important to note that if we are 'visiting' in jail, this function will not set the player.currently_in_jail field to True, since it shouldn't.
    num_locations = len(current_gameboard['location_sequence'])
    go_position = current_gameboard['go_position']
    go_increment = current_gameboard['go_increment']
    # if check for go is True, then assuming that we do pass go or land on go, the increment
    # will be added to the player's current cash
    new_position = player.current_position+rel_move
    new_position = new_position % num_locations

    if check_for_go:
        if _has_player_passed_go(player.current_position, new_position, go_position):
            player.current_cash += go_increment

    player.current_position = new_position # update this only after checking for go


def _has_player_passed_go(current_position, new_position, go_position):
    if new_position == go_position:
        return True

    elif new_position == current_position:  # we've gone all round the board
        return True

    elif current_position < new_position:
        if new_position <= go_position > current_position:
            return True

    elif current_position > new_position:
        if go_position > current_position or go_position <= new_position:
            return True

    return False


def _calculate_board_distance(position_1, position_2): # this is calculated bidirectionally,
    # not by number of effective dice moves.
    dist = 0
    if position_1 - position_2 < 0 :
        dist = position_2 - position_1
    else:
        dist = position_1 - position_2
    return dist

def _move_player__check_for_go(player, new_position, current_gameboard): # the private version
    go_position = current_gameboard['go_position']
    go_increment = current_gameboard['go_increment']
    if _has_player_passed_go(player.current_position, new_position, go_position):
        player.current_cash += go_increment

    player.current_position = new_position # update this only after checking for go