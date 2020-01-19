

def print_asset_owners(game_elements):
    for k,v in game_elements['location_objects'].items():
        if v.loc_class == 'railroad' or v.loc_class == 'utility' or v.loc_class == 'real_estate':
            if v.owned_by == 'bank':
                print 'Owner of ', k, ' is bank'
            else:
                print 'Owner of ', k, ' is ',v.owned_by.player_name

def print_player_cash_balances(game_elements):
    cash_balance = list()
    for p in game_elements['players']:
        cash_balance.append(str(p.current_cash))
    print ' '.join(cash_balance)

    if int(cash_balance[0]) > 20000:
        print cash_balance[0]

def max_cash_balance(game_elements):
    max = -1
    for p in game_elements['players']:
        if max < p.current_cash:
            max = p.current_cash
    return max



