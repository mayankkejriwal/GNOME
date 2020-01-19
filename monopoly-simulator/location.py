
class Location(object):

    def __init__(self, loc_class, name, start_position, end_position, color):
        self.loc_class = loc_class
        self.name = name
        self.start_position = start_position
        self.end_position = end_position
        self.color = color

class DoNothingLocation(Location):
    def __init__(self, loc_class, name, start_position, end_position, color):
        super(DoNothingLocation, self).__init__(loc_class, name, start_position, end_position, color)


class ActionLocation(Location):
    def __init__(self, loc_class, name, start_position, end_position, color, perform_action):
        super(ActionLocation, self).__init__(loc_class, name, start_position, end_position, color)
        self.perform_action = perform_action


class RealEstateLocation(Location):
    def __init__(self, loc_class, name, start_position, end_position, color, rent_1_house, rent_hotel,
                 price, rent_3_houses, rent, mortgage, price_per_house, rent_4_houses, rent_2_houses, owned_by,
                 num_houses, num_hotels):
        super(RealEstateLocation, self).__init__(loc_class, name, start_position, end_position, color)
        self.rent_1_house = rent_1_house
        self.rent_2_houses = rent_2_houses
        self.rent_3_houses = rent_3_houses
        self.rent_4_houses = rent_4_houses
        self.rent_hotel = rent_hotel
        self.rent = rent
        self.price = price
        self.price_per_house = price_per_house
        self.mortgage = mortgage
        self.owned_by = owned_by
        self.num_houses = num_houses
        self.num_hotels = num_hotels
        self.is_mortgaged = False

        obj = dict()
        obj[1] = self.rent_1_house
        obj[2] = self.rent_2_houses
        obj[3] = self.rent_3_houses
        obj[4] = self.rent_4_houses
        self._house_rent_dict = obj

    def update_asset_owner(self, player, current_gameboard):
        self.owned_by = player
        player.assets.add(self)
        flag = True
        for o in current_gameboard['color_assets'][self.color]:
            if o not in player.assets:
                flag = False
                break
        if flag:
            player.full_color_sets_possessed.add(self.color)

        if self.is_mortgaged:
            player.mortgaged_assets.add(self)


    def calculate_rent(self):
        # a property can either have a hotel OR houses OR be unimproved-monopolized OR be unimproved-non-monopolized
        if self.num_hotels == 1:
            return self.rent_hotel
        elif self.num_houses > 0: # later we can replace these with reflections
            return self._house_rent_dict[self.num_houses] # if for some reason
        elif self.color in self.owned_by.full_color_sets_possessed:
            return self.rent*2
        else:
            return self.rent


class TaxLocation(Location):
    def __init__(self, loc_class, name, start_position, end_position, color, amount_due):
        super(TaxLocation, self).__init__(loc_class, name, start_position, end_position, color)
        self.amount_due = amount_due


class RailroadLocation(Location):
    def __init__(self, loc_class, name, start_position, end_position, color, price, mortgage, owned_by):
        super(RailroadLocation, self).__init__(loc_class, name, start_position, end_position, color)
        self.price = price
        self.mortgage = mortgage
        self.owned_by = owned_by
        self.is_mortgaged = False

        obj = dict()
        obj[1] = 25
        obj[2] = 50
        obj[3] = 100
        obj[4] = 200
        self._railroad_dues = obj

    def calculate_railroad_dues(self):
        if self.owned_by.num_railroads_possessed > 4 or self.owned_by.num_railroads_possessed < 0:
            print 'num railroads: ',self.owned_by.num_railroads_possessed
            print self.owned_by
        # print self.owned_by.num_railroads_possessed
        return self._railroad_dues[self.owned_by.num_railroads_possessed]

    def update_asset_owner(self, player,current_gameboard): # current gameboard is unused right now, but may be used to enforce consistency checks later
        self.owned_by = player
        player.assets.add(self)
        player.num_railroads_possessed += 1
        if self.is_mortgaged:
            player.mortgaged_assets.add(self)



class UtilityLocation(Location):
    def __init__(self, loc_class, name, start_position, end_position, color, price, mortgage, owned_by):
        super(UtilityLocation, self).__init__(loc_class, name, start_position, end_position, color)
        self.price = price
        self.mortgage = mortgage
        self.owned_by = owned_by
        self.is_mortgaged = False

        obj = dict()
        obj[1] = 4
        obj[2] = 10
        self._die_multiples = obj

    def calculate_utility_dues(self, die_total):
        if self.owned_by.num_utilities_possessed > 2 or self.owned_by.num_utilities_possessed < 0:
            print 'num utilities: ',self.owned_by.num_utilities_possessed
            print self.owned_by
        return die_total*self._die_multiples[self.owned_by.num_utilities_possessed]

    def update_asset_owner(self, player, current_gameboard): # current gameboard is unused right now, but may be used to enforce consistency checks later
        self.owned_by = player
        player.assets.add(self)
        player.num_utilities_possessed += 1
        if self.is_mortgaged:
            player.mortgaged_assets.add(self)



