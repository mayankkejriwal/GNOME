

MONOPOLY SIMULATOR:

Full code for the simulator is in monopoly-simulator/ and is written using OOP methodology.

The entry point for the simulator is gameplay.py and can be run on the command line:

$ python gameplay.py > game-log.txt

The simulator currently relies on Python 2.7.x. Because inheritance has a different syntax between 2.7 and 3, we will
need to release a different version if you really like 3. This can be accomplished relatively easily, but for now, we recommend
setting up a 2.7 interpreter and running the code therein.

You could also choose to print the log on the command line. We've found the log to be very useful in providing a human
readable version of game events. When debugging a decision agent, these logs are your friend. If you succeed in running
the game off the shelf, you should get a log that looks somewhat (though probably not exactly) like game-1-log.txt

To run the simulator, you need a decision agent and the game schema. We have provided the schema already in the outer folder,
although you will have to specify the path to the schema once you clone this repo on your own system. In gameplay, we
also have to specify the numpy seed (currently a default is set) and if we want, we can modify elements of the game schema
for testing purposes. For simple agents that do not try to monopolize, we recommend modifying go_increment to avoid
runaway cash increases from the bank to the players.

We have provided an example 'dummy' decision agent to guide you on how to build out your own decision agent. We plan
to release at least one sophisticated decision agent sometime in January, and the baseline agent used in evaluations
will also be a rule-based, sophisticated decision maker who weighs the state of the board carefully before deciding
what to do.

The code has been fairly well documented, and we've done a lot of testing on it. That does not mean it's completely clear
or that mistakes might not appear. On our part, we are continuously running tests but if you see something that's unclear
or that seems like an error we'd appreciate feedback!

GAME SCHEMA:

The current version of the schema, generated using monopoly-game-schema.py is monopoly_game_schema_v1-2.json. We provide
_v1-1.json for comparison only. It should not be used in the game. Here's a succinct version of some of the more
important changes in going from v1-1 to v1-2:


Updates from v1-1 to v1-2:

--In location_states, we have changed 'class' to 'loc_class'. The reason is (and we should have realized it earlier)
that class is a reserved word in Python.

--we have added a new field called go_increment. This is the amount you get when you pass go each time.

--has_get_out_of_jail card has been replaced with its community chest and chance equivalents.
The reason is that a player can have two of these at the same time (one from each of the card categories), and we need
to be able to track this (e.g., if the player uses the chance card, it should go back to the chance pile.
Unlike the other cards, which get used and replaced immediately in the pile, this one is something the player can hold
on to for a while, which complicates matters)

--another change in location is that we now keep track of who owns the location WITHIN the location itself, and also
how many houses/hotels are on that location. We decided to make this change to avoid too many function
calls/indirections when calculating rent. This means that under 'assets' in player_states, we have removed hotels and
houses; now, we only track which properties the player owns, along with an derivatory data structure that tracks
whether the players possesses full color sets. In turn, this means the 'assets' has been considerably simplified,
since we only need to keep track of the names of the properties the player owns. More details are provided in the
player.py file.

--chance cards were previously missing from the schema due to a glitch in the JSON generation (these have now been added)

--in chance/community chest, we have added a new card class called 'contingent_cash_from_bank' that was previously in
the class positive/negative_cash_from_bank. The reason is that the positive/negative class always involves a
fixed amount, while contingent cash requires a function calculation (e.g., calculating street repair cost),
which makes the structure of the class different.

--name of 'go_to_nearest_railroad_pay_double_1' card is now just 'go_to_nearest_railroad_pay_double'. Note that the
'name' of a card does not have to be unique since there could be multiple identical cards (such as in this case)

--we've added skip_turn and concluded_actions to out_of_turn action choices. skip_turn in this context just means that we
won't take action on out_of_turn (at least right now). concluded_actions means that we're done with whatever actions we
wanted to take. concluded_actions must follow at least one action, otherwise skip_turn should be invoked. Only when
all out_of_turn players have skipped the turn and the current player rolls the die will the die be rolled, and the
post die roll phase begin. The exception is the post-die roll phase where concluded_actions can be called as the very
first action.

