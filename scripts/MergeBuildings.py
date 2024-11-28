import json
import os
import re

# Data structure:
# {
#     "state_name": {
#         "tag": {
#             "create_building": [
#                 {
#                     "building": "building_name",
#                     "add_ownership": [
#                         {
#                             "building": [
#                                 {
#                                     "type": "ownership",
#                                     "country": "country_tag"
#                                     "levels": "levels"
#                                     "region": "region"
#                                 }
#                             ]
#                             "country": [
#                                 {
#                                     "country": "country_tag"
#                                     "levels": "levels"
#                             ]
#                             "company": [
#                                 {
#                                     "type": "company_tag"
#                                     "country": "country_tag"
#                                     "levels": "levels"
#                                 }
#                         }
#                     ]
#                 }
#             ]
# # other keys are ignored
#         }

def merge(this, other): # this, other are "state_name" values
    '''Merge two state buildings.
    '''
    for tag in other.keys():
        if isinstance(other[tag], list):
            continue
        if tag in this.keys():
            if isinstance(this[tag], list):
                this[tag] = other[tag]
                continue
            for other_building in other[tag]["create_building"]:
                found = False
                for this_building in this[tag]["create_building"]:
                    if this_building["building"] == other_building["building"]:
                        found = True
                        if "building" in other_building["add_ownership"][0].keys():
                            if "building" in this_building["add_ownership"][0].keys():
                                for other_ownership in other_building["add_ownership"][0]["building"]:
                                    found_ownership = False
                                    for this_ownership in this_building["add_ownership"][0]["building"]:
                                        # if "type", "country", "region" are the same, merge "levels"
                                        if this_ownership["type"] == other_ownership["type"] and this_ownership["country"] == other_ownership["country"] and this_ownership["region"] == other_ownership["region"]:
                                            found_ownership = True
                                            this_ownership["levels"] = int(this_ownership["levels"]) + int(other_ownership["levels"])
                                            break
                                    if not found_ownership:
                                        this_building["add_ownership"][0]["building"].append(other_ownership)
                            else:
                                this_building["add_ownership"][0]["building"] = other_building["add_ownership"][0]["building"]
                        if "country" in other_building["add_ownership"][0].keys():
                            if "country" in this_building["add_ownership"][0].keys():
                                for other_ownership in other_building["add_ownership"][0]["country"]:
                                    found_ownership = False
                                    for this_ownership in this_building["add_ownership"][0]["country"]:
                                        # if "country" is the same, merge "levels"
                                        if this_ownership["country"] == other_ownership["country"]:
                                            found_ownership = True
                                            this_ownership["levels"] = int(this_ownership["levels"]) + int(other_ownership["levels"])
                                            break
                                    if not found_ownership:
                                        this_building["add_ownership"][0]["country"].append(other_ownership)
                            else:
                                this_building["add_ownership"][0]["country"] = other_building["add_ownership"][0]["country"]
                        if "company" in other_building["add_ownership"][0].keys():
                            if "company" in this_building["add_ownership"][0].keys():
                                for other_ownership in other_building["add_ownership"][0]["company"]:
                                    found_ownership = False
                                    for this_ownership in this_building["add_ownership"][0]["company"]:
                                        # if "type", "country" are the same, merge "levels"
                                        if this_ownership["type"] == other_ownership["type"] and this_ownership["country"] == other_ownership["country"]:
                                            found_ownership = True
                                            this_ownership["levels"] = int(this_ownership["levels"]) + int(other_ownership["levels"])
                                            break
                                    if not found_ownership:
                                        this_building["add_ownership"][0]["company"].append(other_ownership)
                        break
                if not found:
                    this[tag]["create_building"].append(other_building)
        else:
            this[tag] = other[tag]

