# ``ticguide`` : quick TESS data and observing info

Complementary to the TESS observing tool [``tvguide``](https://github.com/tessgi/tvguide) (see also [WTV](https://heasarc.gsfc.nasa.gov/cgi-bin/tess/webtess/wtv.py)), which tells you if your target *will be* observed by TESS (i.e. on silicon, guaranteed FFI coverage), this tool tells you if your target ***was**** observed by TESS in other cadences (i.e. short- and fast-cadence). * **this draws only from available MAST observations and therefore does not inform you of upcoming sectors.** 

### UPDATE: New 0.5.0 version will even download the data for you!

## Installation
You can install using pip:

``` bash
$ pip install ticguide
```

or via the github repository:

``` bash
$ git clone https://github.com/ashleychontos/ticguide.git
$ cd ticguide
$ python setup.py install
```

You can check your installation with the help command:

```
♡ ~ % ticguide --help
usage: ticguide [-h] [--version] [--download] [--fast] [--file path]
                [--ll int] [--path path] [--progress] [--save] [--sub path]
                [--short] [--star [star ...]] [--verbose]

ticguide: quick + painless TESS observing information

options:
  -h, --help            show this help message and exit
  --version             print version number and exit

  --download, -d        Download data for targets of interest
  --fast, -f            Do not search for fast (20-second) cadence data
  --file path, --in path, --input path, --todo path
                        input list of targets (currently works with txt or csv
                        files)
  --ll int, --linelength int
                        line length for CLI output (default=50)
  --path path           path to directory
  --progress, -p        disable the progress bar
  --save                Disable the auto-saving of relevant tables, files
                        and/or scripts for selected targets
  --sub path, --pathsub path
                        path to sub-selected sample of observed TESS targets
  --short, -s           Do not check for short (2-minute) cadence data
  --star [star ...], --stars [star ...], --tic [star ...]
                        TESS Input Catalog (TIC) IDs
  --verbose, -v         Disable the verbose output
```

## Examples

The program uses the MAST bulk downloads scripts to assemble a list of observed
TIC ids to then generate the relevant material the user wants, whether it be the
observed sectors and/or cadences or the actual data (yes, you read that right!).

CLI example (it may take a minute to run through all observed sectors, since it's
a lot now):

```
♡ ~ % tiguide --star 141810080


Grabbing bulk download info from MAST:
100%|███████████████████████████████████████████| 84/84 [00:46<00:00,  1.81it/s]

Saving target download scripts:
100%|███████████████████████████████████████████| 1/1 [00:00<00:00, 3302.60it/s]


##################################################
                  TIC 141810080                   
##################################################

26 sectors(s) of short cadence
-> observed in sector(s): 1, 2, 3, 4, 5, 6, 7, 8, 
                          9, 10, 11, 12, 13, 27, 
                          28, 29, 30, 31, 32, 33, 
                          34, 35, 36, 37, 38, 39, 
                                                

11 sectors(s) of fast cadence
-> observed in sector(s): 29, 30, 31, 32, 33, 34, 
                          35, 36, 37, 38, 39  
```

^^ as shown by the progress bar, the program iterated through 84 bash scripts. This 
makes sense since if TESS is currently on sector 55, which means there are 55 short-cadence 
and 29 fast-cadence sectors available (-> 55+29=84).

Command line easily handles multiple TIC IDs by appending them to a list:

```
♡ ~/tess % ticguide --star 141810080 441462736 188768068

Grabbing bulk download info from MAST:
100%|███████████████████████████████████████████| 84/84 [00:34<00:00,  2.42it/s]

Saving target download scripts:
100%|███████████████████████████████████████████| 3/3 [00:00<00:00, 6023.41it/s]


##################################################
                  TIC 141810080                   
##################################################

26 sectors(s) of short cadence
-> observed in sector(s): 1, 2, 3, 4, 5, 6, 7, 8, 
                          9, 10, 11, 12, 13, 27, 
                          28, 29, 30, 31, 32, 33, 
                          34, 35, 36, 37, 38, 39, 
                                                

11 sectors(s) of fast cadence
-> observed in sector(s): 29, 30, 31, 32, 33, 34, 
                          35, 36, 37, 38, 39    

##################################################
                  TIC 441462736                   
##################################################

2 sectors(s) of short cadence
-> observed in sector(s): 2, 29

1 sectors(s) of fast cadence
-> observed in sector(s): 29

##################################################
                  TIC 188768068                   
##################################################

11 sectors(s) of short cadence
-> observed in sector(s): 17, 20, 24, 25, 26, 40, 
                          47, 50, 51, 53, 54    

6 sectors(s) of fast cadence
-> observed in sector(s): 40, 47, 50, 51, 53, 54
```

**The new download feature can be seen by the second progress bar. Even if
you didn't use the download option (`-d` or `--download`), the program assumes
there is some interest in the selected targets and therefore creates a bash
script per target in the same way MAST provides bulk download scripts per sector!**

To initialize the scripts, simply run the above command with the `-d` flag:

```
♡ ~/tess % ticguide --star 141810080 441462736 188768068 -d
```

... and watch it go. To keep everything nice and neat, it will create
a parent directory called 'targets' and make one folder per target, where
the target's light curves will be downloaded to!

If you have many many targets, you can instead provide a single-column txt or csv file, with targets
listed by their TIC id (one entry per line).

```
$ head todo.csv

tic
141810080
188768068
441462736
```

A boolean table `selected_tois.csv` is created using the provided list of targets (TICs) as the table indices and all unique
combinations of the cadences and sectors as columns, where `True` would mean a given TIC was observed in the listed
cadence and sector. For example, the column "S027" means short-cadence sector 27 observations, whereas "F027" is the 
same sector but in fast cadence.


## Citation

If you find this code useful and want to cite it in your research, let me know so I can get on that!

