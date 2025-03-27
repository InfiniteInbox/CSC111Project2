import pokemon_class
from pokemon_type_data_scraper import read_effectiveness


def graph_builder(file_path):
    types, effectiveness = read_effectiveness(file_path)
    type_indices = {type_name: idx for idx, type_name in enumerate(types)}
    graph = pokemon_class.TypeGraph()
    for p_type in types:
        graph.add_vertex(p_type)
    for po_type in types:
        for pok_type in types:
            graph.add_attacking_edge(po_type, pok_type, effectiveness[type_indices[po_type]][type_indices[pok_type]])
    return graph


def get_effectiveness(graph, attacker, defender):
    if isinstance(defender, tuple):
        # Dual-type defender: effectiveness is the product of effectiveness against each type
        eff1 = get_effectiveness(graph, attacker, defender[0])
        eff2 = get_effectiveness(graph, attacker, defender[1])
        return eff1 * eff2
    else:
        # Single-type defender: retrieve effectiveness from the graph
        vertex = graph.vertices[attacker]
        for weight, neighbors in vertex.outgoing_neighbors.items():
            if defender in {v.item for v in neighbors}:
                return weight
        return 1.0  # Neutral effectiveness if no edge exists


# Helper function to get maximum effectiveness for a dual-type attacker
def get_max_effectiveness(graph, attacker_types, defender):
    if isinstance(attacker_types, tuple):
        # Dual-type attacker: maximum effectiveness of the two types
        eff1 = get_effectiveness(graph, attacker_types[0], defender)
        eff2 = get_effectiveness(graph, attacker_types[1], defender)
        return max(eff1, eff2)
    else:
        # Single-type attacker: direct effectiveness
        return get_effectiveness(graph, attacker_types, defender)


def strong_weak(chosen_pokemons):
    strong = {}
    weak = {}
    graph = graph_builder(file_path='chart.csv')
    all_types = list(graph.vertices.keys())

    for chosen_pokemon in chosen_pokemons:
        if isinstance(chosen_pokemon, tuple):
            # Dual-type Pokémon
            # Attacking: check max effectiveness against each type
            for pok_type in all_types:
                max_eff = get_max_effectiveness(graph, chosen_pokemon, pok_type)
                if max_eff == 2.0:
                    strong[pok_type] = strong.get(pok_type, 0) + 1
                elif max_eff in (0.5, 0.0):
                    weak[pok_type] = weak.get(pok_type, 0) + 1

            # Defending: check combined effectiveness from each type
            for pok_type in all_types:
                combined_eff = get_effectiveness(graph, pok_type, chosen_pokemon)
                if combined_eff > 1.0:  # e.g., 2.0 or 4.0
                    weak[pok_type] = weak.get(pok_type, 0) + 1
                elif combined_eff < 1.0:  # e.g., 0.5, 0.25, or 0.0
                    strong[pok_type] = strong.get(pok_type, 0) + 1
        else:
            # Single-type Pokémon (original logic)
            pokemon_vertex = graph.vertices[chosen_pokemon]
            # Attacking: outgoing edges
            for out in pokemon_vertex.outgoing_neighbors:
                if out == 2.0:
                    for pokemon in pokemon_vertex.outgoing_neighbors[out]:
                        poke = pokemon.item
                        strong[poke] = strong.get(poke, 0) + 1
                elif out in (0.5, 0.0):
                    for pokemon in pokemon_vertex.outgoing_neighbors[out]:
                        poke = pokemon.item
                        weak[poke] = weak.get(poke, 0) + 1
            # Defending: incoming edges
            for inc in pokemon_vertex.incoming_neighbors:
                if inc == 2.0:
                    for pokemon in pokemon_vertex.incoming_neighbors[inc]:
                        poke = pokemon.item
                        weak[poke] = weak.get(poke, 0) + 1
                elif inc in (0.5, 0.0):
                    for pokemon in pokemon_vertex.incoming_neighbors[inc]:
                        poke = pokemon.item
                        strong[poke] = strong.get(poke, 0) + 1
    return strong, weak


def dict_subtraction(strong, weak):
    final_dict = {}
    for poke_type in weak:
        if poke_type in strong:
            temp = weak[poke_type] - strong[poke_type]
            if temp > 0:
                final_dict[poke_type] = temp
        else:
            final_dict[poke_type] = weak[poke_type]
    return final_dict

