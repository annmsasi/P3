#!/usr/bin/env python
#

"""
// There is already a basic strategy in place here. You can use it as a
// starting point, or you can throw it out entirely and replace it with your
// own.
"""
import logging, traceback, sys, os, inspect
logging.basicConfig(filename=__file__[:-3] +'.log', filemode='w', level=logging.DEBUG)
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from behavior_tree_bot.behaviors import *
from behavior_tree_bot.checks import *
from behavior_tree_bot.bt_nodes import Selector, Sequence, Action, Check

from planet_wars import PlanetWars, finish_turn


# You have to improve this tree or create an entire new one that is capable
# of winning against all the 5 opponent bots
def setup_behavior_tree():
    root = Selector(name='High Level Ordering of Strategies')

    #(main strategy)
    # aggresive bot is too annoying
    anti_aggro = Action(anti_aggressive)

    # first 30 turns
    blitz = Sequence(name='Early Game Blitz')
    blitz_check = Check(is_early_game)
    blitz_action = Action(early_game_aggressive)
    blitz.child_nodes = [blitz_check, blitz_action]

    # desperate
    all_in = Sequence(name='All In Attack')
    all_in_check = Check(should_go_all_in)
    all_in_action = Action(all_in_attack)
    all_in.child_nodes = [all_in_check, all_in_action]
    # Conservative defense
    conservative = Sequence(name='Conservative Defense')
    conservative_check = Check(should_conservative_defense)
    conservative_action = Action(conservative_defense)
    conservative.child_nodes = [conservative_check, conservative_action]
    #  Winning consolidation if ahead
    winning = Sequence(name='Winning Consolidation')
    winning_check = Check(is_winning_comfortably)
    winning_action = Action(winning_consolidation)
    winning.child_nodes = [winning_check, winning_action]

    counter_aggro = Action(counter_aggression)
    root.child_nodes = [anti_aggro, blitz, all_in, conservative, winning, counter_aggro]
    logging.info('\n' + root.tree_to_string())
    return root

# You don't need to change this function
def do_turn(state):
    behavior_tree.execute(planet_wars)

if __name__ == '__main__':
    logging.basicConfig(filename=__file__[:-3] + '.log', filemode='w', level=logging.DEBUG)

    behavior_tree = setup_behavior_tree()
    try:
        map_data = ''
        while True:
            current_line = input()
            if len(current_line) >= 2 and current_line.startswith("go"):
                planet_wars = PlanetWars(map_data)
                do_turn(planet_wars)
                finish_turn()
                map_data = ''
            else:
                map_data += current_line + '\n'

    except KeyboardInterrupt:
        print('ctrl-c, leaving ...')
    except Exception:
        traceback.print_exc(file=sys.stdout)
        logging.exception("Error in bot.")
