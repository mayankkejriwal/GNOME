

# every function in here that can be called from outside must return a success or failure (I need to modify the returns)

# def bid_on_property(player, current_gameboard, asset, current_bid, bidding_strategy_function):
#     # bidding strategy function is what you use to decide what/how to bid. See decision_agent_1 for examples.
#     # make it return 0 (or any number less than current_bid) at any time to drop out.
#     if asset.owned_by != 'bank':
#         print 'bidding can only happen on bank-owned properties!'
#         raise Exception
#     elif player.current_cash <= current_bid:
#         return 0 # player is dropping out of auction
#     else:
#         proposed_bid = bidding_strategy_function(player, current_gameboard, asset, current_bid)
#         if proposed_bid <= current_bid:
#             return 0
#         else:
#             return proposed_bid


def free_mortgage(player, asset): # if the asset is not mortgage-able (which means it's not own-able, an exception is automatically raised)
    if asset.owned_by != player:
        print 'player is trying to free up mortgage on property that is not theirs'
        return -1
    elif asset.is_mortgaged is False or asset not in player.mortgaged_assets: # the or is unnecessary but serves as a check
        print 'property is not mortgaged to begin with'
        return -1
    elif player.current_cash <= 1.1 * asset.mortgage:
        print 'player does not have cash to free this mortgage'
        return -1
    else:
        asset.is_mortgaged = False
        player.current_cash -= (1.1 * asset.mortgage)
        player.mortgaged_assets.remove(asset)
        return 1 # mortgage has successfully been freed


def make_sell_property_offer(from_player, asset, to_player, price): #the property is only sold
    # if the buyer invokes accept_sell_property_offer when it is their turn next.
    if to_player.is_property_offer_outstanding:
        print 'player already has a property offer. You must wait'
        return -1
    elif asset.owned_by != from_player:
        print 'player does not own this property and cannot make an offer'
        return -1
    elif asset.loc_class == 'real_estate' and (asset.num_houses > 0 or asset.num_hotels > 0):
        print 'Property has improvements. Clear them before making an offer!' # note that this entails a risk since you
        # could clear the improvements, and still not get an offer accepted. Decide at your own peril!
        return -1
    else:
        to_player.outstanding_property_offer['asset'] = asset
        to_player.outstanding_property_offer['from_player'] = from_player
        to_player.outstanding_property_offer['price'] = price
        to_player.is_property_offer_outstanding = True
        return 1 # offer has been made


def sell_property(player, asset): # buyer is always the bank. if buyer is not bank, then use make_sell_property_offer
    # we allow you to sell mortgaged properties. The bank will deduct what it is due before paying you if the property is mortgaged.
    if asset.owned_by != player:
        print 'Player does not own this property and cannot sell it'
        return -1

    elif asset.num_houses > 0 or asset.num_hotels > 0 :
        print 'Property has improvements. Clear them before trying to sell!'
        return -1

    else:
        cash_due = _transfer_property_to_bank(player, asset)
        player.receive_cash(cash_due)
        return 1 # property has been successfully sold


def sell_house_hotel(player, asset, sell_house=True, sell_hotel=False): # we can only sell houses or hotels to the bank
    # some checks to ensure the player is allowed to sell houses and hotels.
    if asset.owned_by != player:
        print 'player does not own this property and cannot make an offer'
        return -1


def accept_sell_property_offer(player, current_gameboard):
    if not player.is_property_offer_outstanding:
        print 'no outstanding property offers to accept'
        return -1
    elif player.current_cash <= player.outstanding_property_offer['price']:
        print 'player does not have the cash necessary to accept'
        player.is_property_offer_outstanding = False
        player.outstanding_property_offer['from_player'] = None
        player.outstanding_property_offer['asset'] = None
        player.outstanding_property_offer['price'] = -1
        return -1
    else:
        player.is_property_offer_outstanding = False
        player.current_cash -= player.outstanding_property_offer['price']
        player.outstanding_property_offer['from_player'].receive_cash(player.outstanding_property_offer['price'])
        _transfer_property(player.outstanding_property_offer['asset'], player.outstanding_property_offer['from_player'], player, current_gameboard)
        return 1

def skip_turn():
    return 2 # uses special code, since we need it in gameplay


def concluded_actions():
    return 1 # does nothing; code is always a success


def mortgage_property(player, asset):
    if asset.owned_by != player:
        print 'player is trying to mortgage property that is not theirs'
        return -1
    elif asset.is_mortgaged is True or asset in player.mortgaged_assets: # the or is unnecessary but serves as a check
        print 'property is already mortgaged to begin with'
        return -1
    elif asset.loc_class == 'real_estate' and (asset.num_houses > 0 or asset.num_hotels > 0):
        print 'property has improvements. remove improvements before attempting mortgage'
        return -1
    else:
        asset.is_mortgaged = True
        player.receive_cash(1.1 * asset.mortgage)
        player.mortgaged_assets.add(asset)
        return 1 # property has been successfully mortgaged


