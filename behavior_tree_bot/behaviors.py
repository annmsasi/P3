import sys
sys.path.insert(0, '../')
from planet_wars import issue_order
from collections import defaultdict


def counter_aggression(state):
    # Specialized behavior to counter aggressive strate
    action_taken = False
    my_planets = state.my_planets()
    enemy_fleets = state.enemy_fleets()
    enemy_planets = state.enemy_planets()
    neutral_planets = state.neutral_planets()

    #Defend against incoming
    for fleet in enemy_fleets:
        target_planet = next((p for p in my_planets if p.ID == fleet.destination_planet), None)
        if target_planet:
            turns_until_arrival = fleet.turns_remaining
            expected_defense = target_planet.num_ships + (target_planet.growth_rate * turns_until_arrival)
            ships_needed = max(0, fleet.num_ships - expected_defense + 1)
            if ships_needed > 0:
                ships_to_send = ships_needed
                for sp in sorted(my_planets, key=lambda p: state.distance(p.ID, target_planet.ID)):
                    if sp.ID == target_planet.ID:
                        continue
                    surplus = sp.num_ships - 1
                    if surplus > 0 and ships_to_send > 0:
                        send = min(surplus, ships_to_send)
                        issue_order(state, sp.ID, target_planet.ID, send)
                        ships_to_send -= send
                        action_taken = True
                    if ships_to_send <= 0:
                        break
                if action_taken:
                    return action_taken

    #attack all weak enemy planets
    if not action_taken and len(state.my_fleets()) < 2 and enemy_planets:
        for enemy_planet in sorted(enemy_planets, key=lambda p: p.growth_rate, reverse=True):
            # Prioritize high-growth enemy planets
            if any(fleet.destination_planet == enemy_planet.ID for fleet in state.my_fleets()):
                continue
            required_ships = enemy_planet.num_ships + 1
            # Try to send from multiple of our planets if needed
            ships_to_send = required_ships
            for my_planet in sorted(my_planets, key=lambda p: state.distance(p.ID, enemy_planet.ID)):
                surplus = my_planet.num_ships - 1
                if surplus > 0 and ships_to_send > 0:
                    send = min(surplus, ships_to_send)
                    issue_order(state, my_planet.ID, enemy_planet.ID, send)
                    ships_to_send -= send
                    action_taken = True
                if ships_to_send <= 0:
                    break
        if action_taken:
            return action_taken

    # neutral planets about to be captured by the enemy
    if not action_taken and neutral_planets:
        for neutral in neutral_planets:
            incoming_enemy_fleets = [f for f in state.enemy_fleets() if f.destination_planet == neutral.ID]
            if not incoming_enemy_fleets:
                continue
            soonest_enemy_fleet = min(incoming_enemy_fleets, key=lambda f: f.turns_remaining)
            for my_planet in my_planets:
                my_distance = state.distance(my_planet.ID, neutral.ID)
                if my_distance == soonest_enemy_fleet.turns_remaining + 1 and my_planet.num_ships > neutral.num_ships + 1:
                    issue_order(state, my_planet.ID, neutral.ID, neutral.num_ships + 1)
                    action_taken = True
                    break
            if action_taken:
                break
        if action_taken:
            return action_taken

    # Aggressively capture neutral planets
    if not action_taken and neutral_planets:
        for neutral in sorted(neutral_planets, key=lambda p: p.growth_rate, reverse=True):
            required_ships = neutral.num_ships + 1
            ships_to_send = required_ships
            for my_planet in sorted(my_planets, key=lambda p: state.distance(p.ID, neutral.ID)):
                surplus = my_planet.num_ships - 1
                if surplus > 0 and ships_to_send > 0:
                    send = min(surplus, ships_to_send)
                    issue_order(state, my_planet.ID, neutral.ID, send)
                    ships_to_send -= send
                    action_taken = True
                if ships_to_send <= 0:
                    break
        if action_taken:
            return action_taken

def all_in_attack(state):
    # Desperate when we're losing badly
    action_taken = False
    my_planets = state.my_planets()
    enemy_planets = state.enemy_planets()
    
    if not my_planets or not enemy_planets:
        return action_taken
    
    # Find the weakest enemy planet
    target = min(enemy_planets, key=lambda p: p.num_ships)
    
    # Send ALL ships from ALL our planets
    for my_planet in my_planets:
        if my_planet.num_ships > 1:
            issue_order(state, my_planet.ID, target.ID, my_planet.num_ships - 1)
            action_taken = True
    
    return action_taken

def conservative_defense(state):
    # only defend, never attack
    action_taken = False
    my_planets = state.my_planets()
    enemy_fleets = state.enemy_fleets()
    
    if not my_planets or not enemy_fleets:
        return action_taken
    
    # Reinforce any planet w/ ALL available ships
    for fleet in enemy_fleets:
        target_planet = next((p for p in my_planets if p.ID == fleet.destination_planet), None)
        if target_planet:
            # Send reinforcements from all other planets
            for sp in my_planets:
                if sp.ID != target_planet.ID and sp.num_ships > 1:
                    issue_order(state, sp.ID, target_planet.ID, sp.num_ships - 1)
                    action_taken = True
    
    return action_taken

def winning_consolidation(state):
    # When winning finish the enemy
    action_taken = False
    my_planets = state.my_planets()
    enemy_planets = state.enemy_planets()
    
    if not my_planets or not enemy_planets:
        return action_taken
    
    target = max(enemy_planets, key=lambda p: p.num_ships)
    required_ships = target.num_ships +1 
    # Send ships from multiple planets to win
    ships_to_send = required_ships
    for my_planet in sorted(my_planets, key=lambda p: state.distance(p.ID, target.ID)):
        surplus = my_planet.num_ships - 1
        if surplus > 0 and ships_to_send > 0:
            send = min(surplus, ships_to_send)
            issue_order(state, my_planet.ID, target.ID, send)
            ships_to_send -= send
            action_taken = True
        if ships_to_send <= 0:
            break
    
    return action_taken

