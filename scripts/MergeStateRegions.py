import json
import os
import re

seq_str = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight"]

class state:
    '''Class for state objects in 'StateMergingToolkit/map_data'
    name: string, state name
    id: int, state id
    subsistence_building: string, what kind of subsistence building the state has
    provinces: list of string, provinces in the state
    impassable: list of string, impassable provinces in the state
    traits: list of string, traits of the state
    city: string, province id of the state capital
    port: string, province id of the state port
    farm: string, province id of the state farm
    mine: string, province id of the state mine
    wood: string, province id of the state wood
    arable_land: int, amount of arable land in the state
    arable_resources: list of string, what kind of available agriculture buildings the state has
    capped_resources: dict, capped resources in the state
    naval_exit_id: int, corresponding sea node id for the state
    '''
    name = ''
    id = 0
    subsistence_building = ''
    provinces = []
    impassable = []
    traits = []
    city = ''
    port = ''
    farm = ''
    mine = ''
    wood = ''
    arable_land = 0
    arable_resources = []
    capped_resources = {}
    naval_exit_id = -1

    def __init__(self, name, dict):
        '''Initialize the state object with a dictionary
        '''
        self.name = name
        dict_data = dict[name]
        # print(dict_data)
        self.id = int(dict_data['id'])
        self.subsistence_building = dict_data['subsistence_building']
        self.provinces = dict_data['provinces']
        if 'impassable' in dict_data.keys():
            self.impassable = dict_data['impassable']
        else:
            self.impassable = []
        if 'traits' in dict_data.keys():
            self.traits = dict_data['traits']
        else:
            self.traits = []
        self.city = dict_data['city']
        if 'port' in dict_data.keys():
            self.port = dict_data['port']
        else:
            self.port = ''
        self.farm = dict_data['farm']
        if 'mine' in dict_data.keys():
            self.mine = dict_data['mine']
        else:
            self.mine = ''
        if 'wood' in dict_data.keys():
            self.wood = dict_data['wood']
        else:
            self.wood = ''
        self.arable_land = int(dict_data['arable_land'])
        self.arable_resources = dict_data['arable_resources']
        self.capped_resources = {}
        if 'capped_resources' in dict_data.keys():
            for resource, amount in dict_data['capped_resources'].items():
                # print(resource, amount)
                self.capped_resources[resource] = int(amount)
        if 'naval_exit_id' in dict_data.keys():
            self.naval_exit_id = dict_data['naval_exit_id']
        else:
            self.naval_exit_id = -1

    def merge_states_cnt(self):
        '''Determine the number of states merged in the state
        '''
        for i in range(2, 9):
            if f'"state_trait_{seq_str[i]}_states_integration"' in self.traits:
                return i
        return 1
    
    def merge_coast_cnt(self):
        '''Determine the number of coast states merged in the state
        '''
        if self.naval_exit_id == -1:
            return 0
        for i in range(2, 7):
            if f'"state_trait_{seq_str[i]}_coast_integration"' in self.traits:
                return i
        return 1

    def merge(self, other):
        '''Merge two state objects.
        '''
        # provinces: list append
        self.provinces += other.provinces
        # impassable: list append
        self.impassable += other.impassable
        # traits: list append, remove "state_trait_two_states_integration", "state_trait_three_states_integration", "state_trait_four_states_integration", etc., and add the corresponding trait according to merge_states_cnt(convert to string)
        thisMergeStatesCnt = self.merge_states_cnt()
        otherMergeStatesCnt = other.merge_states_cnt()
        thisCoastCnt = self.merge_coast_cnt()
        otherCoastCnt = other.merge_coast_cnt()
        if thisMergeStatesCnt > 1:
            self.traits.remove(f'"state_trait_{seq_str[thisMergeStatesCnt]}_states_integration"')
        if thisCoastCnt > 1:
            self.traits.remove(f'"state_trait_{seq_str[thisCoastCnt]}_coast_integration"')
        for trait in other.traits:
            if trait != f'"state_trait_{seq_str[otherMergeStatesCnt]}_states_integration"' and trait != f'"state_trait_{seq_str[otherCoastCnt]}_coast_integration"' and trait not in self.traits:
                self.traits.append(trait)
        if (thisMergeStatesCnt + otherMergeStatesCnt < 8):
            self.traits.append(f'"state_trait_{seq_str[thisMergeStatesCnt + otherMergeStatesCnt]}_states_integration"')
        else:
            self.traits.append('"state_trait_eight_states_integration"')
        if (thisCoastCnt + otherCoastCnt > 1) and (thisCoastCnt + otherCoastCnt < 6):
            self.traits.append(f'"state_trait_{seq_str[thisCoastCnt + otherCoastCnt]}_coast_integration"')
        elif (thisCoastCnt + otherCoastCnt >= 6):
            self.traits.append('"state_trait_six_coast_integration"')
        # arable_land: int sum
        self.arable_land += other.arable_land
        # arable_resources: list append
        for resource in other.arable_resources:
            if resource not in self.arable_resources:
                self.arable_resources.append(resource)
        # capped_resources: dict add each key-value pair
        for resource, amount in other.capped_resources.items():
            if resource in self.capped_resources.keys():
                self.capped_resources[resource] += int(amount)
            else:
                self.capped_resources[resource] = int(amount)
        # city, port, farm, mine, wood, naval_exit_id: keep the value of self except they are '' or -1, in which case update them with the value of other
        if self.port == '':
            self.port = other.port
        if self.mine == '':
            self.mine = other.mine
        if self.wood == '':
            self.wood = other.wood
        if self.naval_exit_id == -1:
            self.naval_exit_id = other.naval_exit_id
 
    def export(self):
        '''Export the state object to a string
        '''
        state_str = f'{self.name} = {{\n'
        state_str += f'    id = {self.id}\n'
        state_str += f'    subsistence_building = {self.subsistence_building}\n'
        state_str += f'    provinces = {{ '
        for province in self.provinces:
            state_str += f'{province} '
        state_str += f'}}\n'
        if self.impassable != []:
            state_str += f'    impassable = {{ '
            for province in self.impassable:
                state_str += f'{province} '
            state_str += f'}}\n'
        if self.traits != []:
            state_str += f'    traits = {{ '
            for trait in self.traits:
                state_str += f'{trait} '
            state_str += f'}}\n'
        state_str += f'    city = {self.city}\n'
        if self.port != '':
            state_str += f'    port = {self.port}\n'
        state_str += f'    farm = {self.farm}\n'
        if self.mine != '':
            state_str += f'    mine = {self.mine}\n'
        if self.wood != '':
            state_str += f'    wood = {self.wood}\n'
        state_str += f'    arable_land = {self.arable_land}\n'
        state_str += f'    arable_resources = {{ '
        for resource in self.arable_resources:
            state_str += f'{resource} '
        state_str += f'}}\n'
        if self.capped_resources:
            state_str += f'    capped_resources = {{\n'
            for resource, amount in self.capped_resources.items():
                state_str += f'        {resource} = {amount}\n'
            state_str += f'    }}\n'
        if self.naval_exit_id != -1:
            state_str += f'    naval_exit_id = {self.naval_exit_id}\n'
        state_str += f'}}\n\n'

        return state_str


# Destination directory
states_file = 'StateMergingToolkit/map_data/05_north_america.json'

# Read states from json
states = {}
keys = []
with open(states_file, 'r', encoding='utf-8') as file:
    states_dict = json.load(file)
for state_name in states_dict.keys():
    states[state_name] = state(state_name, states_dict)

# Merge states
merge_file = 'StateMergingToolkit/merge_states.json'
with open(merge_file, 'r', encoding='utf-8') as file:
    merge_dict = json.load(file)
    for diner, food_list in merge_dict.items():
        for food in food_list:
            if food in states.keys():
                states[diner].merge(states[food])
                print(f'Merged {food} into {diner}')
                states.pop(food)

# Export states
output_file = 'StateMergingToolkit/map_data/05_north_america.txt'
with open(output_file, 'w', encoding='utf-8') as file:
    for state_name in states.keys():
        file.write(states[state_name].export())
