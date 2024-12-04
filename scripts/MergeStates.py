import json
import os
import re

# Data structure:
# {
#     "state_name": {
#         "create_state": [
#             {
#                 "country": "country_tag",
#                 "owned_provinces": [
#                     "province_id"
#                 ],
#                 "state_type": "unincorporated" # Optional
#             }
#         ],
#         "add_homeland": [
#             "culture_tag"
#         ],
#         "add_claim": [
#             "country_tag"
#         ]
#     }

def merge(this, other): # this, other are "state_name" values
    '''Merge two state buildings.
    '''
    # Merge create_state
    for province in other["create_state"]:
        found = False
        for province_ref in this["create_state"]:
            if province["country"][0] == province_ref["country"][0]:
                found = True
                province_ref["owned_provinces"] += province["owned_provinces"]
                break
        if not found:
            this["create_state"].append(province)
    # Merge add_homeland
    for culture in other["add_homeland"]:
        if culture not in this["add_homeland"]:
            this["add_homeland"].append(culture)
    # Merge add_claim
    if "add_claim" not in this.keys():
        if "add_claim" in other.keys():
            this["add_claim"] = other["add_claim"]
    elif "add_claim" in other.keys():
        for country in other["add_claim"]:
            if country not in this["add_claim"]:
                this["add_claim"].append(country)

def export(this, name):
    '''Export the state object to a string
    '''
    print('Exporting', name)
    state_str = f'    {name} = {{\n'
    for province in this["create_state"]:
        state_str += f'        create_state = {{\n'
        state_str += f'            country = {province["country"][0]}\n'
        state_str += f'            owned_provinces = {{ '
        for owned_province in province["owned_provinces"]:
            state_str += f'{owned_province} '
        state_str += '}\n'
        if "state_type" in province.keys():
            for state_type in province["state_type"]:
                state_str += f'            state_type = {state_type}\n'
        state_str += '        }\n\n'
    if "add_homeland" in this.keys():
        for culture in this["add_homeland"]:
            state_str += f'        add_homeland = {culture}\n'
    if "add_claim" in this.keys():
        for country in this["add_claim"]:
            state_str += f'        add_claim = {country}\n'
    state_str += '    }\n'

    return state_str


# Destination directory
states_file = 'StateMergingToolkit\\states\\00_states.json'

# Read states from json
with open(states_file, 'r', encoding='utf-8') as file:
    state_dict = json.load(file)

# Merge states
merge_file = 'StateMergingToolkit\\merge_states.json'
with open(merge_file, 'r', encoding='utf-8') as file:
    merge_dict = json.load(file)

# Merge states
for diner, food_list in merge_dict.items():
    for food in food_list:
        if ("s:"+food) in state_dict.keys():
            merge(state_dict[("s:"+diner)], state_dict[("s:"+food)])
            print(f'Merged {food} into {diner}')
            state_dict.pop("s:"+food)

# Export states
output_file = 'StateMergingToolkit\\states\\00_states.txt'
with open(output_file, 'w', encoding='utf-8') as file:
    file.write('STATES = {\n')
    for state_name in state_dict.keys():
        file.write(export(state_dict[state_name], state_name))
    file.write('}\n')
