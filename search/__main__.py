import sys
import json
import copy
import search.util as util
import time

start_time = time.time()
def main():
    with open(sys.argv[1]) as file:
        data = json.load(file)

    file.close()
    expendibots(data)
    print("--- %s seconds ---" % (time.time() - start_time))

def expendibots(data):
    # Use A* algorithm to find optimal path
    # Have it return a path (list of actions either Move or Boom)
    # Print the actions
    path = a_star_search(data)

    for action in path:
        if action is not None:
            if action.name == "Move":
                util.print_move(action.n, action.x_a, action.y_a, action.x_b, action.y_b)

            else:
                util.print_boom(action.x, action.y)


# Move function
# takes the state and coordinate of the moving tile, direction of movement, and the no of steps
# return the state after update
# also keep in mind the stacking part
# Warning - some moves might be invalid so return some flag value like None

def move(state, n, x, y, dir, no_steps):
    # Check if move will still be on the board
    new_state = copy.deepcopy(state)
    # print(new_state)
    new_x = x
    new_y = y

    if dir == 'N':
        new_y += no_steps

    elif dir == 'S':
        new_y -= no_steps

    elif dir == 'E':
        new_x += no_steps

    else:
        new_x -= no_steps

    # Invalid move if there are already black pieces on the destination tile or if the move goes past the borders
    dest_tile = find_tile(new_state, new_x, new_y)
    found_black = dest_tile and dest_tile[1] == "black"

    not_in_range = not (new_x in range(8) and new_y in range(8))
    if not_in_range or found_black:
        return None, None, None

    # Remove the n pieces from the original tile
    source_tile = find_tile(new_state, x, y)
    old_n = source_tile[0][0]
    new_state["white"].remove([old_n, x, y])

    # If moving only part of a stack
    if old_n > n:
        old_n -= n
        new_state["white"].append([old_n, x, y])

    # Place n pieces at destination
    new_n = n

    # If there are already white pieces on the destination tile then stack
    if dest_tile:
        dest_n = dest_tile[0][0]
        new_state["white"].remove([dest_n, new_x, new_y])
        new_n += dest_n

    new_state["white"].append([new_n, new_x, new_y])
    return new_state, new_x, new_y


# Boom function
# Deletes the exploded pieces from board_dict
# takes a state and the location of the blast and returns the updated state
def boom(state, x, y):
    new_state = copy.deepcopy(state)

    # Remove all pieces at location
    tile = []
    found = find_tile(new_state, x, y)
    if found:
        new_state[found[1]].remove(found[0])

    # Check for surrounding tiles if any other pieces caught in explosion
    # Added the feature of removing the surrounding tiles as well
    for surrounding_x in range(x - 1, x + 2):
        for surrounding_y in range(y - 1, y + 2):

            if find_tile(new_state, surrounding_x, surrounding_y):

                new_state = boom(new_state, surrounding_x, surrounding_y)

    return new_state


def find_tile(state, x, y):
    for tile in state["white"]:
        if tile[1] == x and tile[2] == y:
            return tile, "white"

    for tile in state["black"]:
        if tile[1] == x and tile[2] == y:
            return tile, "black"

    return False


# search the optimal tiles/tile where the white pieces/piece should move to
# modelling the problem - States - white and black pieces along with their location
# data structure to store states - dictionary in the format of 'data' as read from json
# operators - move a white "location" to a valid location and blast the current "location"
# goal - 0 black pieces in the state
# path cost - single operation
# Algorithm to reach the goal efficiently - A*


# heuristic - manhattan distance - sum of all distances from all white locations to black locations
# state is a dictionary of white/black as keys and list of coordinates as values
def heuristic(state):
    total_dis = 0
    # white_freq = len(state["white"])
    # black_freq = len(state["black"])
    for nxy in state["white"]:
        x = nxy[1]
        y = nxy[2]
        for mpq in state["black"]:
            p = mpq[1]
            q = mpq[2]
            total_dis += (abs(x - p) + abs(y - q))

    # if black_freq == 0:
    #     return 0
    # if white_freq == 0:
    #     return 100000

    return total_dis


