from location import *
import json
import sys
from action_choices import skip_turn

# print 10%10
# game_schema_path = '/Users/mayankkejriwal/git-projects/GNOME/'
# game_schema = json.load(open(game_schema_path+'monopoly_game_schema_v1-2.json', 'r'))
#
# location_objects = list()
# for l in game_schema['locations']['location_states']:
#     if l['loc_class'] == 'action':
#         location_objects.append(ActionLocation(**l))
#     elif l['loc_class'] == 'do_nothing':
#         location_objects.append(DoNothingLocation(**l))


# k = skip_turn
# if k == skip_turn:
#     print 'yes'
# k()
# print location_objects[2].name


class Test(object):
    def __init__(self):
        pass

    def test_method(self, a, b):
        return a+b

    def test_method2(self):
        print self.test_method(1,2)


g = Test()
print g.test_method(1,2)