# ``ticguide``: **quick + painless TESS observing information**

Complementary to the TESS observing tool [``tvguide``](https://github.com/tessgi/tvguide) (see also [WTV](https://heasarc.gsfc.nasa.gov/cgi-bin/tess/webtess/wtv.py)), which tells you if your target *will be* observed by TESS (i.e. on silicon, guaranteed FFI coverage), this tool tells you if your target ***was**** observed by TESS in other cadences (i.e. short- and fast-cadence). * **this draws only from available MAST observations and therefore does not inform you of upcoming sectors.** (BUT if you know of a way to do this, let's chat!)

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
TIC IDs (which is currently ~150 Mb, so this will take a few minutes). You have an option to disable the
auto-saving of this table and it will still pass the pandas dataframe, but it will need to make this each
time you run the program. Therefore if you use this often, I recommend letting it save a local csv file.

Example of running `ticguide` for the first time with the default settings:

```
$ ticguide --star 141810080

Creating full observed target list:
100%|███████████████████████████████████████████| 64/64 [03:46<00:00,  3.54s/it]

##################################################
                  TIC 141810080                   
##################################################

26 sectors(s) of short cadence
-> observed in sector(s): 1, 2, 3, 4, 5, 6, 7, 8, 
                          9, 10, 11, 12, 13, 27, 
                          28, 29, 30, 31, 32, 33, 
                          34, 35, 36, 37, 38, 39 
                                                

11 sectors(s) of fast cadence
-> observed in sector(s): 29, 30, 31, 32, 33, 34, 
                          35, 36, 37, 38, 39  
                         
```

^^ as shown by the progress bar, it iterated through 64 bash scripts. This makes sense
since TESS is currently on sector 45, which means there are 45 short-cadence and 19 
fast-cadence sectors available (-> 45+19=64).

Command line easily hands multiple TIC IDs by appending them to a list:

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

When the list of targets starts to be on the order of 10 or more, it is probably less helpful
to print the output in the terminal. This can be supressed by using the `--verbose` (or `-v`) 
command:

```
$ ticguide --star 141810080 -v

```


If you have many targets, perhaps it might be more convenient to provide 
a list of targets via a csv file. You can easily do this by providing a single-column csv, with targets
listed by their TIC id (under `'tic'`, one entry per line).
```
$ head todo.csv

tic
231663901
149603524
336732616
231670397
144065872
38846515
92352620
289793076
29344935
```

The example file `todo.csv` is a subset list of TESS planet candidates (TOIs), which may be of interest
to some folks so let's see how often systems were observed for. Use the following command:
```
$ ticguide --file todo.csv

Writing my_tics_observed.csv.

$ head my_tics_observed.csv

141810080, 

```
This new file appends two additional columns. The number in the first column is the minimum number of sectors the target is observable for and the second is the maximum.

You can also run from within a Python script:
```python
import ticguide


```

## Citation
If you find this code useful and want to cite it in your research then we have made that possible for you
```

