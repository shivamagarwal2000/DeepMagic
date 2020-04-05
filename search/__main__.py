import sys
import json
import search.util as util


def main():
    with open(sys.argv[1]) as file:
        data = json.load(file)
        board_dict = {}
        for nxy in data["white"]:
            n = nxy[0]
            x = nxy[1]
            y = nxy[2]
            board_dict[(x, y)] = "{} W".format(n)

        for nxy in data["black"]:
            n = nxy[0]
            x = nxy[1]
            y = nxy[2]
            board_dict[(x, y)] = "{} B".format(n)

    file.close()
    util.print_board(board_dict, "", False, True)

    # TODO: find and print winning action sequence

    # Store white and black pieces in the form of dictionary

    # If only one white piece then 

    # If only one black piece then just have destination tile be any surrounding tile closest to white piece

    # If more than one black piece then
    # Iterate through black pieces, checking surrounding tiles of each
    # If none then check tiles in 5x5 box around
    # If got another black piece then place white piece in middle of the two
    # Plan boom at that tile
    # If will remove all black pieces then make white piece destination be that tile
    # Find shortest path from white piece to that tile

    # If more than one piece then
    # Do the same for the above where more than one black piece
    # If nothing in the 5x5 box, then prioritise this and just move ONE white piece there (preferably white piece closest to black piece)

    # White piece is trapped if all paths are blocked
    # If trapped try to make stack with pieces trapped and try to find path again
    # Once not trapped, destack and only move one piece to boom


# Store function

# For every piece in json file, we append into empty board_dict
# board_dict[(x,y)] = "n c" where n is number of pieces (maybe in stack) and c is colour (B or W)

# print to check if stored correctly


# takes the state and coordinate of the moving tile, direction of movement, and the no of steps
# return the state after update
# also keep in mind the stacking part
# Warning - some moves might be invalid so return some flag value like None
def move(state, x, y, dir, no_steps):
    return state


# Boom function
# Deletes the exploded pieces from board_dict
# takes a state and the location of the blast and returns the updated state
def boom(state, x, y):
    return state


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
    white_freq = 0
    for nxy in state["white"]:
        x = nxy[1]
        y = nxy[2]
        white_freq = len(nxy)
        for mpq in state["black"]:
            p = mpq[1]
            q = mpq[2]
            total_dis += (abs(x - p) + abs(y - q))

    return total_dis * white_freq


# a node class that holds the current state, parent state, f, g, h values
class Node():
    """A node class for A* Pathfinding"""

    def __init__(self, parent=None, state=None):
        self.parent = parent
        self.state = state

        self.g = 0
        self.h = 0
        self.f = 0

    # equality is defined if the current state is the same for any 2 nodes
    def __eq__(self, other):
        return self.state == other.state


def a_star_search(state):
    # initialise the starting node
    start_node = Node(None, state)
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
        for nxy in current_node.state["black"]:
            if len(nxy) == 0:
                path = []
                current = current_node
                while current is not None:
                    path.append(current.state)
                    current = current.parent
                return path[::-1]  # Return reversed path of states

            else:
                break

        # Generate children, if goal not reached and further traversal is needed
        children = []

        # Generating children by moving
        dirs = ['N', 'S', 'E', 'W']
        for nxy in current_node.state["white"]:
            n = nxy[0]
            x = nxy[1]
            y = nxy[2]

            # can move 1 to n steps in a stack of n pieces so running the loop accordingly
            for i in list(range(1, n + 1)):
                for s in dirs:
                    temp = move(current_node.state, x, y, s, i)
                    # if the move was invalid, no need to add it and go to next cycle
                    if temp is None:
                        continue
                    new_node = Node(current_node, temp)
                    children.append(new_node)

        # Generating children by blasting
        for nxy in current_node.state["white"]:
            x = nxy[1]
            y = nxy[2]
            temp = boom(current_node.state, x, y)
            new_node = Node(current_node, temp)
            children.append(new_node)

        # Loop through children
        for child in children:
            flag = 0
            # Child is on the closed list
            for closed_child in closed_list:
                if child == closed_child:
                    flag = 1
                    break
                else:
                    # Create the f, g, and h values
                    child.g = current_node.g + 1
                    child.h = heuristic(child.state)
                    child.f = child.g + child.h

            if flag == 1:
                continue

            # Child is already in the open list
            for open_node in open_list:
                # check if the new path to children is worst or equal
                # than one already in the open_list (by measuring g)
                if child == open_node and child.g >= open_node.g:
                    break
                else:
                    # Add the child to the open list
                    open_list.append(child)


if __name__ == '__main__':
    main()
