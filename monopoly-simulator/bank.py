class Bank(object):
    def __init__(self):
        pass

    def auction(self, starting_player_index, current_gameboard, asset):
        # starting player may be out of the game. the code makes this check and updates starting player if necessary.
        current_bid = 0
        players_out_of_auction = set()

        for p in current_gameboard['players']:
            if p.status == 'lost':
                players_out_of_auction.add(p)

        bidding_player_index = None
        players_considered = set()
        while len(players_considered) < len(current_gameboard['players']):
            if current_gameboard['players'][starting_player_index] in players_out_of_auction:
                players_considered.add(starting_player_index)
                starting_player_index = (starting_player_index+1)%len(current_gameboard['players'])
            else:
                bidding_player_index = starting_player_index
                break

        # winning_player = current_gameboard['players'][bidding_player_index]
        winning_player = None

        if bidding_player_index is None:
            print 'no one left to auction! Why are we here?'
            return # no one left to auction. This is a failsafe, the code should never get here.

        while len(players_out_of_auction) < len(current_gameboard['players'])-1: # till at least 2 players remain
            bidding_player = current_gameboard['players'][bidding_player_index]
            if bidding_player in players_out_of_auction:
                bidding_player_index = (bidding_player_index+1)%len(current_gameboard['players']) # next player
                continue
            proposed_bid = bidding_player.make_bid(bidding_player, current_gameboard, asset, current_bid)
            # make_bid automatically passes in the player as the first argument since it is a non-static function assignment

            if proposed_bid <= current_bid: # the <= serves as a forcing function to ensure the proposed bid must be non-zero
                players_out_of_auction.add(bidding_player)
                bidding_player_index = (bidding_player_index + 1) % len(current_gameboard['players'])
                continue

            current_bid = proposed_bid
            winning_player = bidding_player
            bidding_player_index = (bidding_player_index + 1) % len(current_gameboard['players'])

        if winning_player:
            winning_player.current_cash -= current_bid # if it got here then current_bid is non-zero.
            asset.update_asset_owner(winning_player, current_gameboard)
        return
