import sys
sys.path.insert(0, '../')
from planet_wars import issue_order


def attack_weakest_enemy_planet(state):
    # (1) If we currently have a fleet in flight, abort plan.
    if len(state.my_fleets()) >= 1:
        return False

    # (2) Find my strongest planet.
    strongest_planet = max(state.my_planets(), key=lambda t: t.num_ships, default=None)

    # (3) Find the weakest enemy planet.
    weakest_planet = min(state.enemy_planets(), key=lambda t: t.num_ships, default=None)

    if not strongest_planet or not weakest_planet:
        # No legal source or destination
        return False
    else:
        # (4) Send half the ships from my strongest planet to the weakest enemy planet.
        return issue_order(state, strongest_planet.ID, weakest_planet.ID, strongest_planet.num_ships / 2)

def spread_to_weakest_neutral_planet(state):
    # (1) If we currently have a fleet in flight, just do nothing.
    if len(state.my_fleets()) >= 1:
        return False

    # (2) Find my strongest planet.
    strongest_planet = max(state.my_planets(), key=lambda p: p.num_ships, default=None)

    # (3) Find the weakest neutral planet.
    weakest_planet = min(state.neutral_planets(), key=lambda p: p.num_ships, default=None)

    if not strongest_planet or not weakest_planet:
        # No legal source or destination
        return False
    else:
        # (4) Send half the ships from my strongest planet to the weakest enemy planet.
        return issue_order(state, strongest_planet.ID, weakest_planet.ID, strongest_planet.num_ships / 2)

def spread_to_closest_neutral(state):
    # Spreads to the neutral planet closest to the strongest ally planet
    # (1) If we currently have a fleet in flight, just do nothing.
    if len(state.my_fleets()) >= 1:
        return False

    # (2) Find my strongest planet.
    strongest_planet = max(state.my_planets(), key=lambda p: p.num_ships, default=None)

    # (3) Find the closest neutral planet.
    closest_planet = min(state.neutral_planets(), key=lambda p: state.distance(strongest_planet.ID, p.ID), default=None)

    if not strongest_planet or not closest_planet:
        # No legal source or destination
        return False
    else:
        # (4) Send half the ships from my strongest planet to the closest neutral planet.
        # We want to change this so that it only issues an order to spread if our surplus on that planet >= power of the neutral planet
        return issue_order(state, strongest_planet.ID, closest_planet.ID, strongest_planet.num_ships / 2)

    ''''
    # (2) Create a list of each of my planets and their closest neutral planet
    closest_planet = []
    my_planet = []
    for planet in state.my_planets():
        # (3) Find the closest neutral planet to each of our planets.
        closest_planet.append(min(state.neutral_planets(), key=lambda p: state.distance(planet.ID, p.ID), default=None))
        my_planet.append(planet)

    if not closest_planet:
        # No legal source or destination
        return False
    else:
        # (4) Send half the ships from my strongest planet to the weakest enemy planet.
        return issue_order(state, strongest_planet.ID, closest_planet.ID, strongest_planet.num_ships / 2)
    '''


    
def find_surplus():
    # Helper
    pass

def find_weakest():
    # Helper
    pass

def find_closest():
    # Helper
    pass

def attack_weakest():
    # Behavior
    pass



def defend_planets():
    # Behavior
    pass

def sort_strength(planets):
    pass

def spread_to_furthest_neutral(state):
    # Spread to the neutral planet furthest from the strongest enemy planet
    # (1) If we currently have a fleet in flight, just do nothing.
    if len(state.my_fleets()) >= 1:
        return False

    # (2) Find the enemy strongest planet.
    strongest_planet = max(state.enemy_planets(), key=lambda p: p.num_ships, default=None)

    # (3) Find the furthest neutral planet.
    furthest_planet = max(state.neutral_planets(), key=lambda p: state.distance(strongest_planet.ID, p.ID), default=None)

    if not strongest_planet or not furthest_planet:
        # No legal source or destination
        return False
    else:
        # (4) Send half the ships from my strongest planet to the weakest enemy planet.
        # We want to change this so that it only issues an order to spread if our surplus on that planet >= power of the neutral planet
        return issue_order(state, strongest_planet.ID, furthest_planet.ID, strongest_planet.num_ships / 2)
