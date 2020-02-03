def will_property_complete_set(player, asset, current_gameboard):
    """

    :param player: Player instance
    :param asset: Location instance
    :return: Boolean. True if the asset will complete a color set for the player, False otherwise. For railroads
    (or utilities), returns true only if player owns all other railroads (or utilities)
    """
    if asset.color is None:
        if asset.loc_class == 'railroad':
            if player.num_railroads_possessed == 3:
                return True
        elif asset.loc_class == 'utility':
            if player.num_utilities_possessed == 1:
                return True
        else:
            print 'This asset does not have a color and is neither utility nor railroad'
            raise Exception
    else:
        c = asset.color
        c_assets = current_gameboard['color_assets'][c]
        for c_asset in c_assets:
            if c_asset == asset:
                continue
            else:
                if c_asset not in player.assets:
                    return False
        return True # if we got here, then every asset of the color of 'asset' is possessed by player.

def identify_potential_mortgage(player, amount_to_raise, lone_constraint=False):
    """

    :param player: Player instance. The potential mortgage has to be an unmortgaged property that this player owns.
    :param amount_to_raise: Integer. The amount of money looking to be raised from this mortgage.
    :param lone_constraint: Boolean. If true, we will limit our search to properties that meet the 'lone' constraint i.e.
    the property (if a railroad or utility) must be the only railroad or utility possessed by the player, or if colored,
    the property must be the only asset in its color class to be possessed by the player.
    :return: None, if a mortgage cannot be identified, otherwise a Location instance (representing the potential mortgage)
    """
    return None

def identify_potential_sale(player, amount_to_raise, lone_constraint=False):
    """
    All potential sales considered here will be to the bank.
    :param player: Player instance. The potential sale has to be an unmortgaged property that this player owns.
    :param amount_to_raise: Integer. The amount of money looking to be raised from this sale.
    :param lone_constraint: Boolean. If true, we will limit our search to properties that meet the 'lone' constraint i.e.
    the property (if a railroad or utility) must be the only railroad or utility possessed by the player, or if colored,
    the property must be the only asset in its color class to be possessed by the player.
    :return: None, if a sale cannot be identified, otherwise a Location instance (representing the potential sale)
    """
    return None




