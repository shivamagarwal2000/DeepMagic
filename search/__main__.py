# Assignment 1 COMP30024: Artificial Intelligence Semester 1 2020

# Group Name: DeepMagic
# 
# Student 1 Name: Chan Jie Ho
# Student 1 Number: 961948
#
# Student 2 Name: Shivam Agarwal
# Student 2 Number: 951424

import sys
import json
import copy
import search.util as util

def main():

    # Load the data
    with open(sys.argv[1]) as file:
        data = json.load(file)
    file.close()
    expendibots(data)

# ============================================================================ #
# EXPENDIBOTS FUNCTION #
# -------------------- #
#
# Expendibots game function that runs the A* search algorithm and then prints 
# out the optimal path.
#
# MODELLING THE PROBLEM:
#
# States - Location of all the white and black pieces remaining on the board stored as a dictionary in the sane format as the data from the json file
#
# Actions - Either moving a white piece(s) to a valid location or booming the
# white piece(s)
#
# Goal - 0 black pieces on the board
#
# Path cost - A single action (move or boom)
#
# Algorithm used to reach the goal efficiently - A*

def expendibots(data):
    
    # Get the path
    path = a_star_search(data)

    # Print the path using right functions depending on aciton type
    for action in path:
        if action is not None:
            if action.name == "Move":
                util.print_move(action.n, action.x_a, action.y_a, action.x_b, action.y_b)

            else:
                util.print_boom(action.x, action.y)

# ---------------------------------------------------------------------------- #
# MOVE FUNCTION #
# ------------- #
#
# Move function that (validly) moves the pieces on the board.
# 
# It takes the initial state, the coordinates of the source tile, direction of 
# movement, and the number of steps as input and returns a new updated state 
# and the coordinates of the destination tile if the move is valid or returns 
# three Nones (to create a None node) if not.

def move(state, n, x, y, direction, steps):

    # Create a deep copy of the original state so as to not alter it 
    new_state = copy.deepcopy(state)
    
    # Find the coordinates of the destination tile
    dest_x = x
    dest_y = y

    if direction == 'N':
        dest_y += steps

    elif direction == 'S':
        dest_y -= steps

    elif direction == 'E':
        dest_x += steps

    else:
        dest_x -= steps

    # Invalid move if there are already black pieces on the destination tile or 
    # if the move goes past the borders so return None, None, None
    dest_tile = find_tile(new_state, dest_x, dest_y)

    found_black = dest_tile and dest_tile[1] == "black"
    not_in_range = not (dest_x in range(8) and dest_y in range(8))

    if not_in_range or found_black:
        return None, None, None

    # Remove the n pieces from the original tile
    source_tile = find_tile(new_state, x, y)
    original_n = source_tile[0][0]
    new_state["white"].remove([original_n, x, y])

    # If moving only part of a stack
    if original_n > n:
        original_n -= n
        new_state["white"].append([original_n, x, y])

    # Place n pieces at destination
    # If there are already white pieces on the destination tile then stack
    if dest_tile:
        dest_n = dest_tile[0][0]
        new_state["white"].remove([dest_n, dest_x, dest_y])
        n += dest_n

    new_state["white"].append([n, dest_x, dest_y])
    return new_state, dest_x, dest_y

# ---------------------------------------------------------------------------- #
# BOOM FUNCTION #
# ------------- #
#
# Boom function that removes all the pieces caught in the explosion(s).
# 
# It takes the state and the coordinates of the piece(s) to boom as input and 
# returns the new updated state.

def boom(state, x, y):

    # Create a deep copy of the original state so as to not alter it
    new_state = copy.deepcopy(state)

    # Remove all pieces at location
    tile = find_tile(new_state, x, y)    
    new_state[tile[1]].remove(tile[0])

    # Check surrounding tiles if there any other pieces are caught in explosion
    for surrounding_x in range(x - 1, x + 2):
        for surrounding_y in range(y - 1, y + 2):
            if find_tile(new_state, surrounding_x, surrounding_y):
                new_state = boom(new_state, surrounding_x, surrounding_y)

    return new_state

