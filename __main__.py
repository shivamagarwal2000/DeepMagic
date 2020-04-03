import sys
import json


def main():
    with open(sys.argv[1]) as file:
        data = json.load(file)


    # TODO: find and print winning action sequence



if __name__ == '__main__':
    main()
