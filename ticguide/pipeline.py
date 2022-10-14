import numpy as np
import pandas as pd
from tqdm import tqdm
from bs4 import BeautifulSoup
import argparse, subprocess, requests, glob, os, re


def main(args, url='http://archive.stsci.edu/tess/bulk_downloads/bulk_downloads_ffi-tp-lc-dv.html',
         cadences=['fast','short']):
    """
    Main function call to run the `ticguide` search

    Parameters
    ----------
    args : argparse.Namespace
        the command line arguments
    args.url : str
        link to MAST bulk downloads page -> this should NOT need to be changed for any reason
    args.cadences : List(str)
        cadence for observations of interest, default~['short','fast']
    args.mast : Dict(str)
        dictionary
    args.all_tic : List(int)
        full list of observed TIC ids in all provided cadences (become indices for final table)

    """
    args.cadences, args.url, args.mast, args.all_tics = [], url, {}, []
    if args.short:
        args.cadences.append('short')
    if args.fast:
        args.cadences.append('fast')
    # Check that the input is correct first
    if check_input(args):
        # Retrieve massive table of observed TESS targets
        df_all = update_observations(args)
        # Filter based on the TIC (or TICs) provided
        get_info(df_all, args)


def check_input(args, pathall='all_tics.csv', pathsub='selected_tics.csv'):
    """
    Checks input arguments and returns `True` if the pipeline has enough information to run.
    If an input file is provided, this function will also load in the list of targets and save
    to args.stars

    Parameters
    ----------
    args : argparse.Namespace
        command-line arguments
    args.pathall : str
        path to massive full table with all observing information
    args.pathsub : str
        path to targets with updated observing information
    args.stars : List(int)
        list of targets of interest

    Returns
    -------
    bool

    """
    if not os.path.isfile(args.input):
        args.input = os.path.join(args.path,args.input)
    if not os.path.isfile(args.pathall):
        args.pathall = os.path.join(args.path,args.pathall)
    args.pathsub = os.path.join(args.path,'selected_tics.csv')
    # If no targets are provided via CLI, check for todo file
    if args.stars is None:
        if os.path.exists(args.input):
            if args.input.split('/')[-1].split('.')[-1] == 'csv' or args.input.split('/')[-1].split('.')[-1] == 'txt':
                with open (args.input, "r") as f:
                    args.stars = [int(line.strip()) for line in f.readlines() if line[0].isnumeric()]
            else:
                print('\nERROR: did not understand input file type. Please try again.\n')
        else:
            print('\nERROR: no targets were provided')
            print('*** please either provide entries via command line \n    or an input csv file with a list of TICs (via todo.csv) ***\n')
            return False
    if not args.cadences:
        print("\nERROR: no desired cadences were provided as input.\nPlease use the flags '-f' for fast (i.e. 20-second) and '-s' for short (i.e. 2-minute).\nIf you'd like both you can simply type '-sf'.\n")
    return True


def update_observations(args):
    """
    Before crossmatching the observed TESS target list with personal targets of interest, 
    this function checks that the observed target list exists and is up-to-date (but there is
    still work that needs to be done for this). The goal is to update this so that it will:
    1) create and save the observed TESS targets if the file does not already exist,
    2) otherwise it will check MAST for the current TESS sector and check if the column exists, and
    3) add the new observing sector information if not already available. (TODO!!)

    Parameters
    ----------
    args : argparse.Namespace
        command-line arguments

    Returns
    -------
    df : pandas.DataFrame
        pandas dataframe containing all targets observed in TESS short- and fast-cadence by 'tic' id

    """
    # get available observing info from MAST
    args = retrieve_observed(args)
    # get any existing local information to avoid duplicating efforts
    args = retrieve_existing(args)
    # get new sector information
    args = get_new_sectors(args)
    # merge with existing information
    df = combine_sectors(args)
    return df


def make_soup(args):
    """
    Makes a delicious MAST soup, hot with all of the most important information.

    """
    # Start request session to pull information from MAST
    s = requests.session()
    r = s.get(args.url, headers=dict(Referer=args.url))
    soup = BeautifulSoup(r.content, 'html.parser')
    return s, soup


def retrieve_observed(args):
    """
    NEED TO INCORPORATE WITH THE GET_OBSERVED_TICS FUNCTION TO SAVE TIME, SINCE all of this IS ALREADY DONE IN THAT MODULE

    Parameters
    ----------
    args : argparse.Namespace
        command-line arguments
    args.reorder : List(str)
        current list of observed sectors sorted by ascending order

    Returns
    -------
    args : argparse.NameSpace
        updated command-line arguments

    """
    # Start request session to pull information from MAST
    s, soup = make_soup(args)
    # Iterate through links on website and append relevant ones to dict
    for l in soup.find_all("a", href=re.compile('lc.sh')):
        sector = int(l.get('href').split('/')[-1].split('.')[0].split('_')[2])
        if 'fast' in l.get('href'):
            cadence='fast'
        else:
            cadence='short'
        if '%s%03d'%(cadence[0].upper(),sector) not in args.mast:
            args.mast['%s%03d'%(cadence[0].upper(),sector)] = {}
        args.mast['%s%03d'%(cadence[0].upper(),sector)].update({'link':'%s%s'%('/'.join(args.url.split('/')[:3]),l.get('href'))})
    observed = set([x for x in args.mast])
    args.reorder = sorted(observed)
    return args