def export(this, name):
    '''Export the state object to a string
    '''
    if name == "if":
        return ""
    print('Exporting', name)
    state_str = f'    {name} = {{\n'
    for tag in this.keys():
        state_str += f'        {tag} = {{\n'
        if isinstance(this[tag], dict):
            for building in this[tag]["create_building"]:
                state_str += f'            create_building = {{\n'
                state_str += f'                building = {building["building"]}\n'
                if "add_ownership" not in building.keys(): # is monument, only has key "building" & "level"
                    state_str += f'                level = {building["level"]}\n'
                    state_str += f'            }}\n'
                    continue
                state_str += f'                add_ownership = {{\n'
                # print(name, building["building"], building.keys())
                for owner in building["add_ownership"]:
                    if "building" in owner.keys():
                        state_str += f'                    building = {{\n'
                        for ownership in owner["building"]:
                            state_str += f'                        type = {ownership["type"]}\n'
                            state_str += f'                        country = {ownership["country"]}\n'
                            state_str += f'                        levels = {ownership["levels"]}\n'
                            state_str += f'                        region = {ownership["region"]}\n'
                        state_str += f'                    }}\n'
                    if "country" in owner.keys():
                        state_str += f'                    country = {{\n'
                        for ownership in owner["country"]:
                            state_str += f'                        country = {ownership["country"]}\n'
                            state_str += f'                        levels = {ownership["levels"]}\n'
                        state_str += f'                    }}\n'
                    if "company" in owner.keys():
                        state_str += f'                    company = {{\n'
                        for ownership in owner["company"]:
                            state_str += f'                        type = {ownership["type"]}\n'
                            state_str += f'                        country = {ownership["country"]}\n'
                            state_str += f'                        levels = {ownership["levels"]}\n'
                        state_str += f'                    }}\n'
                state_str += f'                }}\n'
                # Building cash reserve
                if "reserves" in building.keys():
                    state_str += f'                reserves = {building["reserves"]}\n'
                # Building production methodss
                if "activate_production_methods" in building.keys():
                    state_str += f'                activate_production_methods = {{\n'
                    if isinstance(building["activate_production_methods"], str):
                        state_str += f'                    {building["activate_production_methods"]}\n'
                    else:
                        for method in building["activate_production_methods"]:
                            state_str += f'                    {method}\n'
                    state_str += f'                }}\n'
                state_str += f'            }}\n'
        state_str += f'        }}\n'
    state_str += f'    }}\n'

    return state_str


# Destination directory
buildings_file = 'StateMergingToolkit\\buildings\\05_north_america.json'

# Read states from json
with open(buildings_file, 'r', encoding='utf-8') as file:
    building_dict = json.load(file)

# Merge states
merge_file = 'StateMergingToolkit\\merge_states.json'
with open(merge_file, 'r', encoding='utf-8') as file:
    merge_dict = json.load(file)

# Merge building ownerships
for diner, food_list in merge_dict.items():
    for state_name in building_dict.keys():
        if state_name == "if":
            continue
        for tag in building_dict[state_name].keys():
            if isinstance(building_dict[state_name][tag], list):
                continue
            for building in building_dict[state_name][tag]["create_building"]:
                if "add_ownership" not in building.keys():
                    continue
                if "building" not in building["add_ownership"][0].keys():
                    continue
                for owner in building["add_ownership"][0]["building"]:
                    # Remove '\"' from owner["region"]
                    region = owner["region"].replace('\"', '')
                    if region in food_list:
                        owner["region"] = '\"'+diner+'\"'


# Merge buildings
for diner, food_list in merge_dict.items():
    for food in food_list:
        if ("s:"+food) in building_dict.keys():
            merge(building_dict[("s:"+diner)], building_dict[("s:"+food)])
            print(f'Merged {food} into {diner}')
            building_dict.pop("s:"+food)

# Export states
output_file = 'StateMergingToolkit\\buildings\\05_north_america.txt'
with open(output_file, 'w', encoding='utf-8') as file:
    file.write('BUILDINGS = {\n')
    for state_name in building_dict.keys():
        file.write(export(building_dict[state_name], state_name))
    file.write('}\n')

print("Don't forget to manually add the 'if dlc' buildings to the output file!")