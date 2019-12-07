# ukds
A Python package for working with datasets from the UK Data Service (UKDS)





## Quick Demo

(This demonstration uses the following dataset: *Gershuny, J., Sullivan, O. (2017). United Kingdom Time Use Survey, 2014-2015. Centre for Time Use Research, University of Oxford. [data collection]. UK Data Service. SN: 8128, <http://doi.org/10.5255/UKDA-SN-8128-1>*)

The **DataDictionary** class provides access to UKDS .rtf data dictionary files:

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









## DataDictionary class



See <https://nbviewer.jupyter.org/github/building-energy/ukds/blob/master/demo/datadictionary_demo.ipynb>

