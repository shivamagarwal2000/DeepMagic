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
# Warning - some moves might be invalid so return some flag value like None
def move(state, x, y, dir, no_steps):


# Boom function
# Deletes the exploded pieces from board_dict
# takes a state and the location of the blast and returns the updated state
def boom(state, x, y):


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
    for nxy in state["white"]:
        x = nxy[1]
        y = nxy[2]
        for mpq in state["black"]:
            p = mpq[1]
            q = mpq[2]
            total_dis += (abs(x - p) + abs(y - q))

    return total_dis



class Node():
    """A node class for A* Pathfinding"""

    def __init__(self, parent=None, state=None):
        self.parent = parent
        self.state = state

        self.g = 0
        self.h = 0
        self.f = 0

    def __eq__(self, other):
        return self.state == other.state




def a_star_search(state):

    # initialise the starting node
    start_node = Node(None, state)
    start_node.g = 0
    start_node.h = heuristic(state)
    start_node.f = start_node.h

    # Initialize both open and closed list
    open_list = []
    closed_list = []

    # Add the start node
    open_list.append(start_node)

    while len(open_list) > 0:
        # Get the current node
        current_node = open_list[0]
        current_index = 0

        for index, item in enumerate(open_list):
            if item.f < current_node.f:
                current_node = item
                current_index = index

        # Pop current off open list, add to closed list
        open_list.pop(current_index)
        closed_list.append(current_node)

        # if the current node has no black piece it is a goal node hence return
        for nxy in current_node.state["black"]:
            if len(nxy) == 0:
                path = []
                current = current_node
                while current is not None:
                    path.append(current.state)
                    current = current.parent
                return path[::-1]  # Return reversed path

            else:
                break

        # Generate children
        children = []
        



if __name__ == '__main__':
    main()
