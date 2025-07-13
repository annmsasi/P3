

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
