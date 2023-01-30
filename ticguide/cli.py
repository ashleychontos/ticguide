import argparse, os

import ticguide
from ticguide import pipeline
from ticguide import __version__, PATHDIR



def main():

    parser = argparse.ArgumentParser(
                                     description='ticguide: quick + painless TESS observing information',
                                     prog='ticguide',
    )
    parser.add_argument('--version',
                        action='version',
                        version="%(prog)s {}".format(__version__),
                        help="print version number and exit",
    )

    main_parser = parser.add_argument_group()
    main_parser.add_argument('--download','-d', 
                             help='Download data for targets of interest', 
                             dest='download', 
                             default=False, 
                             action='store_true',
    )
    main_parser.add_argument('--fast','-f', 
                             help='Do not search for fast (20-second) cadence data', 
                             dest='fast', 
                             default=True, 
                             action='store_false',
    )
    main_parser.add_argument('--fileinput','--input',
                             metavar='str', 
                             help="input list of targets (currently works with txt or csv files)", 
                             dest='fileinput', 
                             default='todo.csv',
    )
    main_parser.add_argument('--fileselect','--select',
                             metavar='str', 
                             help='filename for sub-selected sample of observed TESS targets', 
                             dest='fileselect', 
                             default='selected_tics.csv',
    )
    main_parser.add_argument('--fileall','--all',
                             metavar='str', 
                             help='path to total sample of observed TESS targets', 
                             dest='fileall', 
                             default='all_tics.csv',
    )
    main_parser.add_argument('--ll','--linelength',
                             metavar='int',
                             help="line length for CLI output (default=50)",
                             type=int,
                             dest='linelength',
                             default=50,
    )
    main_parser.add_argument('--path', 
                             metavar='str', 
                             help='path to directory', 
                             type=str, 
                             dest='path', 
                             default=PATHDIR,
    )
    main_parser.add_argument('--progress','-p', 
                             help='disable the progress bar', 
                             dest='progress', 
                             default=True, 
                             action='store_false',
    )
    main_parser.add_argument('--save', 
                             help='Disable the auto-saving of relevant tables, files and/or scripts for selected targets', 
                             dest='save', 
                             default=True, 
                             action='store_false',
    )
    main_parser.add_argument('--short','-s', 
                             help='Do not check for short (2-minute) cadence data', 
                             dest='short', 
                             default=True, 
                             action='store_false',
    )
    main_parser.add_argument('--star','--stars','--tic', 
                             metavar='int', 
                             help='TESS Input Catalog (TIC) IDs', 
                             type=int, 
                             dest='stars', 
                             nargs='*', 
                             default=[],
    )
    main_parser.add_argument('--totals','-t', 
                             help='Save cadence totals (by TIC ID)', 
                             dest='totals', 
                             default=True,
                             action='store_false',
    )
    main_parser.add_argument('--verbose','-v', 
                             help='Disable the verbose output', 
                             dest='verbose', 
                             default=True, 
                             action='store_false',
    )
    parser.set_defaults(func=pipeline.main)

    args = parser.parse_args()
    args.func(args)



if __name__ == '__main__':

    main()
