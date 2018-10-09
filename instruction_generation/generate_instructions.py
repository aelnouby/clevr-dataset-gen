"""
Generate Instuctions for adding objects
based on realtive positions
"""
import json
import argparse
from glob import glob
import os

import numpy as np
from tqdm import tqdm


class CLEVRObject():
    def __init__(self, index, color, shape):
        self.index = index
        self.color = color
        self.shape = shape


def generate_instructions(json_path):
    with open(json_path, 'r') as f:
        scene_description = json.load(f)
    objects = []
    for i, item in enumerate(scene_description['objects']):
        clevr_object = CLEVRObject(index=i,
                                   color=item['color'],
                                   shape=item['shape'])
        objects.append(clevr_object)

    relationships = _get_relationships(scene_description)

    instructions = []
    for i in range(len(objects)):
        if i == 0:
            insturction = 'Add a {} {} at the center'.format(objects[i].color,
                                                             objects[i].shape)
        elif i == 1:
            relative_position = relationships[i][0]
            if relative_position[0] and relative_position[1]:
                insturction = 'Add a {} {} {} the {} {} on the {}'\
                    .format(objects[i].color,
                            objects[i].shape,
                            relative_position[0],
                            objects[0].color,
                            objects[0].shape,
                            relative_position[1])

            elif relative_position[0]:
                insturction = 'Add a {} {} {} the {} {}'\
                    .format(objects[i].color,
                            objects[i].shape,
                            relative_position[0],
                            objects[0].color,
                            objects[0].shape)

            elif relative_position[1]:
                insturction = 'Add a {} {} on the {} of the {} {}'\
                    .format(objects[i].color,
                            objects[i].shape,
                            relative_position[1],
                            objects[0].color,
                            objects[0].shape)
            else:
                raise Exception('No relation available. Aborting.')

        else:
            relative_items = np.random.choice(list(relationships[i].keys()),
                                              2,
                                              replace=False)

            position_a = relationships[i][relative_items[0]]
            position_b = relationships[i][relative_items[1]]

            if position_a[0] and position_a[1]:
                insturction_a = 'Add a {} {} {} the {} {} on the {}'\
                    .format(objects[i].color,
                            objects[i].shape,
                            position_a[0],
                            objects[relative_items[0]].color,
                            objects[relative_items[0]].shape,
                            position_a[1])
            elif position_a[0]:
                insturction_a = 'Add a {} {} {} the {} {}'\
                    .format(objects[i].color,
                            objects[i].shape,
                            position_a[0],
                            objects[relative_items[0]].color,
                            objects[relative_items[0]].shape)

            elif position_a[1]:
                insturction_a = 'Add a {} {} on the {} of the {} {}'\
                    .format(objects[i].color,
                            objects[i].shape,
                            position_a[1],
                            objects[relative_items[0]].color,
                            objects[relative_items[0]].shape)
            else:
                raise Exception('Direction ambigous.')

            if position_b[0] and position_b[1]:
                insturction_b = ' and {} the {} {} on the {}'\
                    .format(position_b[0],
                            objects[relative_items[1]].color,
                            objects[relative_items[1]].shape,
                            position_b[1])

            elif position_b[0]:
                insturction_b = ' and {} the {} {}'\
                    .format(position_b[0],
                            objects[relative_items[1]].color,
                            objects[relative_items[1]].shape)

            elif position_b[1]:
                insturction_b = ' and on the {} of the {} {}'\
                    .format(position_b[1],
                            objects[relative_items[1]].color,
                            objects[relative_items[1]].shape)

            insturction = insturction_a + insturction_b

        if 'None' in insturction.split():
            raise Exception('An ambigous insturction is added. Aborting!')

        instructions.append(insturction)

    return instructions


def _get_relationships(scene_description):
    relationships = {}
    scene_relationships = scene_description['relationships']
    for i in range(len(scene_description['objects'])):
        directions = {}
        for j in range(0, i, 1):
            directions[j] = [None, None]
        for direction in scene_relationships:
            on_direction = \
                [it for it in scene_relationships[direction][i] if it < i]
            for e in on_direction:
                if direction in ['front', 'behind']:
                    if direction == 'front':
                        complement_direction = 'behind'
                    else:
                        complement_direction = 'in front of'
                    directions[e][0] = complement_direction
                if direction in ['left', 'right']:
                    if direction == 'right':
                        complement_direction = 'left'
                    else:
                        complement_direction = 'right'
                    directions[e][1] = complement_direction

        relationships[i] = directions

    return relationships


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--json_path',
                        type=str,
                        help='Scene description json files path.')
    parser.add_argument('--output_path',
                        type=str,
                        help='instructions path to save to')

    args = parser.parse_args()

    for json_file in tqdm(glob(args.json_path + '*.json')):
        instructions = generate_instructions(json_file)
        filename = os.path.basename(json_file)[:-5]
        with open(os.path.join(args.output_path,
                               '{}.txt'.format(filename)), 'w') as f:
            for inst in instructions:
                f.write(inst + '\n')
