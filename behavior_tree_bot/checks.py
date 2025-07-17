
def is_early_game(state):
    total_planets = len(state.planets)
    neutral_planets = len(state.neutral_planets())
    return neutral_planets > total_planets * 0.3

def is_losing_badly(state):
    my_total_ships = sum(p.num_ships for p in state.my_planets()) + sum(f.num_ships for f in state.my_fleets())
    enemy_total_ships = sum(p.num_ships for p in state.enemy_planets()) + sum(f.num_ships for f in state.enemy_fleets())
    my_growth = sum(p.growth_rate for p in state.my_planets())
    enemy_growth = sum(p.growth_rate for p in state.enemy_planets())
    
    # We're losing badly if enemy has 2x our ships or 10.5 growth
    return enemy_total_ships > my_total_ships *2 or enemy_growth > my_growth * 1.5

def is_winning_comfortably(state):
    my_total_ships = sum(p.num_ships for p in state.my_planets()) + sum(f.num_ships for f in state.my_fleets())
    enemy_total_ships = sum(p.num_ships for p in state.enemy_planets()) + sum(f.num_ships for f in state.enemy_fleets())
    my_growth = sum(p.growth_rate for p in state.my_planets())
    enemy_growth = sum(p.growth_rate for p in state.enemy_planets())
    
    # We're winning comfortably if we have 1.5x their ships or 1.3x their growth
    return my_total_ships > enemy_total_ships * 1.5 and my_growth > enemy_growth * 1.3

def should_go_all_in(state):
    my_planets = state.my_planets()
    enemy_planets = state.enemy_planets()
    
    if not my_planets or not enemy_planets:
        return False
    
    # Go all-in if we have fewer planets and are losing
    if len(my_planets) < len(enemy_planets) and is_losing_badly(state):
        return True
    
    # Go all-in if we have only 2 planets left
    if len(my_planets) <= 2:
        return True
    
    return False

def should_conservative_defense(state):
    my_planets = state.my_planets()
    enemy_fleets = state.enemy_fleets()
    
    # Play conservatively if we have incoming attacks and are outnumbered
    incoming_attacks = sum(1 for f in enemy_fleets if any(p.ID == f.destination_planet for p in my_planets))
    return incoming_attacks > 0 and is_losing_badly(state) 


    