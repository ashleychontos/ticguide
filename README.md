# ``ticguide``: **quick + painless TESS observing information**

Adapted from the TESS [``tvguide``](https://github.com/tessgi/tvguide) concept (see also [WTV](https://heasarc.gsfc.nasa.gov/cgi-bin/tess/webtess/wtv.py)), which would tell you if your target *should be* observed by TESS (i.e. in the future), this tool tells you if your target ***was*** already observed by TESS.

## Installation
You can install using pip
``` bash
$ pip install ticguide --upgrade
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

Success! The target may be observable by TESS during Cycle 1.
We can observe this source for:
    maximum: 2 sectors
    minimum: 0 sectors
    median:  1 sectors
    average: 1.16 sectors
```

You can also run on a file with targets
currently implemented is using RA and Dec.
```
$ head inputfilename.csv

150., -60.
10., -75.
51., 0.
88., +65

$ tvguide-csv inputfilename.csv

Writing example-file.csv-tvguide.csv.

$ head example-file.csv-tvguide.csv

150.0000000000, -60.0000000000, 0, 2
10.0000000000, -75.0000000000, 1, 3
51.0000000000, 0.0000000000, 0, 1
88.0000000000, 65.0000000000, 0, 0
```
This new file appends two additional columns. The number in the first column is the minimum number of sectors the target is observable for and the second is the maximum.

You can also run from within a Python script:
```python
import ticguide

ticguide.check_observable(150.00, -60.00)

ticguide.check_many(ra_array, dec_array)
```

## Citation
If you find this code useful and want to cite it in your research then we have made that possible for you
```
Mukai, K. & Barclay, T. 2017, tvguide: A tool for determining whether stars and galaxies are observable by TESS., v1.0.0, Zenodo, doi:10.5281/zenodo.823357
