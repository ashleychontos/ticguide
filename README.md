# ``ticguide``: **quick + painless TESS observing information**

Complementary to the TESS observing tool [``tvguide``](https://github.com/tessgi/tvguide) (see also [WTV](https://heasarc.gsfc.nasa.gov/cgi-bin/tess/webtess/wtv.py)), which tells you if your target *will be* observed by TESS (i.e. on silicon, guaranteed FFI coverage), this tool tells you if your target ***was**** observed by TESS in other cadences (i.e. short- and fast-cadence). * **this draws only from available MAST observations and therefore does not inform you of upcoming sectors.** 

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
$ ticguide --help
usage: ticguide [-h] [--file path] [--out path] [--path path] [-p] [-s]
                [--star [star [star ...]]] [-t] [-v]

optional arguments:
  -h, --help            show this help message and exit
  --file path, --in path, --input path
                        input list of targets (requires csv with 'tic' column
                        of integer type)
  --out path, --output path
                        path to save the observed TESS table for all targets
  --path path           path to directory
  -p, --progress        disable the progress bar
  -s, --save            disable the saving of output files
  --star [star [star ...]], --stars [star [star ...]], --tic [star [star ...]]
                        TESS Input Catalog (TIC) IDs
  -t, --total           include total sectors per target per cadence
  -v, --verbose         turn off verbose output
```

## Examples

When running the command for the first time, the program will need to make a local copy of all observed
TIC IDs (which is currently ~150 Mb, so this will take a few minutes depending on your computer). You have 
an option to disable the auto-saving of this table and it will still pass the pandas dataframe, but it will 
need to make this each time you run the program. Therefore if you use this often enough, I recommend letting 
it save a local csv file.

Example output when running `ticguide` for the first time with the default settings:

```
$ ticguide --star 141810080

Creating full observed target list:
100%|███████████████████████████████████████████| 64/64 [01:30<00:00,  1.41s/it]

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

^^ as shown by the progress bar, the program iterated through 64 bash scripts. This 
makes sense since if TESS is currently on sector 45, which means there are 45 short-cadence 
and 19 fast-cadence sectors available (-> 45+19=64).

Command line easily handles multiple TIC IDs by appending them to a list:

```
$ ticguide --star 141810080 441462736 188768068

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

6 sectors(s) of short cadence
-> observed in sector(s): 17, 20, 24, 25, 26, 40

1 sectors(s) of fast cadence
-> observed in sector(s): 40
```

If you have many many targets, you can instead provide a single-column txt or csv file, with targets
listed by their TIC id (one entry per line).

```
$ head todo.csv

tic
141810080
188768068
441462736
```

A boolean table is created using the provided list of targets (TICs) as the table indices and all unique
combinations of the cadences and sectors as columns, where `True` would mean a given TIC was observed in the listed
cadence and sector. For example, the column "S027" means short-cadence sector 27 observations, whereas "F027" is the 
same sector but in fast cadence.


## Citation

If you find this code useful and want to cite it in your research, let me know so I can get on that!

