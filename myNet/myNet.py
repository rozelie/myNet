#!/usr/bin/env python
"""Entry file for project - parses CLI arguments
   and executes appropriate functionalites accordingly. 
"""

import argparse
import os
import lan
import beyond
import approximate

__author__ = "Ryan Ozelie"
__copyright__ = "Copyright 2019, Ryan Ozelie"
__credits__ = ["Ryan Ozelie"]
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Ryan Ozelie"
__email__ = "rozelie@iwu.edu"
__status__ = "Development"

def get_args():
    """Create command-line arguments and return arguments provided by user"""

    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--lan", 
                        help="view LAN information", 
                        action='store_true')

    parser.add_argument("-b", "--beyond",
                        help="view information about networks beyond the LAN",
                        action='store_true')
                        
    parser.add_argument("-a", "--approximate",
                        help="determine approximate location of machine", 
                        action='store_true')
    
    return parser.parse_args()

def main():
    """Driver function - determines functionality based on command-line args"""

    args = get_args()

    if not args.lan and not args.beyond and not args.approximate:
        print("Must choose one or more of [-l, -b, -a]")
    else:
        if args.lan:
            lan.retrieve_LAN_info()

        if args.beyond:
            beyond.run_beyond_functions()

        if args.approximate:
            approximate.approximate_location()

    os._exit(1)
    

main()