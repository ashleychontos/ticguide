import argparse, os

import ticguide
from ticguide import pipeline


def main():

    parser = argparse.ArgumentParser(
                                     description='ticguide: quick + painless TESS observing information',
                                     prog='ticguide',
    )
    parser.add_argument('--version',
                        action='version',
                        version="%(prog)s {}".format(ticguide.__version__),
                        help="print version number and exit",
    )

    main_parser = argparse.ArgumentParser()
    main_parser.add_argument('--fast','-f', 
                             help='Check for fast (20-second) cadence data', 
                             dest='fast', 
                             default=False, 
                             action='store_true',
    )
    main_parser.add_argument('--file','--in','--input', 
                             metavar='path', 
                             help="input list of targets (currently works with txt or csv files)", 
                             dest='input', 
                             default='todo.csv',
    )
    main_parser.add_argument('--out','--output',
                             metavar='path', 
                             help='path to save the observed TESS table for all targets', 
                             dest='output', 
                             default='all_observed.csv',
    )
    main_parser.add_argument('--path', 
                             metavar='path', 
                             help='path to directory', 
                             type=str, 
                             dest='path', 
                             default=os.path.join(os.path.abspath(os.getcwd()),''),
    )
    main_parser.add_argument('--progress','-p', 
                             help='disable the progress bar', 
                             dest='progress', 
                             default=True, 
                             action='store_false',
    )
    main_parser.add_argument('--save', 
                             help='disable the saving of output files', 
                             dest='save', 
                             default=True, 
                             action='store_false',
    )
    main_parser.add_argument('--short','-s', 
                             help='Check for short (2-minute) cadence data', 
                             dest='short', 
                             default=False, 
                             action='store_true',
    )
    main_parser.add_argument('--star','--stars','--tic', 
                             metavar='star', 
                             help='TESS Input Catalog (TIC) IDs', 
                             type=int, 
                             dest='stars', 
                             nargs='*', 
                             default=None,
    )
    main_parser.add_argument('--verbose','-v', 
                             help='Disable the verbose output', 
                             dest='verbose', 
                             default=True, 
                             action='store_false',
    )
    main_parser.set_defaults(func=pipeline.main)

    args = main_parser.parse_args()
    args.func(args)



if __name__ == '__main__':

    main()