def retrieve_existing(args):
    """
    If local file already exists, see what has been logged so as to not duplicate
    efforts and hence, require more computation time.

    Parameters
    ----------
    args : argparse.Namespace
        command-line arguments
    args.new : List(str)
        columns (i.e. sectors/cadences) which are not shared between the two dataframes aka new

    Returns
    -------
    args : argparse.NameSpace
        updated command-line arguments

    """
    args.new = []
    # If a local observed target list already exists, removes columns that are already in it to save time
    if os.path.exists(args.pathall):
        df = pd.read_csv(args.pathall)
        df.set_index('tic', drop=True, inplace=True)
        for key in list(observed.intersection(set(df.columns.values.tolist()))):
            no = args.mast.pop(key)
        args.all_tics += df.index.values.tolist()
        args.new = list(observed.difference(set(df.columns.values.tolist())))
    # get output if verbose is True
    if args.verbose:
        get_status_output(args)
    return args 


def get_new_sectors(args):
    """
    Similar to `get_all_sectors`, this module pulls target information for a given sector and cadence
    from MAST. This is used to update the observed target list and therefore only does it for newly added
    data. Note: it does not save the info to a .txt file like the other does 

    """
    s, soup = make_soup(args)
    # Save new shell scripts to local directory (path)
    if args.verbose and args.progress:
        pbar = tqdm(total=len(args.mast))
    for key in args.mast:
        response = s.get(args.mast[key]['link'])
        with open('%s/%s'%(args.path,args.mast[key]['link'].split('/')[-1]), "wb") as file:
            file.write(response.content)
        with open('%s/%s'%(args.path,args.mast[key]['link'].split('/')[-1]), "r") as sh:
            lines = sh.readlines()
        os.remove('%s/%s'%(args.path,args.mast[key]['link'].split('/')[-1]))
        args.mast[key].update({'tic':[int(line.split()[5].split('-')[2]) for line in lines[1:]]})
        args.all_tics += args.mast[key]['tic']
        if args.verbose and args.progress:
            pbar.update(1)
    if args.verbose and args.progress:
        pbar.close()
    args.all_tics = sorted(list(set(args.all_tics)))
    return args


def combine_sectors(args):
    """
    Combines observed target lists by sectors and cadences into one large list/table. For now,
    it iterates by file so it does not open up multiple files for each target. I am unsure if this 
    is the most efficient way to do this (so TBD).
    
    Parameters
    ----------
    args : argparse.Namespace
        command-line arguments

    Returns
    -------
    df : pandas.DataFrame
        full observed TESS target list

    """
    if os.path.exists(args.pathall):
        df = pd.read_csv(args.pathall)
    else:
        df = pd.DataFrame(columns=args.reorder)
    df.set_index('tic', drop=True, inplace=True)
    # Make large csv with all observed targets per sector per cadence
    tics = sorted(list(set(args.all_tics)))
    new_df = pd.DataFrame(index=tics, columns=args.reorder)
    for tic in new_df.index.values.tolist():
        # first copy information from existing table
        if tic in df.index.values.tolist():
            for column in df.columns.values.tolist():
                new_df.loc[tic,column] = df.loc[tic,column]
        # add any new targets or information
        for column in list(args.mast.keys()):
            if tic in args.mast[column]['tic']:
                new_df.loc[tic,column] = True
    # Fill nan values
    df = new_df.fillna(False)
    # Get target totals
    df = add_target_totals(df, args)
    if args.save:
        df.index.name = 'tic'
        df.to_csv(args.pathall)
        df.reset_index(inplace=True)
    return df


def add_target_totals(df, args, reorder=[]):
    """
    Adds

    """
    # add total number of sectors per target per cadence
    for cadence in args.cadences:
        cols = [col for col in df.columns.values.tolist() if col.startswith('%s'%cadence[0].upper())]
        df['%sTOT'%cadence[0].upper()]=df[cols].sum(axis=1)
        cols += ['%sTOT'%cadence[0].upper()]
        reorder += cols
    # reorder columns of final dataframe
    df_new = pd.DataFrame(columns=reorder)
    for column in reorder:
        df_new[column] = df[column]
    df = df_new.sort_values(by=['FTOT','STOT'], ascending=[False,False])
    return df


