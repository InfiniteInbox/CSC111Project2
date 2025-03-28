import csv

from csc111.CSC111Project2 import pokemon_data_scraper
from csc111.CSC111Project2.pokemon_class import Pokemon
def get_team_bst(team: Pokemon | list[Pokemon]):
    """gets the teams bst category"""
    if isinstance(team, Pokemon):
        return team.bst
    else:
        total_bst = 0
        for pokemon in team:
            total_bst += get_team_bst(pokemon)
        return total_bst // len(team)

def ideal_bst_range(team: Pokemon | list[Pokemon]):
    enemy_bst = get_team_bst(team)
    if isinstance(team, Pokemon):
        return [10 - enemy_bst, enemy_bst, 10 + enemy_bst]
    else:
        max_bst = max([pokemon.bst for pokemon in team])
        min_bst = min([pokemon.bst for pokemon in team])
        return [min_bst, enemy_bst, 10 + max_bst]

def get_pokemon(team: list[int], file_path='pokemon_data.csv'):
    poke_list = []
    pokemon = Pokemon()
    for poke in team:
        data = pokemon_data_scraper.get_pokemon_data([poke], file_path)
        pokemon.pokemon_id = data[0]
        pokemon.name = data[1]
        pokemon.type1 = data[2]
        pokemon.type2 = data[3]
        pokemon.stats = data[4:10]
        poke_list.append(pokemon)
    return poke_list


def filter_bst_team(team: list[Pokemon], bst_range: list[int]):
    for pokemon in team:
        if pokemon.bst < bst_range[0]:
            team.remove(pokemon)
        elif pokemon.bst > bst_range[2]:
            team.remove(pokemon)
    return team

def bst_type_score(team: list[Pokemon], type_dict):
    for pokemon in team:
        if (pokemon.type1.name, pokemon.type2.name) in type_dict:
            pokemon.score = type_dict[(pokemon.type1.name, pokemon.type2.name)] * pokemon.bst
            return
        elif pokemon.type1.name in type_dict:
            pokemon.score = type_dict[pokemon.type1.name] * pokemon.bst
            return



def get_enemy_pokemon(team: list[Pokemon], file_pokemon='pokemon_data.csv', file_types='chart.csv'):
    '''get enemy pokemon based on bst and type'''
    types, scores = recommend_top_types(team, file_types, len(team))
    enemy_bst_range = ideal_bst_range(team)
    possible_poke = []
    with open(file_pokemon, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[2] in types or (row[2], row[3]) in types:
                possible_poke = int(row[0])
    poke_data = get_pokemon(possible_poke, file_pokemon)
    po_data = filter_bst_team(poke_data, enemy_bst_range)
    bst_type_score(po_data, scores)
    pok_sorted = sorted(po_data, key=lambda x: x.score, reverse=True)
    final_team = []
    count = len(team)
    while count > 0:
        for pokemon in pok_sorted:
            final_team.append(pokemon.name)
            count -= 1
    return final_team

if __name__ == '__main__':
    get_enemy_pokemon(get_pokemon([1,2,3], 'pokemon_data.csv'), 'pokemon_data.csv', 'chart.csv')
from csc111.CSC111Project2.graph_algorithm import recommend_top_types
