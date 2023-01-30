import numpy as np
import pandas as pd
from tqdm import tqdm
from bs4 import BeautifulSoup
from collections import Counter
import argparse, subprocess, requests, glob, os, re


def main(args, url='http://archive.stsci.edu/tess/bulk_downloads/bulk_downloads_ffi-tp-lc-dv.html',
         cadences=['fast','short'], script='#!/bin/sh\n'):
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
    args.cadences, args.url, args.mast, args.all_tics, args.script = [], url, {}, [], script
    # Check that the input is correct first
    check_input(args)
    # Retrieve all available TESS data from MAST
    args = get_information(args)
    # Get verbose output
    if args.verbose:
        get_final_output(args)


def check_input(args, totals=True, fileall='all_tics.csv', fileselect='selected_tics.csv'):
    """
    Checks input arguments and returns `True` if the pipeline has enough information to run.
    If an input file is provided, this function will also load in the list of targets and save
    to args.stars iff no targets are provided via command line

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
    if not os.path.isfile(args.fileinput):
        args.pathinput = os.path.join(args.path,args.fileinput)
    args.pathall = os.path.join(args.path,fileall)
    args.pathselect = os.path.join(args.path,fileselect)
    # If no targets are provided via CLI, check for todo file
    if args.stars == [] and os.path.exists(args.pathinput):
        if args.input.split('/')[-1].split('.')[-1] == 'csv' or args.input.split('/')[-1].split('.')[-1] == 'txt':
            with open (args.pathinput, "r") as f:
                args.stars = [int(line.strip()) for line in f.readlines() if line[0].isnumeric()]
    if args.short:
        args.cadences.append('short')
    if args.fast:
        args.cadences.append('fast')
    if not args.cadences:
        print("\nERROR: no desired cadences were provided as input.\nPlease use the flags '-f' for fast (i.e. 20-second) and '-s' for short (i.e. 2-minute).\nIf you'd like both you can simply type '-sf'.\n")
        return
    # set up main dictionary
    if args.stars:
        tics, args.stars = list(np.copy(args.stars)), {}
        for tic in tics:
            args.stars[tic]={}
            args.stars[tic]['data'], args.stars[tic]['script'] = [], '#!/bin/sh\n'
        if args.save:
            if not os.path.exists(os.path.join(args.path,'targets')):
                os.makedirs(os.path.join(args.path,'targets'))
            for star in args.stars:
                os.makedirs(os.path.join(args.path,'targets','%s'%str(star)))
    # if totals are desired
    if args.totals:
        args.tics={}
        for cadence in args.cadences:
            args.tics[cadence[0].upper()] = []


def get_information(args):
    """
    Uses bash scripts from the MAST bulk downloads to obtain a complete list of observed
    TIC ids in all sectors and cadences. Previous version saved a large file of all observed
    TIC ids but this has since been improved by only storing the relevant information.

    Parameters
    ----------
    args : argparse.Namespace
        command-line arguments

    Returns
    -------
    df : pandas.DataFrame
        table with observing information for relevant TICs

    If args.save is True, will save a local csv with observing information as well as a
    bash script per target for downloading, which will automatically initialize if 
    args.download == True

    Parameters
    ----------
    args : argparse.Namespace
        command-line arguments

    Returns
    -------
    df : pandas.DataFrame
        table with observing information for relevant TICs

    """
    # get available observing info from MAST
    args = get_observed(args)
    # merge with existing information
    save_totals(args)
    args = save_select(args)
    save_scripts(args)
    return args


def get_observed(args):
    """
    Iterates through all sectors and cadences from MAST to record if any targets of interest
    were observed and in so, in what sector(s) and cadence(s).

    Parameters
    ----------
    args : argparse.Namespace
        command-line arguments

    Returns
    -------
    args : argparse.NameSpace
        updated command-line arguments

    """
    args, s = get_mast(args)
    # Save new shell scripts to local directory (path)
    if args.verbose and args.progress:
        print('\nGrabbing bulk download info from MAST:')
        pbar = tqdm(total=len(args.mast))
    for key in args.mast:
        response = s.get(args.mast[key]['link'])
        with open('%s/%s'%(args.path,args.mast[key]['link'].split('/')[-1]), "wb") as file:
            file.write(response.content)
        with open('%s/%s'%(args.path,args.mast[key]['link'].split('/')[-1]), "r") as sh:
            lines = [line for line in sh.readlines() if not line.startswith('#')]
        os.remove('%s/%s'%(args.path,args.mast[key]['link'].split('/')[-1]))
        args = check_targets(key, lines, args)
        if args.verbose and args.progress:
            pbar.update(1)
    if args.verbose and args.progress:
        pbar.close()
    return args


def get_mast(args):
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
    return args, s


def make_soup(args):
    """
    Makes a delicious MAST soup, hot with all of the most important information.

    """
    # Start request session to pull information from MAST
    s = requests.session()
    r = s.get(args.url, headers=dict(Referer=args.url))
    soup = BeautifulSoup(r.content, 'html.parser')
    return s, soup


def check_targets(key, lines, args):
    """
    Now added within this first function since the file is already open and available.
    Doing it later was stupidly slow.

    Parameters
    ----------
    key : str
        dictionary key for args.mast which indicates the current sector and cadence (i.e. 'S001', 'F027', etc.)
    lines : List(str)
        bulk downloads bash script from MAST read in for sector in cadence (minus the first hashbang line)
    args : argparse.Namespace
        command-line arguments

    Returns
    -------
    args : argparse.Namespace
        updated command-line arguments

    """
    tics = [int(line.split()[5].split('-')[2]) for line in lines]
    if args.totals:
        args.tics[key[0].upper()] += tics
    for tic in args.stars:
        if tic in tics:
            args.stars[tic]['data'].append(key)
            args.stars[tic]['script'] += lines[tics.index(tic)]
    return args


def save_totals(args, d={}, types={}):
    """

    """
    if args.totals:
        for cadence in args.cadences:
            d.update({cadence:Counter(args.tics[cadence[0].upper()])})
            types.update({cadence:'int64'})
        df = pd.DataFrame(d)
        df.reset_index(drop=False, inplace=True)
        df.rename(columns={'index':'tic'}, inplace=True)
        df = df.fillna(0)
        df = df.astype(types)
        df = df.sort_values(by=['fast','short'], ascending=[False,False])
        if args.save:
            df.to_csv(args.pathall, index=False)


def save_select(args):
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
        table with observing information for relevant TICs

    """
    if args.stars:
        df = pd.DataFrame(columns=['tic']+list(args.mast.keys()))
        for i, star in enumerate(args.stars):
            df.loc[i,'tic'] = star
            for col in list(args.mast.keys()):
                if col in args.stars[star]['data']:
                    df.loc[i,col] = True
        # Fill nan values
        df_new = df.fillna(False)
        # Get target totals
        df = add_target_totals(df_new, args)
        if args.save:
            df.set_index('tic', inplace=True, drop=True)
            df.to_csv(args.pathselect)
        args.df = df.copy()
    return args


