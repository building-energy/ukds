# -*- coding: utf-8 -*-

import unittest
import ukds, os
from fairly import CreateRDF, Fuseki
from pprint import pprint

chunks=10000000

base_dir=os.path.join(*[os.pardir]*4,r'_Data\United_Kingdom_Time_Use_Survey_2014-2015\UKDA-8128-tab')
dt_fp=os.path.join(base_dir,r'tab\uktus15_household.tab')
dd_fp=os.path.join(base_dir,r'mrdoc\allissue\uktus15_household_ukda_data_dictionary.rtf')
dt=ukds.DataTable(dt_fp,dd_fp)
#print(dt)

c=CreateRDF()
c.add_data_cube_prefixes()
c.add_prefix('ukds-attribute','<http://purl.org/berg/ukds/attribute#>')
c.add_prefix('ukds-code','<http://purl.org/berg/ukds/code#>')
#print(c)

f=Fuseki('http://localhost:3030/fairly_unittest') 
f.update_request("CLEAR DEFAULT")
#print(f)   
             
class Test_fuseki_upload1(unittest.TestCase):
    
    def test1(self):
        
        c.reset_rdf()
        c1=dt.add_data_cube_observation(
                                  createRDF=c,
                                  base_uri='http://purl.org/berg/ukds/8128/uktus15_household/',
                                  row=0,
                                  row_dimension_property_suffix='household',
                                  row_dimension_value='11010903',
                                  column_variable='strata',
                                  cell_value='-2',
                                  pos=2,
                                  variable='strata',
                                  variable_label='Strata',
                                  variable_type='numeric',
                                  SPSS_measurement_level='SCALE',
                                  SPSS_user_missing_values=True,
                                  value_labels=True
                                  )
        print('len(c1.rdf)',len(c1.rdf))
        
        l=c1.sparql_update_request_chunks(chunks)
        print('no_of_chunks',len(l))
        
        f.update_request("CLEAR DEFAULT")
        for i,ru in enumerate(l):
            print(i,end=' ')
            f.update_request(ru)
        print()
    
        result=f.query_request("SELECT (COUNT(?s) AS ?triple_count) WHERE { ?s ?p ?o .}",
                               values=True)
        print(result[0])
    
    
class Test_fuseki_upload2(unittest.TestCase):

    def test1(self):
        
        c.reset_rdf()
        c1=dt.add_data_cube_observations_by_column(
                createRDF=c,
                base_uri='http://purl.org/berg/ukds/8128/uktus15_household/',
                column_variable='strata',
                row_dimension_property_suffix='household',
                row_dimension_value_function=lambda df,index: df.loc[index,'serial']
                )
        print('len(c1.rdf)',len(c1.rdf))
        
        l=c1.sparql_update_request_chunks(chunks)
        print('no_of_chunks',len(l))
        
        f.update_request("CLEAR DEFAULT")
        for i,ru in enumerate(l):
            print(i,end=' ')
            f.update_request(ru)
        print()
    
        result=f.query_request("SELECT (COUNT(?s) AS ?triple_count) WHERE { ?s ?p ?o .}",
                               values=True)
        print(result[0])

    
class Test_fuseki_upload3(unittest.TestCase):

    def test1(self):
        
        c.reset_rdf()
        c1=dt.add_data_cube_observations_by_table(
                createRDF=c,
                base_uri='http://purl.org/berg/ukds/8128/uktus15_household/',
                row_dimension_property_suffix='household',
                row_dimension_value_function=lambda df,index: df.loc[index,'serial']
                )
        print('len(c1.rdf)',len(c1.rdf))
        
        l=c1.sparql_update_request_chunks(chunks)
        print('no_of_chunks',len(l))
        
        f.update_request("CLEAR DEFAULT")
        for i,ru in enumerate(l):
            print(i,end=' ')
            f.update_request(ru)
        print()
    
        result=f.query_request("SELECT (COUNT(?s) AS ?triple_count) WHERE { ?s ?p ?o .}",
                               values=True)
        print(result[0])
    
    
if __name__=='__main__':
    
    #o=unittest.main(Test_fuseki_upload1()) 
    #o=unittest.main(Test_fuseki_upload2()) 
    o=unittest.main(Test_fuseki_upload3()) 
