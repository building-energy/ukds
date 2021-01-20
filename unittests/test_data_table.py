# -*- coding: utf-8 -*-

import unittest
import ukds, os
from fairly import CreateRDF

base_dir=os.path.join(*[os.pardir]*4,r'_Data\United_Kingdom_Time_Use_Survey_2014-2015\UKDA-8128-tab')
dt_fp=os.path.join(base_dir,r'tab\uktus15_household.tab')
dd_fp=os.path.join(base_dir,r'mrdoc\allissue\uktus15_household_ukda_data_dictionary.rtf')

dt=ukds.DataTable(dt_fp,dd_fp)
dt.tab=dt.tab.head(5)

class Test_data_table(unittest.TestCase):

    def test_to_bso_variable(self):
        
        c=dt.to_bso_variable(base_prefix='eg',
                            base_uri='http://example.com/',
                            variable='hh_wt',
                    )
        print(c.serialize_rdf())
        
    def test_to_bso_survey(self):
        
        c=dt.to_bso_survey(base_prefix='eg',
                     base_uri='http://example.com/',
                     )
        #print(c.serialize_rdf())
    
    
# general query methods
    
    #def test_read_tab(self):
        
    
        #dt=ukds.DataTable(dt_fp)
        #df=dt.tab
        
        #print(df[df.columns[:5]])
        
        #print(df.dtypes)
    
    
    #def test_get_dataframe(self):
        
        #dt=ukds.DataTable(dt_fp,dd_fp)
        #df=dt.get_dataframe()
        
        #df.head()
        
        
#    def test_to_rdf_data_cube(self):
#        
#        c=dt.to_rdf_data_cube(base_prefix='ukds8128',
#                              base_uri='<http://www.purl.org/berg/ukds8128/>',
#                              dimension_columns=['serial'],
#                              column='strata',
#                              )
#        #print(c.serialize())
        
#    def test_to_rdf_bdo_observation_datum(self):
#        
#        st=dt.to_rdf_bdo_observation_datum(base_prefix='household',
#                                           base_uri='http://www.purl.org/berg/ukds8128/uktus15_household/',
#                                           column_name='strata',
#                                           row_index=0
#                                           )
#        print(st)
#        
#    def test_to_rdf_bdo_observation(self):
#        
#        st=dt.to_rdf_bdo_observation(base_prefix='household',
#                                     base_uri='http://www.purl.org/berg/ukds8128/uktus15_household/',
#                                     row_index=0
#                                     )
#        print(st)
#        
#    def test_to_rdf_bdo_observation_set(self):
#        
#        st=dt.to_rdf_bdo_observation_set(base_prefix='household',
#                                         base_uri='http://www.purl.org/berg/ukds8128/uktus15_household/',
#                                         )
#        print(st)
#        
#    def test_to_rdf_bdo_observation_data_set(self):
#        
#        st=dt.to_rdf_bdo_observation_data_set(base_prefix='household',
#                                              base_uri='http://www.purl.org/berg/ukds8128/uktus15_household/',
#                                              column_name='strata'
#                                              )
#        print(st)
        
        
        
        
        
if __name__=='__main__':
    
    o=unittest.main(Test_data_table())    
    
    
    
    
    
    
    
    
    
    
    