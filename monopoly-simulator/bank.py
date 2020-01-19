class Bank(object):
    def __init__(self):
        pass

    def auction(self, starting_player_index, current_gameboard, asset):
        """
        This function will be called when a player lands on a purchaseable property (real estate, railroad or utility)
        but decides not to make the purchase. 
        :param starting_player_index:  An integer. The index of the player in current_gameboard['players'] who will be starting the auction
        :param current_gameboard: A dict. Specifies the global game board data structure
        :param asset: A purchaseable instance of Location (i.e. RealEstateLocation, UtilityLocation or RailroadLocation)
        :return: None
        """

        print 'Entering auctioning for asset ',asset.name

        current_bid = 0
        players_out_of_auction = set()
        winning_player = None
        bidding_player_index = None

        # Since the starting player may be out of the game, we first check if we should update the starting player
        for p in current_gameboard['players']:
            if p.status == 'lost':
                players_out_of_auction.add(p)
            else:
                print p.player_name,' is an auction participant.'

        count = 0
        while count < len(current_gameboard['players']):
            if current_gameboard['players'][starting_player_index] in players_out_of_auction:
                count += 1
                starting_player_index = (starting_player_index+1)%len(current_gameboard['players'])
            else:
                bidding_player_index = starting_player_index
                break

        if bidding_player_index is None: # no one left to auction. This is a failsafe, the code should never get here.
            print 'No one is left in the game that can participate in the auction! Why are we here?'
            return
        else:
            print current_gameboard['players'][bidding_player_index].player_name,' will place the first bid'

        while len(players_out_of_auction) < len(current_gameboard['players'])-1: # we iterate and bid while at least 2 players remain
            bidding_player = current_gameboard['players'][bidding_player_index]
            if bidding_player in players_out_of_auction:
                bidding_player_index = (bidding_player_index+1)%len(current_gameboard['players']) # next player
                continue
            proposed_bid = bidding_player.make_bid(bidding_player, current_gameboard,
                                asset, current_bid) # make_bid automatically passes in the player as the first argument
                                                    # since it is a non-static function assignment
            print bidding_player.player_name,' proposed bid ',str(proposed_bid)

            if proposed_bid == 0:
                pass
            elif proposed_bid < current_bid: # the <= serves as a forcing function to ensure the proposed bid must be non-zero
                players_out_of_auction.add(bidding_player)
                print bidding_player.player_name, ' is out of the auction.'
                bidding_player_index = (bidding_player_index + 1) % len(current_gameboard['players'])
                continue

            current_bid = proposed_bid
            print 'The current highest bid is ',str(current_bid), ' and is held with ',bidding_player.player_name
            winning_player = bidding_player
            bidding_player_index = (bidding_player_index + 1) % len(current_gameboard['players'])

        if winning_player:
            winning_player.current_cash -= current_bid # if it got here then current_bid is non-zero.
            asset.update_asset_owner(winning_player, current_gameboard)
        else:
            print 'Auction did not succeed in a sale.'
        return
