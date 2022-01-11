import numpy as np
import pandas as pd
from tqdm import tqdm
from bs4 import BeautifulSoup
import argparse, requests, glob, os, re


def main(args, url='http://archive.stsci.edu/tess/bulk_downloads/bulk_downloads_ffi-tp-lc-dv.html',
             cadences=['short','fast'], columns=['files','sectors'],):
    """
    Main function call to run the `ticguide` search

    Parameters
    ----------
    args : argparse.Namespace
        the command line arguments
    url : str
        link to MAST bulk downloads page -> this should NOT need to be changed for any reason
    cadences : List(str)
        dlfkajd
    columns: List(str)
        dfjlda

    """

    args.cadences, args.columns, args.url = cadences, columns, url
    # Check that the input is correct first
    if check_input(args):
        # Retrieve massive table of observed TESS targets
        df_all = check_table(args)
        # Filter based on the TIC (or TICs) provided
        get_info(df_all, args)


def check_input(args):
    """
    Checks input arguments and returns `True` if the pipeline has enough information to run.
    If an input csv is provided, this function will load in the csv and save the list of targets 
    to args.stars

    Parameters
    ----------
    args : argparse.Namespace
        command-line arguments
    args.fname : str
        path to targets with updated observing information

    Returns
    -------
    bool

    """

    if not os.path.isfile(args.input):
        args.input = os.path.join(args.path,args.input)
    if not os.path.isfile(args.output):
        args.output = os.path.join(args.path,args.output)
    args.fname = os.path.join(args.path,'my_tics_observed.csv')

    # If no targets are provided via CLI, check for todo file
    if args.stars is None:
        if os.path.exists(args.input):
            if args.input.split('/')[-1].split('.')[-1] == 'csv':
                df = pd.read_csv(args.input)
                args.stars = [int(tic) for tic in df.tic.values.tolist()]
            elif args.input.split('/')[-1].split('.')[-1] == 'txt':
                with open (args.input, "r") as f:
                    args.stars = [int(line.strip()) for line in f.readlines() if line[0].isnumeric()]
            else:
                print('\nERROR: Did not understand input file type. Please try again.\n')
        else:
            print('\nERROR: No targets were provided')
            print('*** please either provide entries via command line \n    or an input csv file with a list of TICs (via todo.csv) ***\n')
            return False
    return True


