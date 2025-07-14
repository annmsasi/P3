import sys
sys.path.insert(0, '../')
from planet_wars import issue_order
from collections import defaultdict


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
    action_taken = False

    # For each planet, check if it has a surplus of ships
    for planet in state.my_planets():
        # surplus = find_surplus(state, planet)
        # if surplus <= 0:
        #     continue

        # Find the closest neutral planet
        closest_neutral = min(state.neutral_planets(), key=lambda p: state.distance(planet.ID, p.ID), default=None)

        # If we found a neutral planet, issue an order to spread if no fleet is already in flight to that neutral planet
        if closest_neutral and (planet.num_ships > closest_neutral.num_ships + 1) and not any(fleet.destination_planet == closest_neutral.ID for fleet in state.my_fleets()):
            issue_order(state, planet.ID, closest_neutral.ID, closest_neutral.num_ships + 1)
            action_taken = True
        
    return action_taken
    

# “The surplus of player P at planet A at time t is the number of ships that can be sent away on that turn from the defending army without:
# making any scheduled order from planet A invalid
# causing the planet to be lost anytime after that (observing only the fleets already in space)
# bringing an imminent loss closer in time


def find_surplus(state, planet, horizon= 20):
    """
    Estimate how many ships can be safely sent from the given planet.

    Args:
        state (PlanetWars): Current game state
        planet (Planet): The planet to compute surplus for
        horizon (int): How many turns into the future to simulate

    Returns:
        int: Number of ships that can safely be sent this turn
    """
    # Net ship changes from fleets arriving at this planet per future turn
    timeline = defaultdict(int)

    for fleet in state.my_fleets() + state.enemy_fleets():
        if fleet.destination_planet == planet.ID:
            arrival_turn = fleet.turns_remaining
            if fleet.owner == planet.owner:
                timeline[arrival_turn] += fleet.num_ships  # Friendly reinforcement
            else:
                timeline[arrival_turn] -= fleet.num_ships  # Enemy attack

    ships = planet.num_ships
    min_future_ships = ships

    # Simulate up to `horizon` turns
    for t in range(1, horizon + 1):
        ships += planet.growth_rate
        ships += timeline[t]
        ships = max(ships, 0)  # A planet can't have negative ships
        min_future_ships = min(min_future_ships, ships)

    # Surplus is how many ships can be safely removed now
    surplus = max(0, planet.num_ships - min_future_ships)
    return surplus

def find_weakest():
    # Helper
    pass

# Takes the strongest planet and finds the closest planet to it
def find_closest(state, strongest_planet):
    return min(state.planets(), key=lambda p: state.distance(strongest_planet.ID, p.ID), default=None)
    
def attack_weakest():
    # Behavior
    pass


def defend_planets(state):
    my_planets = state.my_planets()
    enemy_fleets = sorted(state.enemy_fleets(), key=lambda f: f.num_ships)

    if not my_planets or not enemy_fleets:
        return False

    avg_strength = sum(p.num_ships for p in my_planets) / len(my_planets)

    strong_planets = [p for p in my_planets if p.num_ships > avg_strength]
    if not strong_planets:
        return False

    action_taken = False

    for fleet in enemy_fleets:
        # Is it targeting our planet?
        target_planet = next((p for p in my_planets if p.ID == fleet.destination_planet), None)
        if not target_planet:
            continue

        # Estimate how many ships are needed to defend
        turns = fleet.turns_remaining
        expected_growth = target_planet.growth_rate * turns
        predicted_defense = target_planet.num_ships + expected_growth
        ships_needed = fleet.num_ships - predicted_defense + 1

        if ships_needed <= 0:
            continue  # Planet can defend itself

        # Find strongest planet that can afford to help
        for sp in sorted(strong_planets, key=lambda p: p.num_ships, reverse=True):
            surplus = find_surplus(state, sp)
            if surplus >= ships_needed:
                issue_order(state, sp.ID, target_planet.ID, ships_needed)
                action_taken = True
                break
            elif surplus > 0:
                issue_order(state, sp.ID, target_planet.ID, surplus)
                action_taken = True

    return action_taken

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

def creep(state):
    # Re-Allocate ships to the planet closest to the enemy
    action_taken = False
    my_planets = state.my_planets()
    if not my_planets:
        return action_taken
    # Find the closest enemy planet
    closest_enemy_planet = min(state.enemy_planets(), key=lambda p: state.distance(my_planets[0].ID, p.ID), default=None)
    if not closest_enemy_planet:
        return action_taken
    # Find the closest of my planets to the enemy planet
    closest_my_planet = min(my_planets, key=lambda p: state.distance(p.ID, closest_enemy_planet.ID), default=None)
    if not closest_my_planet:
        return action_taken
    # If the closest planet to the enemy has more ships than the enemy planet, do nothing and hold the position
    if closest_my_planet.num_ships > closest_enemy_planet.num_ships:
        return action_taken
    else:
        # Otherwise, we want to bolster the closest planet to the enemy with ships from our other planets if a fleet is not already in flight to that planet
        for planet in my_planets:
            if planet.ID != closest_my_planet.ID and planet.num_ships > 1 and not any(fleet.destination_planet == closest_my_planet.ID for fleet in state.my_fleets()):
                issue_order(state, planet.ID, closest_my_planet.ID, planet.num_ships - 1)
                action_taken = True

    return action_taken

def reckless_spread(state):
    # Spread to the neutral planets with the largest combined growth rate
    action_taken = False
    neutral_planets = state.neutral_planets()

    # If there are no neutral planets, do nothing
    if not neutral_planets:
        return action_taken
    
    # Sort neutral planets by growth rate return in descending order
    sorted_neutral_planets = sorted(neutral_planets, key=lambda p: (p.growth_rate / (p.num_ships + 1)), reverse=True)

    # For each planet in the sorted list, try to spread from the closest of my planets
    for neutral_planet in sorted_neutral_planets:
        # Check if we have a fleet already in flight to this neutral planet
        if any(fleet.destination_planet == neutral_planet.ID for fleet in state.my_fleets()):
            continue

        # Array to hold the potential source planets and allocatable ships
        source_planets = []
        # Variable to tally the total surplus ships of nearby ally planets
        total_ships = 0

        # Sort my planets by distance to the neutral planet
        my_planets = sorted(state.my_planets(), key=lambda p: state.distance(p.ID, neutral_planet.ID))
        for my_planet in my_planets:
            if my_planet.num_ships > 1:  # Only consider planets with more than 1 ship
                total_ships += min(my_planet.num_ships - 1, neutral_planet.num_ships + 1)
                source_planets.append(my_planet)
            # If we have enough ships to spread to the neutral planet, issue the order
            if total_ships >= neutral_planet.num_ships + 1:
                # Issue the order from each planet that has enough ships
                for source_planet in source_planets:
                    total_ships -= min(source_planet.num_ships - 1, neutral_planet.num_ships + 1)
                    issue_order(state, source_planet.ID, neutral_planet.ID, min(source_planet.num_ships - 1, neutral_planet.num_ships + 1))
                action_taken = True
                break
        

    return action_taken