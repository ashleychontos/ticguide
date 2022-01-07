# ``ticguide``: **quick + painless TESS observing information**

Adapted from the TESS [``tvguide``](https://github.com/tessgi/tvguide) concept (see also [WTV](https://heasarc.gsfc.nasa.gov/cgi-bin/tess/webtess/wtv.py)), which would tell you if your target *should be* observed by TESS (i.e. in the future), this tool tells you if your target ***was*** already observed by TESS.

## Installation
You can install using pip
``` bash
$ pip install ticguide
```

or via the github repository
``` bash
$ git clone https://github.com/ashleychontos/ticguide.git
$ cd ticguide
$ python setup.py install
```

The code has been tested in Python 3.6.

## Usage
Pick your favorite star and have a whirl. I'm a big fan of Alpha Mensae or TIC 141810080.
```
$ ticguide --star 141810080


```

If you have multiple targets, perhaps it might be more convenient to provide 
a list of targets. You can do this by providing a csv input file, with targets
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

The example file `todo.csv` is a subset list of TESS planet candidates (TOIs), which we may be interested
in learning how often a given system was observed for. Use the following command:
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