def get_attacking_effectiveness(graph, attacker, defender):
    """Get effectiveness of attacker against defender from the graph."""
    vertex = graph.vertices[attacker]
    for weight, neighbors in vertex.outgoing_neighbors.items():
        if defender in {v.item for v in neighbors}:
            return weight
    return 1.0  # Neutral if no edge found

def get_defense_effectiveness(graph, attack_type, defend_types):
    """Get effectiveness of attack_type against defend_types (product for dual types)."""
    multiplier = 1.0
    for defend_type in defend_types:
        for weight, vertices in graph.vertices[defend_type].incoming_neighbors.items():
            if attack_type in {v.item for v in vertices}:
                multiplier *= weight
                break
        # If no edge, assume neutral (1.0) for that type
    return multiplier

def score_candidate(graph, candidate_types, enemy_team):
    """Score a candidate type against the enemy team."""
    score = 0
    for enemy in enemy_team:
        # Offensive effectiveness: best attack option
        off_eff = max(get_attacking_effectiveness(graph, c, enemy) for c in candidate_types)
        # Defensive vulnerability: enemy's effectiveness against candidate
        def_vuln = get_defense_effectiveness(graph, enemy, candidate_types)
        score += off_eff - def_vuln
    return score

def score_assigner(final_dict, enemy_types, graph):
    temp = {}
    for key in final_dict:
        defense_0 = 0
        defense_2 = 0
        defense_5 = 0
        attack_0 = 0
        attack_2 = 0
        attack_5 = 0
        one_point_zero = 0
        key = key.capitalize()
        for type in enemy_types:
            if type in {vertex.item for vertex in graph.vertices[key].incoming_neighbors[0.0]}:
                defense_0 += 1
            elif type in {vertex.item for vertex in graph.vertices[key].incoming_neighbors[0.5]}:
                defense_5 += 1
            elif type in {vertex.item for vertex in graph.vertices[key].incoming_neighbors[2.0]}:
                defense_2 += 1
            elif type in {vertex.item for vertex in graph.vertices[key].incoming_neighbors[1.0]}:
                one_point_zero += 1
            elif type in {vertex.item for vertex in graph.vertices[key].outgoing_neighbors[0.0]}:
                attack_0 += 1
            elif type in {vertex.item for vertex in graph.vertices[key].outgoing_neighbors[0.5]}:
                attack_5 += 1
            elif type in {vertex.item for vertex in graph.vertices[key].outgoing_neighbors[2.0]}:
                attack_2 += 1
            elif type in {vertex.item for vertex in graph.vertices[key].incoming_neighbors[1.0]}:
                one_point_zero += 1
        final_score = final_dict[key]*((30*defense_0)+(5*attack_2)+(3*defense_5)+(0.1*one_point_zero)-(4.9*defense_2)-(30*attack_0)-(2.9*attack_5))
        temp[key] = final_score
    return temp

def recommend_top_types(enemy_team, file_path='chart.csv', top_x=None):
    """Recommend the top X types against the enemy team."""
    if top_x is None:
        top_x = len(enemy_team)

    # Build the type effectiveness graph (assumed to be provided)
    graph = graph_builder(file_path)

    strong, weak = strong_weak(enemy_team)

    final_dict = dict_subtraction(strong, weak)

    # Generate all candidate types
    types = list(final_dict.keys())
    single_types = [(t,) for t in types]
    dual_types = []
    for i in range(len(types)):
        for j in range(i + 1, len(types)):
            dual_types.append((types[i], types[j]))
    candidates = single_types + dual_types

    # Score each candidate
    scores = {}
    for cand in candidates:
        scores[cand] = score_candidate(graph, cand, enemy_team)

    # Sort candidates by score (descending)
    sorted_candidates = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    # Get top X and format as strings
    top_candidates = sorted_candidates[:top_x]
    top_types = [(cand[0], cand[1]) if len(cand) > 1 else cand[0] for cand, _ in top_candidates]

    return top_types, scores



if __name__ == '__main__':
    g, scores = recommend_top_types([('Fire', 'Water'), 'Grass', 'Electric'], file_path='chart.csv', top_x=5)