# class holds all the variables needed to define a unique move
class Move():

    def __init__(self, n, x_a, y_a, x_b, y_b):
        self.n = n
        self.x_a = x_a
        self.x_b = x_b
        self.y_a = y_a
        self.y_b = y_b
        self.name = "Move"


# class holds all the variables needed to define a unique boom
class Boom():

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.name = "Boom"


# a node class that holds the current state, parent state, f, g, h values
# it also stores the action which tells us how the state was achieved from the last one
class Node():
    """A node class for A* Pathfinding"""

    def __init__(self, parent=None, state=None, action=None):
        self.parent = parent
        self.state = state
        self.action = action

        self.g = 0
        self.h = 0
        self.f = 0

    # equality is defined if the current state is the same for any 2 nodes
    def __eq__(self, other):
        return self.state == other.state


def a_star_search(state):
    # initialise the starting node
    start_node = Node(None, state, None)
    start_node.g = 0
    start_node.h = heuristic(state)
    start_node.f = start_node.h

    # Initialize both open and closed list
    # open list has all the unvisited nodes and the closed list has the visited ones
    open_list = []
    closed_list = []

    # Add the start node
    open_list.append(start_node)

    # loop till the end
    while len(open_list) > 0:
        # Get the current node
        # print(len(open_list))
        current_node = open_list[0]
        current_index = 0

        # check if some other node might be optimal to traverse based on the evaluation function
        for index, item in enumerate(open_list):
            if item.f < current_node.f:
                current_node = item
                current_index = index

        # Pop current off open list, add to closed list
        open_list.pop(current_index)
        closed_list.append(current_node)

        # if the current node has no black piece, it is a goal node hence return
        # print(len(current_node.state["black"]))

        if len(current_node.state["black"]) == 0:

            path = []
            current = current_node
            while current is not None:
                path.append(current.action)
                current = current.parent
            return path[::-1]  # Return reversed path of actions either move or boom

        # Generate children, if goal not reached and further traversal is needed
        children = []

        # Generating children by moving
        dirs = ['N', 'S', 'E', 'W']
        for nxy in current_node.state["white"]:
            n = nxy[0]
            x = nxy[1]
            y = nxy[2]
            for i in range(1, n + 1):
                for pieces in range(1, n + 1):
                    for s in dirs:
                        (temp_state, new_x, new_y) = move(current_node.state, pieces, x, y, s, i)
                        if temp_state is None:
                            continue

                        temp_act = Move(pieces, x, y, new_x, new_y)
                        new_node = Node(current_node, temp_state, temp_act)
                        # print(new_node.action.name)
                        children.append(new_node)

        # Generating children by blasting
        for nxy in current_node.state["white"]:
            x = nxy[1]
            y = nxy[2]
            temp = boom(current_node.state, x, y)
            temp_act = Boom(x, y)
            new_node = Node(current_node, temp, temp_act)
            children.append(new_node)

        # Loop through children
        for child in children:
            # Child is on the closed list
            flag_1 = 0
            for closed_child in closed_list:
                if child == closed_child:
                    # print("Visited child")
                    flag_1 = 1
                    break

            if flag_1 == 1:
                continue
            else:
                # Create the f, g, and h values
                child.g = current_node.g + 1
                child.h = heuristic(child.state)
                child.f = child.g + child.h
                # print(child.f)

            # Child is already in the open list
            flag2 = 0
            for open_node in open_list:
                # check if the new path to children is worst or equal
                # than one already in the open_list (by measuring g)
                if child == open_node and child.g >= open_node.g:
                    flag2 = 1
                    break

            if flag2 == 1:
                continue
            else:
                # Add the child to the open list
                open_list.append(child)



if __name__ == '__main__':
    main()
