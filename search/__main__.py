import sys
import json
import search.util as util


def main():
    with open(sys.argv[1]) as file:
        data = json.load(file)

        # Store white and black pieces in the form of dictionary
        state = {}
        state = store(data)

    file.close()

    # Use A* algorithm to find optimal path
    # Have it return a path (list of tuple with (action_type, n, source_x, source_y, dest_x, dest_y))

    path = []
    path = a_star_search(data) 

    # Print the actions

    for action in path:
        if action[1] == "move":
            print_move(action[2],action[3],action[4],action[5],action[6])

        else: 
            print_boom(action[2],action[3],action[4])
            
    util.print_board(state)

# Store function
def store(data):
    
    # For every piece in json file, we append into empty board_dict
    # board_dict[(x,y)] = "n c" where n is number of pieces (maybe in stack) and c is colour (B or W) 
    state = {}

    for nxy in data["white"]:
        n = nxy[0]
        x = nxy[1]
        y = nxy[2]
        state[(x,y)] = "{} W".format(n)

    for nxy in data["black"]:
        n = nxy[0]
        x = nxy[1]
        y = nxy[2]
        state[(x,y)] = "{} B".format(n)

    return state
    


# Move function
# takes the state and coordinate of the moving tile, direction of movement, and the no of steps
# return the state after update
# also keep in mind the stacking part
# Warning - some moves might be invalid so return some flag value like None

def move(state, n, x, y, dir, no_steps):

    # Check if move will still be on the board
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

    if new_x not in range(8) and new_y not in range(8):
        return None

    # Remove the n pieces from the original tile 
    old_n = int(state[(x,y)][0])

    # If moving less than a full stack
    if old_n > n:
        old_n -= n
        state[(x,y)] = "{} W".format(old_n)

    # If moving full stack
    else:
        del state[(x,y)]

    # Place n pieces at destination 
    new_n = n

    # If there are already pieces on the destination tile
    if (new_x, new_y) in state:

        # If piece at destination is white then just make/add to stack
        c = state[(new_x, new_y)][2]

        if c == "W":
            new_n += int(state[(new_x, new_y)][0])

        # If piece at destination is black then is an invalid move
        else:
            return None

    # Store and return the new state with the moved tiles
    state[(new_x, new_y)] = "{} W".format(new_n)
    return state

# Boom function
# Deletes the exploded pieces from board_dict
# takes a state and the location of the blast and returns the updated state
def boom(state, x, y):
    
    # Remove all pieces at location
    if (x,y) in state:
        del state[(x,y)]

    # Check for surrounding tiles if any other pieces caught in explosion
    for surrounding_x in range(x-1, x+2):
        for surrounding_y in range(y-1,y+2):
            if (surrounding_x, surrounding_y) in state:
                state = boom(state, surrounding_x,surrounding_y)
    
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

        # Generating children by moving
        dirs = ['N', 'S', 'E', 'W']
        for nxy in current_node.state["white"]:
            n = nxy[0]
            x = nxy[1]
            y = nxy[2]
            for i in list(range(1, n+1)):
                for pieces in list(range(1,n+1)):
                    for s in dirs:
                        temp = move(current_node.state, pieces, x, y, s, i)
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
