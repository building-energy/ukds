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

#### Importing the DataTable class

```python
from ukds import DataTable
```

#### Creating an instance of DataTable and reading in the data file and the datadictionary file

Either:

```python
dt=DataTable()
dt.read_tab(r'.../uktus15_household.tab')
df.read_datadictionary(r'.../uktus15_household_ukda_data_dictionary.rtf')
```

or:

```python
dt=DataTable(fp_tab=r'.../uktus15_household.tab',
             fp_dd=r'.../uktus15_household_ukda_data_dictionary.rtf')
```

#### Attributes

As the files are read in, a number of attributes are populated. These are:

```python
dt.tab				# a pandas.DataFrame object
dt.datadictionary	# a ukds.DataDictionary object
```

#### get_dataframe method

The method `get_dataframe` is available which converts the information in the `tab` and `datadictionary` attributes into a new pandas DataFrame.

```python
dt=df.get_dataframe()
```

See the [datatable_demo.ipynb](https://nbviewer.jupyter.org/github/building-energy/ukds/blob/master/demo/datatable_demo.ipynb) Jupyter Notebook in the 'demo' section for more information.






### The `DataDictionary` class

The **DataDictionary** class provides access to UKDS .rtf data dictionary files.

#### Importing the DataDictionary class

```python
from ukds import DataDictionary
```

#### Creating an instance of DataTable and reading in the data file and the datadictionary file

Either:

```python
dd=DataDictionary()
dd.read_rtf(r'.../uktus15_household_ukda_data_dictionary.rtf')
```

or:

```python
dd=DataDictionary(fp_dd=r'.../uktus15_household_ukda_data_dictionary.rtf')
```

#### Attributes

As the file are read in, a number of attributes are populated. These are:

```python
dt.rtf				# a string of the raw contents of the rtf file
dt.variablelist		# a list of dictionaries with the variable information
```

#### get_variable_dict method

Returns a dictionary with the information for a single variable. For example:

```python
serial=dd.get_variable_dict('serial')
```

returns:

```python
{'pos': '1',
 'variable': 'serial',
 'variable_label': 'Household number',
 'variable_type': 'numeric',
 'SPSS_measurement_level': 'SCALE',
 'SPSS_user_missing_values': '',
 'value_labels': ''}
```

#### get_variable_names method

Returns a list of the variable names:

```python
dd.get_variable_names()
```

See the [datadictionary_demo.ipynb](https://nbviewer.jupyter.org/github/building-energy/ukds/blob/master/demo/datadictionary_demo.ipynb) Jupyter Notebook in the 'demo' section for more examples based on this class.