# ---------------------------------------------------------------------------- #
# FIND_TILE FUNCTION #
# ------------------ #
#
# Helper function checks if a tile is occupied by a piece.
# 
# It takes the state and the coordinates of the tile to check as input and 
# returns tile and colour of the piece(s) occupying it if it is occupied or 
# False if it isn't occupied.

def find_tile(state, x, y):

    # Check for white pieces
    for tile in state["white"]:
        if tile[1] == x and tile[2] == y:
            return tile, "white"

    # Check for black pieces
    for tile in state["black"]:
        if tile[1] == x and tile[2] == y:
            return tile, "black"

    return False

# ---------------------------------------------------------------------------- #
# HEURISTIC FUNCTION #
# ------------------ #
#
# Helper function that uses the Manhattan distance (since we can only move in 
# the four cardinal directions) to estimate the total number of moves that we 
# must take to cover each of the black piece remaining.
# 
# It takes the current state to calculate the heuristic as input and returns 
# the sum of all the distances from all the white pieces to the black pieces.

def heuristic(state):

    total_distance = 0

    checking = copy.deepcopy(state)

    # Iterate through all the white pieces left on the board
    for white in checking["white"]:
        n = white[0]
        x = white[1]
        y = white[2]

        # If there is already a black piece in the surrounding, then remove it 
        checking = remove_black_cluster(checking, x, y)

        for black in checking["black"]:
            black_x = black[1]
            black_y = black[2]
            
            # Add the number of moves needed to reach the black pieces

            # Minus 3 to account for the fact that the minimum distance is at 
            # least 1 since we cannot place a white piece on a tile with a 
            # black piece and also that we do not need to be directly beside a 
            # black piece when booming to remove it

            # Minus n to prioritise being in stacks
            total_distance += (abs(x - black_x) + abs(y - black_y)) - 2

    return total_distance

# ---------------------------------------------------------------------------- #
# REMOVE_BLACK_CLUSTER FUNCTION #
# ----------------------------- #
#
# Helper function that removes all the black pieces that are already next to a 
# white piece - similar to boom
# 
# It takes the state and the coordinates of the piece(s) to boom as input and 
# returns the new updated state.

def remove_black_cluster(state, x, y):

    # Create a deep copy of the original state so as to not alter it
    new_state = copy.deepcopy(state)

    # Remove the piece if it is a black piece
    tile = find_tile(new_state, x, y)
    if tile[1] == "black":    
        new_state[tile[1]].remove(tile[0])

    # Check surrounding tiles if there any other black pieces connected
    for surrounding_x in range(x - 1, x + 2):
        for surrounding_y in range(y - 1, y + 2):
            tile = find_tile(new_state, surrounding_x, surrounding_y)
            if tile and tile[1] == "black":
                new_state = remove_black_cluster(new_state, surrounding_x, surrounding_y)

    return new_state


# ---------------------------------------------------------------------------- #
# MOVE CLASS #
# ---------- #
#
# Move action class that holds all the variables needed to define a unique move.
# 
# It requires the number of pieces to move and the coordinates of the source 
# and destination tiles.

class Move():

    def __init__(self, n, x_a, y_a, x_b, y_b):
        self.n = n
        self.x_a = x_a
        self.x_b = x_b
        self.y_a = y_a
        self.y_b = y_b
        self.name = "Move"

# ---------------------------------------------------------------------------- #
# BOOM CLASS #
# ---------- #
#
# Boom action class that holds all the variables needed to define a unique boom.
# 
# It requires the coordinates of the tile to boom.

class Boom():

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.name = "Boom"

# ---------------------------------------------------------------------------- #
# NODE CLASS #
# ---------- #
#
# Node class that holds the current state of the game, the parent (previous) 
# state, f, g, h values and also stores the action which tells us how the state 
# was changed from the parent state. 
#
# f value - Total cost of the node
# g value - Number of actions made from the initial state
# h value - Heuristic value (explained in the heuristic function)

class Node():

    def __init__(self, parent=None, state=None, action=None):
        self.parent = parent
        self.state = state
        self.action = action

        self.f = 0 
        self.g = 0
        self.h = 0
        
    # Equality is defined if the current state is the same for any 2 nodes
    def __eq__(self, other):
        return self.state == other.state

