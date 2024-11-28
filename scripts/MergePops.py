import json
import os
import re

def merge(this, other):
    '''Merge two state pops.
    '''
    for tag in other.keys():
        if tag in this.keys():
            for other_pop in other[tag]["create_pop"]:
                found = False
                hasAttributeType = "pop_type" in other_pop
                hasAttributeReligion = "religion" in other_pop
                for this_pop in this[tag]["create_pop"]:
                    if other_pop["culture"] != this_pop["culture"]:
                        continue
                    if hasAttributeType and "pop_type" in this_pop:
                        if other_pop["pop_type"] == this_pop["pop_type"]:
                            if hasAttributeReligion and "religion" in this_pop:
                                if other_pop["religion"] == this_pop["religion"]:
                                    this_pop["size"] = int(this_pop["size"]) + int(other_pop["size"])
                                    found = True
                                    break
                            elif not hasAttributeReligion and "religion" not in this_pop:
                                this_pop["size"] = int(this_pop["size"]) + int(other_pop["size"])
                                found = True
                                break
                        continue
                    elif not hasAttributeType and "pop_type" not in this_pop:
                        if hasAttributeReligion and "religion" in this_pop:
                            if other_pop["religion"] == this_pop["religion"]:
                                this_pop["size"] = int(this_pop["size"]) + int(other_pop["size"])
                                found = True
                                break
                        elif not hasAttributeReligion and "religion" not in this_pop:
                            this_pop["size"] = int(this_pop["size"]) + int(other_pop["size"])
                            found = True
                            break
                if not found:
                    this[tag]["create_pop"].append(other_pop)
        else:
            this[tag] = other[tag]

def export(this, name):
    '''Export the state object to a string
    '''
    state_str = f'    {name} = {{\n'
    for tag in this.keys():
        state_str += f'        {tag} = {{\n'
        for pop in this[tag]["create_pop"]:
            state_str += f'            create_pop = {{\n'
            for key, value in pop.items():
                state_str += f'                {key} = {value}\n'
            state_str += f'            }}\n'
        state_str += f'        }}\n'
    state_str += f'    }}\n'

    return state_str


# Destination directory
pops_file = 'C:/Users/ASUS/Documents/Codes/Vic3/pops/05_north_america.json'

# Read states from json
with open(pops_file, 'r', encoding='utf-8') as file:
    pop_dict = json.load(file)

# Merge states
merge_file = 'C:/Users/ASUS/Documents/Codes/Vic3/merge_states.json'
with open(merge_file, 'r', encoding='utf-8') as file:
    merge_dict = json.load(file)
    for diner, food_list in merge_dict.items():
        for food in food_list:
            if ("s:"+food) in pop_dict.keys():
                merge(pop_dict[("s:"+diner)], pop_dict[("s:"+food)])
                print(f'Merged {food} into {diner}')
                pop_dict.pop("s:"+food)

# Export states
output_file = 'C:/Users/ASUS/Documents/Codes/Vic3/pops/05_north_america.txt'
with open(output_file, 'w', encoding='utf-8') as file:
    file.write('POPS = {\n')
    for state_name in pop_dict.keys():
        file.write(export(pop_dict[state_name], state_name))
    file.write('}\n')