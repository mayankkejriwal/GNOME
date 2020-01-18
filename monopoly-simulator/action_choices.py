import numpy as np


def bid_on_property(player, current_gameboard, asset, current_bid, bidding_strategy_function):
    # bidding strategy function is what you use to decide what/how to bid. See decision_agent_1 for examples.
    # make it return 0 (or any number less than current_bid) at any time to drop out.
    if asset.owned_by != 'bank':
        print 'bidding can only happen on bank-owned properties!'
        raise Exception
    elif player.current_cash <= current_bid:
        return 0 # player is dropping out of auction
    else:
        proposed_bid = bidding_strategy_function(player, current_gameboard, asset, current_bid)
        if proposed_bid <= current_bid:
            return 0
        else:
            return proposed_bid


def free_mortgage(player, asset): # if the asset is not mortgage-able (which means it's not own-able, an exception is automatically raised)
    if asset.owned_by != player:
        print 'player is trying to free up mortgage on property that is not theirs'
        return
    elif asset.is_mortgaged is False or asset not in player.mortgaged_assets: # the or is unnecessary but serves as a check
        print 'property is not mortgaged to begin with'
        return
    elif player.current_cash <= 1.1 * asset.mortgage:
        print 'player does not have cash to free this mortgage'
        return
    else:
        asset.is_mortgaged = False
        player.current_cash -= (1.1 * asset.mortgage)
        player.mortgaged_assets.remove(asset)


def make_sell_property_offer(from_player, asset, to_player, price): #the property is only sold
    # if the buyer invokes accept_sell_property_offer when it is their turn next.
    if to_player.is_property_offer_outstanding:
        print 'player already has a property offer. You must wait'
        return
    elif asset.owned_by != from_player:
        print 'player does not own this property and cannot make an offer'
        return
    elif asset.loc_class == 'real_estate' and (asset.num_houses > 0 or asset.num_hotels > 0):
        print 'Property has improvements. Clear them before making an offer!' # note that this entails a risk since you
        # could clear the improvements, and still not get an offer accepted. Decide at your own peril!
        return
    else:
        to_player.outstanding_property_offer['asset'] = asset
        to_player.outstanding_property_offer['from_player'] = from_player
        to_player.outstanding_property_offer['price'] = price
        to_player.is_property_offer_outstanding = True


def sell_property(player, asset): # buyer is always the bank. if buyer is not bank, then use make_sell_property_offer
    # we allow you to sell mortgaged properties. The bank will deduct what it is due before paying you if the property is mortgaged.
    if asset.owned_by != player:
        print 'Player does not own this property and cannot sell it'
        return

    elif asset.num_houses > 0 or asset.num_hotels > 0 :
        print 'Property has improvements. Clear them before trying to sell!'
        return

    else:
        cash_due = _transfer_property_to_bank(player, asset)
        player.receive_cash(cash_due)


def sell_house_hotel(player, asset, sell_house=True, sell_hotel=False): # we can only sell houses or hotels to the bank
    # some checks to ensure the player is allowed to sell houses and hotels.
    if asset.owned_by != player:
        print 'player does not own this property and cannot make an offer'
        return


def accept_sell_property_offer(player, current_gameboard):
    if not player.is_property_offer_outstanding:
        print 'no outstanding property offers to accept'
        return
    elif player.current_cash <= player.outstanding_property_offer['price']:
        print 'player does not have the cash necessary to accept'
        player.is_property_offer_outstanding = False
        player.outstanding_property_offer['from_player'] = None
        player.outstanding_property_offer['asset'] = None
        player.outstanding_property_offer['price'] = -1
        return
    else:
        player.is_property_offer_outstanding = False
        player.current_cash -= player.outstanding_property_offer['price']
        player.outstanding_property_offer['from_player'].receive_cash(player.outstanding_property_offer['price'])
        _transfer_property(player.outstanding_property_offer['asset'], player.outstanding_property_offer['from_player'], player, current_gameboard)


def skip_turn():
    return # does nothing


def concluded_actions():
    return # does nothing


def mortgage_property(player, asset):
    if asset.owned_by != player:
        print 'player is trying to mortgage property that is not theirs'
        return
    elif asset.is_mortgaged is True or asset in player.mortgaged_assets: # the or is unnecessary but serves as a check
        print 'property is already mortgaged to begin with'
        return
    elif asset.loc_class == 'real_estate' and (asset.num_houses > 0 or asset.num_hotels > 0):
        print 'property has improvements. remove improvements before attempting mortgage'
        return
    else:
        asset.is_mortgaged = True
        player.receive_cash(1.1 * asset.mortgage)
        player.mortgaged_assets.add(asset)


def improve_property(player, asset, current_gameboard, add_house=True, add_hotel=False):
    if asset.owned_by != player or asset.is_mortgaged or asset.color not in player.full_color_sets_possessed or \
        player.current_cash < asset.price_per_house:
        # these are the usual conditions that we verify before allowing any improvement to proceed
        print 'player is not permitted to/cannot afford to improve this property'
        return

    if add_hotel: # this is the simpler case
        if asset.num_hotels == 1:
            print 'there is already a hotel here. You are only permitted one...'
            return
        elif asset.num_houses != 4:
            print 'you need to have four houses before you can build a hotel...'
            return
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

        else:
            print 'all same-colored properties must be informly improved first before you can build a hotel on this property'

    elif add_house:
        if asset.num_hotels == 1 or asset.num_houses == 4:
            print 'there is already a hotel or 4 houses here. You are not permitted another house.'
            return
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

        else:
            print 'all same-colored properties must be informly improved first before you can build a hotel on this property'


def use_get_out_of_jail_card(player, current_gameboard):
    if not player.currently_in_jail:
        return # simple check. note that player will still have the card(s)

    if player.has_get_out_of_jail_chance_card: # we give first preference to chance, then community chest
        player.has_get_out_of_jail_chance_card = False
        player.currently_in_jail = False
        current_gameboard['chance_cards'].add(current_gameboard['chance_card_objects']['get_out_of_jail_free'])
        return
    elif player.has_get_out_of_jail_community_chest_card:
        player.has_get_out_of_jail_community_chest_card = False
        player.currently_in_jail = False
        current_gameboard['community_chest_cards'].add(current_gameboard['community_chest_card_objects']['get_out_of_jail_free'])
        return


def pay_jail_fine(player): # if you don't have enough cash, you'll stay in jail.
    if player.current_cash >= 50 and player.currently_in_jail:
        player.current_cash -= 50
        player.currently_in_jail = False
        return
    else:
        return


def roll_die(die_objects):
    return [np.random.choice(a=d.die_state) for d in die_objects]


def buy_property(player, asset, current_gameboard): # you must have enough cash for this asset + it must belong to the bank
    # the only way to buy a property from another player is if they offer to sell it to you and you accept the offer.
    if player.current_cash < asset.price or asset.owned_by != 'bank':
        return
    else:
        player.current_cash -= asset.price
        asset.update_asset_owner(player, current_gameboard)
        return


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




