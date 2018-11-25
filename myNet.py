import argparse
import os
import lan
import beyond

def get_args():
    """Create command-line arguments and return arguments provided by user"""

    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--lan", help="view LAN information", action='store_true')
    parser.add_argument("-b", "--beyond", help="view information about networks beyond the LAN", action='store_true')
    parser.add_argument("-a", "--approximate", help="determine approximate location of machine", action='store_true')
    parser.add_argument("-vis", "--visualize", help="visualize information from -l or -b", action='store_true')    
    parser.add_argument("-v", "--verbose", help="increase verbosity of output", action='store_true')
    
    return parser.parse_args()

def main():
    """Driver function - determines functionality based on command-line args"""

    args = get_args()

    if not args.lan and not args.beyond and not args.approximate:
        print("Must choose one or more of [-l, -b, -a]")
    else:
        if args.lan:
            lan.retrieve_LAN_info(args.verbose, args.visualize)

        if args.beyond:
            beyond.retrieve_beyond_info()

        if args.approximate:
            pass

    os._exit(1)
    

main()