# -*- coding: utf-8 -*-

import pandas as pd
from .data_dictionary import DataDictionary

class DataTable(): 
    """A class for reading a UK Data Service .tab data table file
    """
    
    def __init__(self,fp_tab=None,fp_dd=None):
        """
        
        Arguments:
            fp_tab (str): a filepath to a UK Data Service .tab data table file
            fp_dd (str): a filepath to a UK Data Service data dictionary .rtf file
        
        """
        if fp_tab: self.read_tab(fp_tab)
        if fp_dd: self.read_datadictionary(fp_dd)
        
        
    def read_tab(self,fp_tab):
        """Reads in a .tab file
        
        Arguments:
            fp_tab (str): a filepath to a UK Data Service .tab data table file
        
        """
        self.tab=pd.read_csv(fp_tab,
                             sep='\t',
                             skipinitialspace=True
                            )
    
    
    def read_datadictionary(self,fp_dd):
        """Reads in a .rtf file
        
        Arguments:
            fp_dd (str): a filepath to a UK Data Service data dictionary .rtf file
        
        """
        self.datadictionary=DataDictionary(fp_dd)
            
        
        
    def get_dataframe(self):
        """Returns a pandas DataFrame based on the ukds .tab and .rtf files
        
        Returns:
            (pandas.DataFrame)
        
        """
    
        def get_column_multiindex(columns,datadictionary):
            
            names=['variable',
                   'variable_label',
                   'variable_type',
                   'SPSS_measurement_level',
                   'SPSS_user_missing_values',
                   #'value_labels',
                   'pos']
            #print(names)
            
            l=[]
            
            for col in columns:
                #print(col)
                variable=datadictionary.get_variable_dict(col)
                t=tuple([str(variable[x]) for x in names])
                l.append(t)
            #print(l)
            
            column_index=pd.MultiIndex.from_tuples(l,names=names)
            #print(column_index)
            
            return column_index
            
            
        df=self.tab.copy()
            
        # rename columns
        column_index=get_column_multiindex(df.columns,self.datadictionary)
        df.columns=column_index
        
        # replace values
        for col in df.columns:
            #print(col)
            value_labels=self.datadictionary.get_variable_dict(col[0])['value_labels']
            #print(value_labels)
            df[col]=df[col].replace(value_labels)
        
        return df
        