# ---------------------------------------------------------------------------- #
# A_STAR_SEARCH FUNCTION #
# ---------------------- #
#
# A* search algorithm function that searches for the optimal list of actions 
# (move or boom) to take to remove all the black pieces from the board
#
# It takes in the initial state that the game starts with and returns the path 
# which is a list of Move and Boom class types
#
# Code is modelled off the COMP30024 lecture notes and the following link. It 
# has been altered to fit the requirements of our problem. 
# https://medium.com/@nicholas.w.swift/easy-a-star-pathfinding-7e6689c7f7b2

def a_star_search(state):

    # Initialise the starting node with the initial state
    start_node = Node(None, state, None)
    start_node.g = 0
    start_node.h = heuristic(state)
    start_node.f = start_node.h

    # Initialize the lists of unvisited and visited nodes
    
    unvisited_nodes = []
    visited_nodes = []

    # Add the start node
    unvisited_nodes.append(start_node)

    # Loop until there are no more nodes that need visiting or if we reach our 
    # goal
    while len(unvisited_nodes) > 0:

        # Get the current node
        current_node = unvisited_nodes[0]
        current_index = 0

        # Check if some other node might be optimal to traverse based on the 
        # evaluation function
        for index, item in enumerate(unvisited_nodes):
            if item.f < current_node.f:
                current_node = item
                current_index = index

        # Move the current node from unvisited_nodes to visited_nodes
        unvisited_nodes.pop(current_index)
        visited_nodes.append(current_node)

        # If the current node has no black piece, it is a goal node
        if len(current_node.state["black"]) == 0:

            # Iterate through the states and its parent to get the path taken 
            # to reach the goal
            path = []
            current = current_node

            while current is not None:
                path.append(current.action)
                current = current.parent
            
            # Path from goal to parents is in reverse, so return reversed 
            return path[::-1]  


        # Going beyond this means that it is not the end goal

        # Create list of possible children node - possible future states using 
        # the possible movements that we can make
        children = []

        # Generating potential children by moving
        direction = ['N', 'S', 'E', 'W']

        for nxy in current_node.state["white"]:
            n = nxy[0]
            x = nxy[1]
            y = nxy[2]

            # Allow for movement of up to n steps for the n pieces in the stack
            for pieces in range(1, n + 1):

                # Allow for movement of up to n pieces from the stack
                for steps in range(1, n + 1):

                    # Allow for any of the 4 directions
                    for cardinal in direction:

                        # Try the movement 
                        (temp_state, new_x, new_y) = move(current_node.state, pieces, x, y, cardinal, steps)

                        # Invalid move
                        if temp_state is None:
                            continue

                        # Valid move so append it as a potential child node
                        temp_action = Move(pieces, x, y, new_x, new_y)
                        new_node = Node(current_node, temp_state, temp_action)
                        children.append(new_node)

        # Generating potential children by booming
        for nxy in current_node.state["white"]:
            x = nxy[1]
            y = nxy[2]

            # Boom the white piece(s) and append it as a potential child node
            temp = boom(current_node.state, x, y)
            temp_action = Boom(x, y)
            new_node = Node(current_node, temp, temp_action)
            children.append(new_node)

        # Loop through potential children nodes
        for child in children:

            # Check if child was already visited
            visited = False

            for visited_child in visited_nodes:
                if child == visited_child:
                    visited = True
                    break

            if visited:
                continue

            else:
                # Create the f, g, and h values
                child.g = current_node.g + 1
                child.h = heuristic(child.state)
                child.f = child.g + child.h

            # Check if child is already queued to be checked in unvisited_nodes 
            # and if it is, check if the current node is better than the one 
            # queued
            current_worse = False
            better_child = None
            
            for unvisited_child in unvisited_nodes:  

                if child == unvisited_child:
                    
                    if child.g >= unvisited_child.g or child.h >= unvisited_child.h:
                        current_worse = True
                        break

                    else:
                        better_child = unvisited_child
                
            # If the current child is better than the one queued, remove the 
            # one that is queued
            if better_child != None:
                unvisited_nodes.remove(better_child)

            # Else continue on to the next child
            elif current_worse:
                continue
            
            # Add the child to the list of nodes to traverse
            unvisited_nodes.append(child)

# ---------------------------------------------------------------------------- #

if __name__ == '__main__':
    main()

# ============================================================================ #

# :)