def get_info(df, args, output='', line_length=50):
    """
    Calls the `get_observed_subset` module to crossmatch the target(s) of interest with 
    the complete observed target list and displays (i.e. prints) the relevant information 
    if `args.verbose` is `True` (default).

    Parameters
    ----------
    df : pandas.DataFrame
        complete list of observed TESS targets
    args : argparse.Namespace
        command-line arguments
    output : str
        optional verbose output
    line_length : int
        optional verbose output line width (default is `50`)

    """
    # Crossmatch full table with targets of interest
    df = get_observed_subset(df, args)
    if args.download:
        make_script(df, args)


def get_observed_subset(df, args):
    """
    Filters the complete list of observed TESS targets by TIC IDs and saves
    output to my_observed_tics.csv (by default)

    Parameters
    ----------
    df : pandas.DataFrame
        complete list of observed TESS targets
    args : argparse.Namespace
        command-line arguments
    args.save : bool
        if `True`, saves output to `'my_observed_tics.csv'`

    Returns
    -------
    df : pandas.DataFrame
        observed TESS target list filtered on the target(s) of interest (via `args.stars`)

    """
    # Filter on target(s) of interest
    filter_df = df[df['tic'].isin(args.stars)]
    df = filter_df.copy()
    # Account for any stars not in csv (i.e. long-cadence)
    check = set(args.stars)
    df_updated = pd.DataFrame({'tic':list(check.difference(set(df.tic.values.tolist())))})
    # Add them to csv and fix format
    df_all = df.merge(df_updated, how='outer', on='tic')
    df = df_all.astype({'tic':'int64'})
    df = df.fillna(False)
    df.set_index('tic', inplace=True)
    # Add total counts
    df = add_target_totals(df, args)
    if args.save:
        df.to_csv(args.pathsub)
    return df


def make_script(df, args, script='#!/bin/sh\n'):
    import subprocess
    # remake soup
    s, soup = make_soup(args)
    # set by tic for easier searching
    df.set_index('tic', inplace=True, drop=True)
    drop = [col for col in df.columns.values.tolist() if 'TOT' in col]
    df.drop(columns=drop, inplace=True)
    # easiest way is to iterate through scripts to prevent opening same file several times
    for sector in args.mast:
        response = s.get(args.mast[sector]['link'])
        with open('%s/%s'%(args.path,args.mast[sector]['link'].split('/')[-1]), "wb") as file:
            file.write(response.content)
        with open('%s/%s'%(args.path,args.mast[sector]['link'].split('/')[-1]), "r") as sh:
            lines = sh.readlines()
        os.remove('%s/%s'%(args.path,args.mast[key]['link'].split('/')[-1]))
        tics=[int(line.split()[5].split('-')[2]) for line in lines[1:]]
        indices = df.index[df[sector]].values.tolist()
        for idx in indices:
            find = tics.index(idx)
            script += '%s\n'%lines[find+1]
    with open('%s/%s.sh'%(args.path,args.pathsub.split('.csv')[0]), "wb") as file:
        file.write(script)
#    subprocess.call(['%s/%s.sh'%(args.path,args.pathsub.split('.csv')[0])],shell=True)


def get_status_output(args):
    """
    Verbose output for new or updated results from the MAST query

    Parameters
    ----------
    args : argparse.Namespace
        command-line arguments

    """
    if not os.path.exists(args.pathall):
        if args.progress:
            output = '\nCreating full observed target list:'
        else:
            output = '\nCreating master list of all observed TESS targets\n *note: this will take a couple minutes if running for the first time'
    else:
        if args.new:
            if args.progress:
                output = '\nUpdating observed target list:'
            else:
                output = '\nUpdating master target list w/ %d new sectors'%len(args.new)
        else:
            output = '\nNo updates needed at this time'
            args.progress = False
    print(output)


def get_final_output(args, output='', line_length=50):
    """
    Verbose output for individual targets of interest

    Parameters
    ----------
    args : argparse.Namespace
        command-line arguments

    """
    for star in args.stars:
        tic = 'TIC %d'%star
        output+='\n##################################################\n%s\n##################################################\n'%tic.center(line_length)
        for cadence in args.cadences:
            x = ''
            count=0
            filter_cols = [col for col in df if col.startswith('%s'%cadence[0].upper()) and not col.endswith('T')]
            for column in filter_cols:
                if df.loc[star,column]:
                    x += '%d, '%int(column[1:])
                    count+=1
            if count != 0:
                output += '\n%d sectors(s) of %s cadence\n-> observed in sector(s): '%(count,cadence)
                if len(x[:-2]) <= (line_length-28):
                    output += '%s\n'%x[:-2]
                else:
                    p = ''
                    c = 0
                    for each in x[:-2].split(', '):
                        p+='%s, '%each
                        if len(p) > (line_length-28):
                            if c == 0:
                                output += '%s\n'%p
                            else:
                                output += '%s%s\n'%(' '*26, p.ljust(line_length-28))
                            p = ''
                            c += 1
                    output += '%s%s\n'%(' '*26, p[:-2].ljust(line_length-28))
            else:
                output += '\n%d sector(s) of %s cadence\n'%(count, cadence)
    print(output)