def check_table(args):
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
    args.output : str
        path to csv file for all observed TESS targets

    Returns
    -------
    df : pandas.DataFrame
        pandas dataframe containing all targets observed in TESS short- and fast-cadence by 'tic' id

    """
    # If the table does not already exist, it will make a new one
    # note: it asks this because it will take a little while to make
    # ** you can dl the table from my github repo to skip this **
    if not os.path.exists(args.output):
        if args.verbose:
            if args.progress:
                print('\nCreating full observed target list:')
            else:
                print('\nCreating master list of all observed TESS targets\n *note: this will take a couple minutes if running for the first time')
        df = make_table(args)
    # If there is a local copy, it will first check if it is up-to-date,
    # which is done by getting the latest sector from MAST and seeing if
    # there is a column for the current sector -> STILL TODO
    else:
#        sector = get_current_sector()
        df = pd.read_csv(args.output)
#        filter_col = [col for col in df if not col.endswith('T')]
#        cols = list(set([int(column[1:]) for column in filter_col]))
#        if sector not in cols:
#            update_table(args)
    return df


def make_table(args):
    """
    Creates a large dataframe for all targets observed by TESS in short- and fast-cadence
    data. Given the success of TESS, we fortunately have many sectors so this step takes a few
    minutes if creating the table from scratch. By default, it will save the table as a csv file 
    (which is currently ~150 Mb).

    """
    # Get observed targets
    get_observed_sectors(args)

    # Combine them into one large dataframe
    df = combine_sectors(args)

    # Fill nan values
    df = df.fillna(False)
    if args.save:
        df.index.name = 'tic'
        df.to_csv(args.output)
        df.reset_index(inplace=True)
    return df


def get_observed_sectors(args, links=[]):
    """
    Downloads bulk downloads scripts from MAST and iterates through these files to create
    a complete list of observed TESS targets for a given sector and cadence. It will delete
    the bash scripts when finished.

    """
    # Start request session to webscrape
    s = requests.session()
    r = s.get(args.url, headers=dict(Referer=args.url))
    soup = BeautifulSoup(r.content, 'html.parser')

    # Iterate through links on website and append relevant ones to list
    for l in soup.find_all("a", href=re.compile('lc.sh')):
        links.append('%s%s'%('/'.join(args.url.split('/')[:3]),l.get('href'))) 
    links = list(set(links))

    # Save shell scripts to local directory (path)
    for link in links:
        response = s.get(link)
        with open('%s/%s'%(args.path,link.split('/')[-1]), "wb") as file:
            file.write(response.content)

    # Open files to save observed targets, which will remove the script after the text file is saved
    files = glob.glob('%s/*%s'%(args.path,'lc.sh'))
    for file in files:
        fn = '%s/sector_%s'%(args.path,file.split('/')[-1].split('_')[-2])
        if 'fast' in file:
            fn+='_fast'
        fn += '.txt'
        with open(file, "r") as sh:
            lines = sh.readlines()
        lines = lines[1:]
        # Iterate through lines and save the tics to text
        text=''
        for line in lines:
            text += '%d\n'%int(line.split()[5].split('-')[2])
        with open(fn, "w") as f:
            f.write(text)
        # Remove file once completed
        os.remove(file)


def combine_sectors(args, observed={}, cols=[], all_tic=[],):
    """
    Combines observed target lists by sectors and cadences into one large list/table. For now,
    it iterates by file so it does not open up multiple files for each target. I am unsure if this 
    is the most efficient way to do this (so TBD).
    
    Parameters
    ----------
    args : argparse.Namespace
        command-line arguments
    observed : dict
        observed TESS target list container
    cols : List(str)
        array of column names for the final observed table
    all_tic : List(int)
        complete list of observed tics over all cadences -> which become the indices for the final observed table

    """
    # Make dictionary to save file information for all current sectors+cadences
    for cadence in args.cadences:
        observed[cadence]={}
        for column in args.columns:
            observed[cadence][column]=[]
    files = glob.glob('%s/*.txt'%args.path)
    for file in files:
        if 'fast' in file:
            idx='fast'
        else:
            idx='short'
        observed[idx]['files'].append(file)
        observed[idx]['sectors'].append(int(file.split('/')[-1].split('.')[0].split('_')[1]))

    # Iterate through files and add up n_sectors per tic per cadence
    for cadence in observed:
        cols += ['%s%03d'%(cadence[0].upper(),sector) for sector in sorted(observed[cadence]['sectors'])]
        series={}
        for file in observed[cadence]['files']:
            with open(file,"r") as f:
                lines = f.readlines()
            tics = [int(line.strip()) for line in lines]
            for tic in tics:
                if tic not in series:
                    series[tic]=1
                else:
                    series[tic]+=1
        # Make csv with totals for each cadence
        s = pd.Series(series, name='n_sectors')
        s.index.name = 'tic'
        s.sort_values(ascending=False, inplace=True)
        if args.save and args.total:
            s.to_csv('%s/totals_%s.csv'%(args.path,cadence))
        all_tic += s.index.values.tolist()

    # Make large csv with all observed targets per sector per cadence
    tics = sorted(list(set(all_tic)))
    df = pd.DataFrame(index=tics, columns=cols)
    # I think easiest way for now is to search by file, so we aren't opening 20+ files per target entry (but TBD)
    files = glob.glob('%s/*.txt'%args.path)
    if args.verbose and args.progress:
        pbar = tqdm(total=len(files))
    for file in files:
        sector=int(file.split('/')[-1].split('.')[0].split('_')[1])
        if 'fast' in file:
            cadence='fast'
        else:
            cadence='short'
        column = '%s%03d'%(cadence[0].upper(),sector)
        with open(file,"r") as f:
            lines = f.readlines()
        tics = [int(line.strip()) for line in lines]
        for tic in tics:
            df.loc[tic,column]=True
        os.remove(file)
        if args.verbose and args.progress:
            pbar.update(1)
    if args.verbose and args.progress:
        pbar.close()
    return df


def add_target_totals(df, args, reorder=[], d={}):
    """
    Adds

    """
    # add total number of sectors per target per cadence
    # add part to double check this with the other csvs
    for cadence in args.cadences:
        d.update({'%sTOT'%cadence[0].upper():'int64'})
        filter_col = [col for col in df if col.startswith(cadence[0].upper())]
        filter_df = df[filter_col]
        for index in df.index.values.tolist():
            df.loc[index,'%sTOT'%cadence[0].upper()] = int(filter_df.loc[index].sum())
        # reorder columns so that cadences are displayed together
        filter_col = [col for col in df if col.startswith(cadence[0].upper())]
        df_temp = df[filter_col]
        reorder += sorted(df_temp.columns.values.tolist())
    # reorder columns of final dataframe
    df_final = pd.DataFrame(columns=reorder)
    for column in reorder:
        df_final[column] = df[column]
    df = df_final.astype(d)
    return df


def get_current_sector(args, sectors=[]):
    """
    NEED TO INCORPORATE WITH THE GET_OBSERVED_TICS FUNCTION TO SAVE TIME, SINCE all of this IS ALREADY DONE IN THAT MODULE

    Parameters
    ----------
    args : argparse.Namespace
        command-line arguments
    sectors : List(int)
        observed TESS target list filtered on the target(s) of interest
    output : str
        optional verbose output

    Returns
    -------
    

    """
    # Start request session to webscrape
    s = requests.session()
    r = s.get(args.url, headers=dict(Referer=args.url))
    soup = BeautifulSoup(r.content, 'html.parser')
    table = soup.find("tr", text = re.compile("Calibrated FFIs"))
    new_soup = table.find_parent("tbody")

    # Get all sectors and then take the max to get the most recent
    for l in new_soup.find_all("a", href=re.compile('ffic.sh')):
        link = l.get('href')
        sectors.append(int((link.split('/')[-1]).split('_')[2]))
    return max(sectors)


def update_table(args):
    """
    NEED TO DO!

    """

    pass


def get_observed_subset(df, args):
    """
    

    """
    # Filter on target(s) of interest
    filter_df = df[df['tic'].isin(args.stars)]
    df = filter_df.copy()
    # Account for any stars not in csv (i.e. long-cadence)
    check = set(args.stars)
    df_no = pd.DataFrame({'tic':list(check.difference(set(df.tic.values.tolist())))})
    # Add them to csv and fix format
    df_all = df.merge(df_no, how='outer', on='tic')
    df = df_all.astype({'tic':'int64'})
    df = df.fillna(False)
    df.set_index('tic', inplace=True)
    # Add total counts
    df = add_target_totals(df, args)
    if args.save:
        df.to_csv(args.fname)
    return df


def get_info(df, args, output=''):
    """
    Crossmatches the target(s) of interest with the complete observed target list and 
    displays (i.e. prints) the relevant information if `args.verbose` is `True` (default).

    Parameters
    ----------
    args : argparse.Namespace
        command-line arguments
    df : pandas.DataFrame
        observed TESS target list filtered on the target(s) of interest
    output : str
        optional verbose output

    """
    # Crossmatch full table with targets of interest
    df = get_observed_subset(df, args)

    if args.verbose:
        for star in args.stars:
            tic = 'TIC %d'%star
            output+='\n##################################################\n%s\n##################################################\n'%tic.center(50)
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
                    if len(x[:-2]) <= 22:
                        output += '%s\n'%x[:-2]
                    else:
                        p = ''
                        c = 0
                        for each in x[:-2].split(', '):
                            p+='%s, '%each
                            if len(p) > 22:
                                if c == 0:
                                    output += '%s\n'%p
                                else:
                                    output += '%s%s\n'%(' '*26, p.ljust(22))
                                p = ''
                                c += 1
                        output += '%s%s\n'%(' '*26, p[:-2].ljust(22))
                else:
                    output += '\n%d sector(s) of %s cadence\n'%(count, cadence)
        print(output)