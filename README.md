# ukds
A Python package for working with datasets from the UK Data Service (UKDS).

Any problems? [Please raise an Issue on GitHub](https://github.com/building-energy/ukds/issues)

## To install:

`pip install ukds`

## Quick Demo

(This demonstration uses the following dataset: *Gershuny, J., Sullivan, O. (2017). United Kingdom Time Use Survey, 2014-2015. Centre for Time Use Research, University of Oxford. [data collection]. UK Data Service. SN: 8128, <http://doi.org/10.5255/UKDA-SN-8128-1>*)

The following code reads a UK Data Service .tab data file and its associated .rtf data dictionary file, and converts them to a Pandas DataFrame:

```python
import ukds
dt=UKDS.DataTable(fp_tab=r'.../uktus15_household.tab'
                  fp_dd=r'.../uktus15_household_ukda_data_dictionary.rtf')
df=dt.get_dataframe()
```

The DataFrame looks like this:

![dataframe_screenshot](https://github.com/building-energy/ukds/raw/master/DataTable_screenshot.png)

##  User Guide

The ukds package provides two classes:

### The `DataTable` class

The DataTable class converts a UKDS .tab data file and .rtf data dictionary file into a single Pandas DataFrame ready for further analysis.


See the [datatable_demo.ipynb](https://nbviewer.jupyter.org/github/building-energy/ukds/blob/master/demo/datatable_demo.ipynb) Jupyter Notebook in the 'demo' section for more information.


### The `DataDictionary` class

The **DataDictionary** class provides access to UKDS .rtf data dictionary files.

An example of its use is:

```python
>>> import ukds
>>> dd=UKDS.DataDictionary(r'.../uktus15_household_ukda_data_dictionary.rtf')
>>> serial=dd.get_variable_dict('serial')
>>> print(serial)

{'pos': '1',
 'variable': 'serial',
 'variable_label': 'Household number',
 'variable_type': 'numeric',
 'SPSS_measurement_level': 'SCALE',
 'SPSS_user_missing_values': '',
 'value_labels': ''}
```

For a full description, see the [datadictionary_demo.ipynb](https://nbviewer.jupyter.org/github/building-energy/ukds/blob/master/demo/datadictionary_demo.ipynb) Jupyter Notebook in the 'demo' section.