def improve_property(player, asset, current_gameboard, add_house=True, add_hotel=False):
    if asset.owned_by != player or asset.is_mortgaged or asset.color not in player.full_color_sets_possessed or \
        player.current_cash < asset.price_per_house:
        # these are the usual conditions that we verify before allowing any improvement to proceed
        print 'player is not permitted to/cannot afford to improve this property'
        return -1

    if add_hotel: # this is the simpler case
        if asset.num_hotels == 1:
            print 'there is already a hotel here. You are only permitted one...'
            return -1
        elif asset.num_houses != 4:
            print 'you need to have four houses before you can build a hotel...'
            return -1
        flag = True
        for same_colored_asset in current_gameboard['color_assets'][asset.color]:
            if same_colored_asset == asset:
                continue
            if not (same_colored_asset.num_houses == 4 or same_colored_asset.num_hotels == 1):
                flag = False
                break
        if flag:
            player.num_total_hotels = 1
            player.num_total_houses -= asset.num_houses
            player.current_cash -= asset.price_per_house
            asset.num_houses = 0
            asset.num_hotels = 1
            return 1 # player has successfully improved property

        else:
            print 'all same-colored properties must be informly improved first before you can build a hotel on this property'
            return -1

    elif add_house:
        if asset.num_hotels == 1 or asset.num_houses == 4:
            print 'there is already a hotel or 4 houses here. You are not permitted another house.'
            return -1
        flag = True
        current_asset_num_houses = asset.num_houses
        for same_colored_asset in current_gameboard['color_assets'][asset.color]:
            if same_colored_asset == asset:
                continue
            if same_colored_asset.num_houses < current_asset_num_houses or same_colored_asset.num_hotels == 1:
                flag = False
                break
        if flag:
            player.num_total_houses += 1
            player.current_cash -= asset.price_per_house
            asset.num_houses += 1
            return 1 # player has successfully improved property

        else:
            print 'all same-colored properties must be informly improved first before you can build a hotel on this property'
            return -1


def use_get_out_of_jail_card(player, current_gameboard):
    if not player.currently_in_jail:
        return -1 # simple check. note that player will still have the card(s)

    if player.has_get_out_of_jail_chance_card: # we give first preference to chance, then community chest
        player.has_get_out_of_jail_chance_card = False
        player.currently_in_jail = False
        current_gameboard['chance_cards'].add(current_gameboard['chance_card_objects']['get_out_of_jail_free'])
        return 1
    elif player.has_get_out_of_jail_community_chest_card:
        player.has_get_out_of_jail_community_chest_card = False
        player.currently_in_jail = False
        current_gameboard['community_chest_cards'].add(current_gameboard['community_chest_card_objects']['get_out_of_jail_free'])
        return 1


def pay_jail_fine(player): # if you don't have enough cash, you'll stay in jail.
    if player.current_cash >= 50 and player.currently_in_jail:
        player.current_cash -= 50
        player.currently_in_jail = False
        return 1
    else:
        return -1 # failure to pay fine


def roll_die(die_objects, choice):
    return [choice(a=d.die_state) for d in die_objects]


def buy_property(player, asset, current_gameboard): # you must have enough cash for this asset + it must belong to the bank

    # Note: the only way to buy a property from another player is if they offer to sell it to you and you accept the offer.
    if asset.owned_by != 'bank':
        return -1

    if player.current_cash < asset.price:
        # property has to go up for auction
        index_current_player = current_gameboard['players'].index(player)  # in players, find the index of the current player
        starting_player_index = (index_current_player + 1) % len(current_gameboard['players'])  # the next player's index. this player will start the auction
        current_gameboard['bank'].auction(starting_player_index, current_gameboard, asset)
        return -1 # this is a -1 even though you may still succeed in buying the property at auction
    else:
        player.current_cash -= asset.price
        asset.update_asset_owner(player, current_gameboard)
        player.reset_option_to_buy()
        return 1


def _transfer_property(asset, from_player, to_player, current_gameboard):
    _remove_asset_from_player(from_player, asset) # it's important to note that between this statement and the next, the asset/players will be in a state of flux
    asset.update_asset_owner(to_player, current_gameboard)


def _transfer_property_to_bank(player, asset):
    asset.owned_by = 'bank'
    cash_due = asset.price/2
    cash_owed = 0
    if asset.loc_class == 'real_estate' and (asset.num_houses > 0 or asset.num_hotels > 0):
        print 'Bank error! property being sold has improvements on it'
        return
    if asset.is_mortgaged:
        asset.is_mortgaged = False
        player.mortgaged_assets.remove(asset)
        cash_owed = 1.1*asset.mortgage

    _remove_asset_from_player(player, asset)

    return cash_due-cash_owed


def _remove_asset_from_player(player, asset):
    player.assets.remove(asset)
    if asset.loc_class == 'railroad':
        player.num_railroads_possessed -= 1
    elif asset.loc_class == 'utility':
        player.num_utilities_possessed -= 1
    elif asset.color in player.full_color_sets_possessed:  # the asset must have a color (i.e. be real estate if it is not railroad or utility)
        player.full_color_sets_possessed.remove(asset.color)

    if asset.is_mortgaged:
        player.mortgaged_assets.remove(asset)