def early_game_aggressive(state):
    # For the first 30 turns, send ships to all neutral and weak
    action_taken = False
    my_planets = state.my_planets()
    neutral_planets = state.neutral_planets()
    enemy_planets = state.enemy_planets()
    turn = getattr(state, 'turn', 1)
    if not hasattr(state, 'turn'):
        turn = max([getattr(f, 'turns_remaining', 0) for f in state.my_fleets() + state.enemy_fleets()] + [1])
    if turn > 30:
        return False
    # Track available ships for each planet locally
    available_ships = {p.ID: p.num_ships for p in my_planets}
    for neutral in sorted(neutral_planets, key=lambda p: (-p.growth_rate, p.num_ships)):
        for my_planet in sorted(my_planets, key=lambda p: state.distance(p.ID, neutral.ID)):
            if available_ships[my_planet.ID] > neutral.num_ships + 1:
                if not any(fleet.destination_planet == neutral.ID for fleet in state.my_fleets()):
                    issue_order(state, my_planet.ID, neutral.ID, neutral.num_ships + 1)
                    available_ships[my_planet.ID] -= (neutral.num_ships + 1)
                    action_taken = True
                    break
    for enemy in sorted(enemy_planets, key=lambda p: p.num_ships):
        for my_planet in sorted(my_planets, key=lambda p: state.distance(p.ID, enemy.ID)):
            required = int(enemy.num_ships * 1.1) + 1
            if available_ships[my_planet.ID] > required:
                issue_order(state, my_planet.ID, enemy.ID, required)
                available_ships[my_planet.ID] -= required
                action_taken = True
                break
    return action_taken

def anti_aggressive(state):
    action_taken = False
    my_planets = state.my_planets()
    enemy_planets = state.enemy_planets()
    neutral_planets = state.neutral_planets()
    enemy_fleets = state.enemy_fleets()
    # identify vulnerable planets
    enemy_launched_fleets = [f for f in enemy_fleets if f.owner == 2]
    total_enemy_launched = sum(f.num_ships for f in enemy_launched_fleets)
    # Counter-attack
    if enemy_planets and total_enemy_launched > 0:
        for enemy_planet in sorted(enemy_planets, key=lambda p: p.growth_rate, reverse=True):
            outgoing_from_this = sum(f.num_ships for f in enemy_launched_fleets 
                                   if hasattr(f, 'source_planet') and f.source_planet == enemy_planet.ID)
            
            if outgoing_from_this > 0 or enemy_planet.num_ships < 5:  # Planet is vulnerable
                for my_planet in sorted(my_planets, key=lambda p: state.distance(p.ID, enemy_planet.ID)):
                    distance = state.distance(my_planet.ID, enemy_planet.ID)
                    required = enemy_planet.num_ships + (distance * enemy_planet.growth_rate) + 1
                    
                    if my_planet.num_ships > required + 2: # Keep 2 ships for defense
                        issue_order(state, my_planet.ID, enemy_planet.ID, required)
                        action_taken = True
                        break
                if action_taken:
                    break
    # Capture close neutral planets 
    if not action_taken and neutral_planets:
        for neutral in sorted(neutral_planets, key=lambda p: p.growth_rate, reverse=True):
            if not my_planets or not enemy_planets:
                continue
            my_closest = min(my_planets, key=lambda p: state.distance(p.ID, neutral.ID))
            enemy_closest = min(enemy_planets, key=lambda p: state.distance(p.ID, neutral.ID))
            
            my_distance = state.distance(my_closest.ID, neutral.ID)
            enemy_distance = state.distance(enemy_closest.ID, neutral.ID)
            
            if my_distance < enemy_distance or my_closest.num_ships > neutral.num_ships * 2:
                if not any(f.destination_planet == neutral.ID for f in state.my_fleets()):
                    if my_closest.num_ships > neutral.num_ships + 2:
                        issue_order(state, my_closest.ID, neutral.ID, neutral.num_ships + 1)
                        action_taken = True
                        break
    
    if not action_taken:
        for fleet in enemy_fleets:
            target_planet = next((p for p in my_planets if p.ID == fleet.destination_planet), None)
            if target_planet:
                turns_until_arrival = fleet.turns_remaining
                expected_defense = target_planet.num_ships + (target_planet.growth_rate * turns_until_arrival)
                ships_needed = max(0, fleet.num_ships - expected_defense + 1)
                if ships_needed > 0:
                    for sp in sorted(my_planets, key=lambda p: state.distance(p.ID, target_planet.ID)):
                        if sp.ID != target_planet.ID and sp.num_ships > ships_needed + 1:
                            issue_order(state, sp.ID, target_planet.ID, ships_needed)
                            action_taken = True
                            break
                    if action_taken:
                        break
    #  Attack weakest enemy planet if no other action taken
    if not action_taken and enemy_planets:
        weakest_enemy = min(enemy_planets, key=lambda p: p.num_ships)
        for my_planet in sorted(my_planets, key=lambda p: state.distance(p.ID, weakest_enemy.ID)):
            distance = state.distance(my_planet.ID, weakest_enemy.ID)
            required = weakest_enemy.num_ships + (distance * weakest_enemy.growth_rate) + 1
            
            if my_planet.num_ships > required + 1:
                issue_order(state, my_planet.ID, weakest_enemy.ID, required)
                action_taken = True
                break
    return action_taken