def add_target_totals(df, args, reorder=['tic']):
    """
    Adds number of sectors observed in given cadences for targets of interest

    Parameters
    ----------
    df : pandas.DataFrame
        table with observing information for relevant TICs
    args : argparse.Namespace
        command-line arguments

    """
    # add total number of sectors per target per cadence
    for cadence in args.cadences:
        cols = sorted([col for col in df.columns.values.tolist() if col.startswith('%s'%cadence[0].upper())])
        df['%sTOT'%cadence[0].upper()]=df[cols].sum(axis=1)
        cols += ['%sTOT'%cadence[0].upper()]
        reorder += cols
    # reorder columns of final dataframe
    df_new = pd.DataFrame(columns=reorder)
    for column in reorder:
        df_new[column] = df[column]
    df = df_new.sort_values(by=['FTOT','STOT'], ascending=[False,False])
    return df


def save_scripts(args):
    """
    Saves bash scripts to download data for targets of interest
    (if save is True)

    Parameters
    ----------
    args : argparse.Namespace
        command-line arguments

    """
    if args.save and args.stars:
        if args.verbose and args.progress:
            print('\nSaving target download scripts:')
            pbar = tqdm(total=len(args.stars))
        for star in args.stars:
            with open(os.path.join(args.path,'targets','%s'%str(star),'download.sh'), "w") as file:
                file.write(args.stars[star]['script'])
            if args.verbose and args.progress:
                pbar.update(1)
        if args.verbose and args.progress:
            pbar.close()
            print()
        init_scripts(args)


def init_scripts(args):
    """
    Initializes scripts to download data in relevant directories
    (if download is True)

    Parameters
    ----------
    args : argparse.Namespace
        command-line arguments

    """
    if args.download:
        print('\nDownloading target data:')
        for script in glob.glob(os.path.join(args.path,'targets','*','*.sh')):
            dir, fname = os.path.split(script)
            os.chdir(dir)
            subprocess.call(['chmod +x %s'%fname], shell=True)
            subprocess.call(['./%s'%fname])
            os.remove(fname)
        print('\n\n -- complete --\n')


def get_final_output(args, output='', linelength=50):
    """
    Verbose output for individual targets of interest

    Parameters
    ----------
    args : argparse.Namespace
        command-line arguments

    """
    for star in args.stars:
        tic = 'TIC %d'%star
        output+='\n##################################################\n%s\n##################################################\n'%tic.center(args.linelength)
        for cadence in args.cadences:
            x, count = '', 0
            filter_cols = [col for col in args.df.columns.values.tolist() if col.startswith('%s'%cadence[0].upper()) and not col.endswith('T')]
            for column in filter_cols:
                if args.df.loc[star,column]:
                    x += '%d, '%int(column[1:])
                    count+=1
            if count != 0:
                output += '\n%d sectors(s) of %s cadence\n-> observed in sector(s): '%(count,cadence)
                if len(x[:-2]) <= (args.linelength-28):
                    output += '%s\n'%x[:-2]
                else:
                    p = ''
                    c = 0
                    for each in x[:-2].split(', '):
                        p+='%s, '%each
                        if len(p) > (args.linelength-28):
                            if c == 0:
                                output += '%s\n'%p
                            else:
                                output += '%s%s\n'%(' '*26, p.ljust(args.linelength-28))
                            p = ''
                            c += 1
                    output += '%s%s\n'%(' '*26, p[:-2].ljust(args.linelength-28))
            else:
                output += '\n%d sector(s) of %s cadence\n'%(count, cadence)
    print(output)