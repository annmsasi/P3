

def if_neutral_planet_available(state):
    return any(state.neutral_planets())


def have_largest_fleet(state):
    return sum(planet.num_ships for planet in state.my_planets()) \
             + sum(fleet.num_ships for fleet in state.my_fleets()) \
           > sum(planet.num_ships for planet in state.enemy_planets()) \
             + sum(fleet.num_ships for fleet in state.enemy_fleets())

def check_incoming_fleets(state):
    my_planet_ids = {planet.ID for planet in state.my_planets()}
    
    for fleet in state.enemy_fleets():
        if fleet.destination_planet in my_planet_ids:
            return True  # We have at least one incoming threat

    return False

def check_growth(state):
    # Growth constant, adjust as needed to prioritize growth
    growth_constant = 1.0

    # Tally the growth rate of my planets and compare it to the enemy's
    my_growth = sum(planet.growth_rate for planet in state.my_planets())
    enemy_growth = sum(planet.growth_rate for planet in state.enemy_planets())

    # Assume that the fleets in flight will affect the growth rates of both sides
    destinations = [fleet.destination_planet for fleet in state.my_fleets()]
    for destination in destinations:
        # check if the destination is a neutral planet and it has a lower number of ships than all fleets targeting it
        sum_ships = sum(fleet.num_ships for fleet in state.my_fleets() if fleet.destination_planet == destination)
        if destination in state.neutral_planets() and destination.num_ships < sum_ships:
            my_growth += destination.growth_rate
    
    # Check the enemy's fleets in flight
    destinations = [fleet.destination_planet for fleet in state.my_fleets()]
    for destination in destinations:
        # check if the destination is a neutral planet and it has a lower number of ships than all fleets targeting it
        sum_ships = sum(fleet.num_ships for fleet in state.my_fleets() if fleet.destination_planet == destination)
        if destination in state.neutral_planets() and destination.num_ships < sum_ships:
            enemy_growth += destination.growth_rate
    return my_growth <= enemy_growth * growth_constant

def if_many_neutral_planets_available(state):
    # Check if there are more neutral planets than my planets and enemy planets combined
    return len(state.neutral_planets()) > len(state.my_planets()) + len(state.enemy_planets())    
    