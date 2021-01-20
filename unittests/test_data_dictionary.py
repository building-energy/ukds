# -*- coding: utf-8 -*-

import unittest
import ukds, os

base_dir=os.path.join(*[os.pardir]*4,r'_Data\United_Kingdom_Time_Use_Survey_2014-2015\UKDA-8128-tab')
data_dictionary_directory=os.path.join(base_dir,r'mrdoc\allissue')

        
class Test_data_dictionary(unittest.TestCase):

    def test_variable_dicts(self):
        
        result=dd.variable_dicts()
        self.assertEqual(len(result),335)
        self.assertIsInstance(result[0],dict)
    
    def test_variable_names(self):
        
        result=dd.variable_names()
        self.assertEqual(len(result),335)
        self.assertIsInstance(result[0],str)
    
    def test_variable_dict(self):
        
        result=dd.variable_dict('serial')
        answer={'pos': '1', 
                'variable': 'serial', 
                'variable_label': 'Household number', 
                'variable_type': 'numeric', 
                'SPSS_measurement_level': 'SCALE', 
                'SPSS_user_missing_values': {}, 
                'value_labels': {}}
        self.assertEqual(result,answer)
    
    
    def test_to_bso_variable(self):
  
        c=dd.to_bso_variable(base_prefix='eg',
                            base_uri='http://example.com/',
                            variable='IMonth',
                    )
        print(c.serialize_rdf())
        
    def test_to_bso(self):
        ""
        
        c=dd.to_bso(base_prefix='eg',
                    base_uri='http://example.com/',
                    )
        #print(c.rdf)
        #print(c.serialize())
    
#    def test_read_rdf(self):
#        
#        base_dir=os.path.join(*[os.pardir]*4,r'_Data\United_Kingdom_Time_Use_Survey_2014-2015\UKDA-8128-tab')
#        data_dictionary_directory=os.path.join(base_dir,r'mrdoc\allissue')
#        directory=os.fsencode(data_dictionary_directory)
#        for file in os.listdir(directory):
#            filename = os.fsdecode(file)
#            if filename.endswith(".rtf"): 
#                #print(filename)
#                dd=ukds.DataDictionary()
#                dd.read_rtf(os.path.join(data_dictionary_directory,filename))
#    
#    def test_to_rdf_data_cube(self):
#        
#        filename='uktus15_household_ukda_data_dictionary.rtf'
#        dd=ukds.DataDictionary(os.path.join(data_dictionary_directory,filename))
#        c=dd.to_rdf_data_cube(base_prefix='ukds8128',
#                              base_uri='<http://www.purl.org/berg/ukds8128/>',
#                              dimension_variables=['serial']
#                              #dimension_property_uri='<http://www.purl.org/berg/ukds8128/dimension_property/household>',
#                              #dimension_property_concept_uri='<http://www.purl.org/berg/ukds8128/dimension_concept/Household>'
#                              )
#        #print(c.serialize())
#    
#    
#    
#    def test_to_rdf_bdo_characteristic(self):
#        
#        filename='uktus15_household_ukda_data_dictionary.rtf'
#        dd=ukds.DataDictionary(os.path.join(data_dictionary_directory,filename))
#        st=dd.to_rdf_bdo_characteristic(base_prefix='household',
#                        base_uri='http://www.purl.org/berg/ukds8128/uktus15_household/',
#                        variable_name='HhOut'
#                        )
#        print(st)
#        
#    def test_to_rdf_bdo_category_set(self):
#        
#        filename='uktus15_household_ukda_data_dictionary.rtf'
#        dd=ukds.DataDictionary(os.path.join(data_dictionary_directory,filename))
#        st=dd.to_rdf_bdo_category_set(base_prefix='household',
#                        base_uri='http://www.purl.org/berg/ukds8128/uktus15_household/',
#                        variable_name='strata'
#                        )
#        #print(st)
#        
#    def test_to_rdf_bdo_category(self):
#        
#        filename='uktus15_household_ukda_data_dictionary.rtf'
#        dd=ukds.DataDictionary(os.path.join(data_dictionary_directory,filename))
#        st=dd.to_rdf_bdo_category(base_prefix='household',
#                        base_uri='http://www.purl.org/berg/ukds8128/uktus15_household/',
#                        variable_name='strata',
#                        value=-2.0
#                        )
#        #print(st)
    
if __name__=='__main__':
    
    filename='uktus15_household_ukda_data_dictionary.rtf'
    dd=ukds.DataDictionary(os.path.join(data_dictionary_directory,filename))
    o=unittest.main(Test_data_dictionary())    
    
    
    