--we have simplified player_states since it contained redundant information. Now it refers to a single dictionary.

--there is a small chance my current cash might become negative even if it's not my turn (if another player collects
from me due to a card draw, and I have low cash). Because the chances are so small of this happening, we do not force
that player to take action just yet but once it's his turn, he'll have to deal with the negative cash before he can
conclude his turn (or declare bankruptcy)

--the 'player' objects now have some additional fields that will be useful for keeping track of the game state.

--I've added 'mortgage_property', 'improve_property' to the list of functions that are allowed in out_of_turn moves.
'bid_on_property' has been removed. The reason is that currently, the only way you can bid on a property is at auction,
which is conducted by the bank as a special process when a player refuses to buy a property on which he/she has
landed. So you can't really 'choose' to bid in an out_of_turn move; instead, you can bid only in a player's
post-roll phase.


REMINDERS:

--it IS possible to sell a mortgaged property

UPDATES:

February 5, 2020:

--A background agent that is significantly more advanced than the previous simple decision agent has been added, along with
some agent helper functions in a separate file. When building your own agent, you should make use of the helper file as
a guide only, since some elements are strategic rather than logical (e.g., how to decide which property we should sell
to another player) and can be done in other (probably more optimal) ways. 

--To ensure the game continues without a single player having the ability to 'hang' things up, we have instituted limits
on (i) how many actions you are allowed to take in pre/post/out-of-turn moves before you are forced to conclude actions
(currently 50), and (ii) how many out-of-turn 'rounds' we allow before we force the current player to roll the dice
and enter post-roll. Currently it is set at 200. We believe these limits are more than adequate to ensure that players
have the opportunity to take all moves they may want to take before passing the baton. Currently, the game ends within
150-500 die rolls, and does not enter into a runaway state. This is due to aggressive trading on the part of the
background agents. 

January 27, 2020:

--We've added a 'history' facility (a dict) to the game_elements data structure (also called current_gameboard in much of the
game). There are three lists inside 'history', all of equal length, keyed respectively by 'function', 'param' and 'return'.
Each time a function is called (starting from within gameplay/simulate_game_instance), we append the function to 'function',
the parameters passed inside the function to 'param' and the return value to 'return'. We always make this update after
the function returns (if the function does not return anything, then we simply append None). 'function' is a list of
function pointers, and 'return' can be heterogeneous, depending on what a function is returning. 'param' is a list of
dicts, with the keys in the dicts corresponding to exactly the expected arguments in the function (including 'self') and
the values shallow copies of the corresponding arguments passed to the function. Note that if a function takes on no values,
we still append an empty dictionary to param to maintain equal length of all three lists. Furthermore, functions that
are internal (starting with _ or __) are not recorded. Anything called before simulate_game_instance (particularly, the
initialization of the game board itself) is not recorded either. Finally, diagnostics functions are not recorded since
they are 'extra-game' conceptually; they should only be used by a developer for stress-testing agents/games and not
by agents themselves.

--Note that since the parameters can be objects, and we do not do a deep copy of objects when we insert them into
a param dict, the state of objects can (and in many cases, will) change between the time an object is inserted as
a parameter or return value into a list, and the time when it is queried by an external agent. With this caveat in mind,
 there are many core values in each object that stay constant over the tenure of the game e.g., a player's name,
 an asset's name, card details etc. Dereference with caution.

 --Because of the history facility, we had to modify the signatures of action_choices/mortgage_property & pay_jail_fine slightly
 (we added current_gameboard to the argument list of both functions). This was necessary since each of these functions
 itself calls a function, and in order to accurately update history, needs access to the gameboard. If you have already
 implemented a decision agent that expects the old signature (without current_gameboard) you may want to update; it should
 be a very small change.