# -*- coding: utf-8 -*-

#import rdflib
#from rdflib.namespace import RDF
import os
import fairly

class DataDictionary(): 
    """A class for reading a UK Data Service .rtf data dictionary file
    """
    
    def __init__(self,fp=None):
        """
        
        Arguments:
            fp (str): a filepath to a UK Data Service .rtf data dictionary file
        
        """
        
        if fp: self.read_rtf(fp)


    def variable_dicts(self):
        """Returns a list which contains the information in a UK Data Service .rtf data dictionary file.
        
        Returns:
            - (list): a list of dictionaries. Each dictionary has the following items: 
                 {'pos': ... ,
                  'variable': ... ,
                  'variable_label': ... ,
                  'variable_type': ... ,
                  'SPSS_measurement_level': ... ,
                  'SPSS_user_missing_values': ... ,
                  'value_labels': ... }
        
        """
        
        def get_variable_text(rtf_file):
            "Returns a list of variable_texts for each variable"
            st='Pos. = '
            return rtf_file.split(st)[1:]
            
        def get_variable_name(variable_text):
            st='Variable = '
            b=variable_text.split(st)[1]
            return b[b.find(' ')+1:b.find('\t')]
        
        def find_pos(rtf):
            a=rtf
            b=a
            return b[b.find(' ')+1:b.find('\t')]
        
        def find_variable_label(rtf):
            try:
                a=rtf
                b=a.split('Variable label = ')[1]
                return b[b.find(' ')+1:b.find('\\par')]
            except IndexError:
                return None
        
        def find_variable_type(rtf):
            if not 'This variable is  ' in rtf: return ''
            a=rtf
            b=a.split('This variable is  ')[1]
            i1=b.find(' ')+1
            i2=i1+b[i1:].find('}')
            return b[i1:i2]
        
        def find_SPSS_measurement_level(rtf):
            if not 'the SPSS measurement level is ' in rtf: return ''
            a=rtf
            b=a.split('the SPSS measurement level is ')[1]
            i1=b.find(' ')+1
            i2=i1+b[i1:].find('\\par')
            return b[i1:i2]
        
        def find_SPSS_user_missing_values(rtf):
            if not 'SPSS user missing values = ' in rtf: return dict()
            a=rtf
            d=a.split('SPSS user missing values = ')
            if len(d)<2: return None
            e=d[1]
            i1=e.find(' ')+1
            i2=i1+e[i1:].find('\\par')
            f=e[i1:i2]
            g=f.split(' ')
            i=' '.join([g[0],g[2],g[4]])
            return i
        
        def find_value_labels(rtf):
            if not 'Value = ' in rtf: return dict()
            a=rtf
            d=a.split('Value = ')[1:]
            z={}
            for e in d:
                value=e[e.find(' ')+1:e.find('\t')]
                value=float(value)
                f=e.split('Label = ')[1]
                label=f[f.find(' ')+1:f.find('\\par')]
                z[value]=label
            #print(z)
            return z
        
        variable_texts=get_variable_text(self.rtf)
        #pprint(variable_texts[0:2])
        
        result=[]
        for variable_text in variable_texts:
            d={'pos':find_pos(variable_text),
               'variable':get_variable_name(variable_text),
                'variable_label':find_variable_label(variable_text),
                'variable_type':find_variable_type(variable_text),
                'SPSS_measurement_level':find_SPSS_measurement_level(variable_text),
                'SPSS_user_missing_values':find_SPSS_user_missing_values(variable_text),
                'value_labels':find_value_labels(variable_text)                 
                }
            result.append(d)
            
        return result        
        

    def read_rtf(self,fp):
        """Reads a UK Data Service .rtf data dictionary file and creates the 'variable_list' attribute
            
        Arguments:
            fp (str): a filepath to a UK Data Service .rtf data dictionary file
    
        """
        with open (fp, "r", encoding="ANSI") as myfile:
            self.rtf=myfile.read()
        

    def variable_dict(self,variable):
        """Returns the dictionary for a variable
        
        Arguments:
            - variable (str): the name of the variable
            
        Returns:
            - (dict): A dictionary with the following items: 
                 {'pos': ... ,
                  'variable': ... ,
                  'variable_label': ... ,
                  'variable_type': ... ,
                  'SPSS_measurement_level': ... ,
                  'SPSS_user_missing_values': ... ,
                  'value_labels': ... }
        
        """
        return [x for x in self.variable_dicts() if x['variable']==variable][0]


    def variable_names(self):
        """Returns a list of all variable names
       
        Returns:
            - (list): A list of strings
        
        """
        
        return [x['variable'] for x in self.variable_dicts()]

#############
     
    def to_bso_variable(self,
                       base_prefix,
                       base_uri,
                       variable):
        """Returns a CreateRDF instance with variable info as bso rdf.
        """
        c=fairly.CreateRDF()
        c.add_prefix(base_prefix,base_uri)
        
        d=self.variable_dict(variable)
        #print(d)
        
        # variable
        variable_uri='%s:variable_%s' % (base_prefix,variable)
        c.add_subject_triples(variable_uri,[('a','bso:Variable'),
                                            ('rdfs:label','"%s"' % variable),
                                            ('rdfs:comment','"%s"' % d['variable_label'])
                                            ])
        
        #scale
        scale_uri='%s:scale_%s' % (base_prefix,variable)
        
        if d['SPSS_measurement_level']=="NOMINAL":
            scale_class='bso:NominalScale'
        else:
            scale_class='bso:Scale'
            
        c.add_triple(scale_uri,'a',scale_class)
        
        # categories    
        if d['SPSS_measurement_level']=="NOMINAL":
            for k,v in d['value_labels'].items():
                category_uri='%s:category_%s_%s' % (base_prefix,variable,k)
                c.add_triple(scale_uri,'bso:category',category_uri)
                concept_uri='%s:concept_%s_%s' % (base_prefix,variable,k)
                c.add_triple(category_uri,'bso:concept',concept_uri)
        
                
        # codes
        for k,v in d['value_labels'].items():
            code_uri='%s:code_%s_%s' % (base_prefix,variable,k)
            c.add_triple(variable_uri,'bso:code',code_uri)
            concept_uri='%s:concept_%s_%s' % (base_prefix,variable,k)
            c.add_subject_triples(code_uri,[('a','bso:Code'),
                                            ('bso:notation',k),
                                            ('bso:concept',concept_uri)])
            
        # concepts
        for k,v in d['value_labels'].items():
            concept_uri='%s:concept_%s_%s' % (base_prefix,variable,k)
            c.add_subject_triples(concept_uri,[('rdfs:label','"%s"' % v)])
    
        return c
    
    
    def to_bso(self,
               base_prefix,
               base_uri):
        
        c=fairly.CreateRDF()
        c.add_prefix(base_prefix,base_uri)
        
        
        survey_uri='%s:survey' % base_prefix
        c.add_triple(survey_uri,'a','bso:Survey')
        
        sample_uri='%s:sample' % base_prefix
        c.add_triple(sample_uri,'a','bso:Sample')
        c.add_triple(survey_uri,'bso:sample',sample_uri)
        
        for variable in self.variable_names():
            
            variable_uri='%s:variable_%s' % (base_prefix,variable)
            c.add_triple(survey_uri,'bso:variable',variable_uri)
            
            c1=self.to_bso_variable(base_prefix,
                                    base_uri,
                                    variable)
            c.rdf+=c1.rdf
        
        return c
    
    
    
    
    
#############


    def to_rdf_data_cube(self,
                         base_prefix,
                         base_uri,
                         dimension_variables,
                         #dimension_property_uri,
                         #dimension_property_concept_uri,
                         ):
        """Converts the data dictionary to RDF Data Cube format
        
        :param base_prefix str: the base prefix for the data cube
        :param base_uri str: the base uri for the data cube
        
        :return data_cube:
        :rtype fairly.CreateRDF
        
        """

        c=fairly.CreateRDF()
        c.add_data_cube_prefixes()
        c.add_skos_prefixes()
        c.add_prefix(base_prefix,base_uri)
        
        dataset_uri='%s:dataset' % base_prefix
        data_structure_definition_uri='%s:dsd' % base_prefix
        slice_key_uri='%s:sk' % base_prefix
        
        # add qb:DataSet
        c.add_data_cube_dataset(
                              dataset_uri,
                              title=None,
                              label=None,
                              description=None,
                              comment=None,
                              issued=None,
                              modified=None,
                              subject_uris=None,
                              publisher_uri=None,
                              license_uri=None,
                              data_structure_definition_uri=data_structure_definition_uri,
                              slice_uris=None,
                              component_specification_uris=None,
                              attribute_list=None,
                              predicate_object_list=None                              
                              )
        
        # add qb:DataStructureDefinition
        c.add_data_cube_data_structure_definition(
                                      data_structure_definition_uri,
                                      component_specification_uris=None,
                                      sliceKey_uris=None,
                                      predicate_object_list=None)
        
        
        
        
        # add qb:DimensionProperty
        for dimension_variable in dimension_variables:
            dimension_property_uri='%s:dp-%s' % (base_prefix,dimension_variable)
            c.add_data_cube_dimension_property(
                                   dimension_property_uri,
                                   label=None,
                                   subPropertyOf_uri=None,
                                   range_uri=None,
                                   concept_uri=None,
                                   code_list_uri=None,
                                   predicate_object_list=None)
            
            # add qb:ComponentSpecification - dimension
            dimension_component_specification_uri='%s:dcs-%s' % (base_prefix,dimension_variable)
            c.add_data_cube_dimension_component_specification(
                                                  dimension_component_specification_uri,
                                                  dimension_property_uri, 
                                                  order=1,
                                                  component_attachment_uri=None
                                                  )
            c.add_triple(data_structure_definition_uri,'qb:component',dimension_component_specification_uri)
        
        
        # add attributes
        attributes=['pos','variable','variable_label','variable_type',
                    'SPSS_measurement_level','SPSS_user_missing_values',
                    'value_labels']
        for attribute in attributes:
            
            attribute_property_uri='<http://www.purl.org/berg/ukds/attribute_property/%s>' % (attribute)
            attribute_component_specification_uri='%s:acs-%s' % (base_prefix,attribute)
            
            # add qb:AttributeProperty
            c.add_data_cube_attribute_property(
                                   attribute_property_uri,
                                   label='"%s"' % attribute,
                                   subPropertyOf_uri=None,
                                   range_uri=None,
                                   concept_uri=None,
                                   code_list_uri=None,
                                   predicate_object_list=None)
            
            # add qb:ComponentSpecification
            c.add_data_cube_attribute_component_specification(
                                              attribute_component_specification_uri,
                                              attribute_property_uri, 
                                              order=None,
                                              component_attachment_uri='qb:Slice',
                                              component_required=True,
                                              )
            c.add_triple(data_structure_definition_uri,'qb:component',attribute_component_specification_uri)
            
        # add qb:SliceKey
        c.add_data_cube_slice_key(
                            slice_key_uri,
                            componentProperty_uris=('qb:measureType',),
                            predicate_object_list=None
                            )
        c.add_triple(data_structure_definition_uri,'qb:sliceKey',slice_key_uri)
        
        
        # loop through variable
        for i,var_dict in enumerate(self.get_variable_list()):
            
            pos = var_dict['pos']
            variable = var_dict['variable']
            variable_label = var_dict['variable_label']
            variable_type = var_dict['variable_type']
            SPSS_measurement_level = var_dict['SPSS_measurement_level']
            SPSS_user_missing_values = var_dict['SPSS_user_missing_values']
            value_labels = var_dict['value_labels']
        
            measure_property_uri='%s:mp-%s' % (base_prefix,variable) 
            measure_component_specification_uri='%s:mcs-%s' % (base_prefix,variable) 
           
        
            # add qb:MeasureProperty
            c.add_data_cube_measure_property(
                             measure_property_uri,
                             label='"%s"' % variable,
                             subPropertyOf_uri=None,
                             range_uri=None,
                             concept_uri=None,
                             code_list_uri=None,
                             predicate_object_list=None)
        
            # add qb:ComponentSpecification
            c.add_data_cube_measure_component_specification(
                                            measure_component_specification_uri,
                                            measure_property_uri, 
                                            order=i+1,
                                            component_attachment_uri=None
                                            )
            c.add_triple(data_structure_definition_uri,'qb:component',measure_component_specification_uri)
        
            if value_labels:
        
                concept_scheme_uri='%s:concept_scheme-%s' % (base_prefix,variable)
                
                # add codeList link to skos:ConceptScheme
                c.add_triple(measure_property_uri, 'qb:codeList',concept_scheme_uri)
        
                # add skos:ConceptScheme
                c.add_skos_concept_scheme(
                         concept_scheme_uri,
                         prefLabel='"%s"' % variable,
                         label='"%s"' % variable,
                         notation='"%s"' % variable,
                         note='"%s"' % variable_label,
                         definition_uri='"%s"' % variable_label,
                         seeAlso_uri=None,
                         hasTopConcept_uris=None,
                         predicate_object_list=None
                         )
                
                for value,label in value_labels.items():
                    
                    concept_uri='%s:concept-%s-%s' % (base_prefix,variable,value)
                    
                    # add skos:hasTopConcept
                    c.add_triple(concept_scheme_uri, 'skos:hasTopConcept',concept_uri)
                    
                    # add skos:Concept
                    c.add_skos_concept(
                         concept_uri,
                         topConceptOf_uri=concept_scheme_uri,
                         prefLabel='"%s"' % label,
                         notation=value,
                         inScheme_uri=concept_scheme_uri,
                         predicate_object_list=None
                         )
        
            # add qb:Slice
            slice_uri='%s:slice-%s' % (base_prefix,variable)
            dimension_list=[('qb:measureType',measure_property_uri)]
            predicate_object_list=[]
            predicate_object_list.append(('<http://www.purl.org/berg/ukds/attribute_property/pos>',pos))
            predicate_object_list.append(('<http://www.purl.org/berg/ukds/attribute_property/variable>','"%s"' % variable))
            predicate_object_list.append(('<http://www.purl.org/berg/ukds/attribute_property/variable_label>','"%s"' % variable_label))
            predicate_object_list.append(('<http://www.purl.org/berg/ukds/attribute_property/variable_type>','"%s"' % variable_type))
            predicate_object_list.append(('<http://www.purl.org/berg/ukds/attribute_property/SPSS_measurement_level>','"%s"' % SPSS_measurement_level))
            predicate_object_list.append(('<http://www.purl.org/berg/ukds/attribute_property/SPSS_user_missing_values>',
                                          '"%s"' % str(SPSS_user_missing_values if SPSS_user_missing_values else '[]')))
            predicate_object_list.append(('<http://www.purl.org/berg/ukds/attribute_property/value_labels>',
                                          '"""%s"""' % str(value_labels if value_labels else '{}')))
            c.add_data_cube_slice(
                             slice_uri,
                             sliceStructure_uri=slice_key_uri,
                             dimension_list=dimension_list,
                             observation_uris=None,
                             predicate_object_list=predicate_object_list)
            c.add_triple(dataset_uri, 'qb:slice',slice_uri)
            
            #break
            #if variable=='strata': break
        
        return c


### bdo - BERG Data Ontology

    def to_rdf_bdo_variable_set(self,
                                base_prefix,
                                base_uri,
                                member_variables=None
                                ):
        """Creates the rdf for a bdo:VariableSet
        
        :param base_prefix str: the base prefix 
        :param base_uri str: the base uri 
        :param member_variables list: list of variable names
            - member triples are added for each variable in the list
            - if None, then no member triples are added
          
        :return c: the rdf
        :rtype fairly.CreateRDF:
        
        """

        c=fairly.CreateRDF()
        c.add_bdo_prefixes()
        c.add_skos_prefixes()
        c.add_prefix(base_prefix,base_uri)
        
        variable_set_uri='%s:variable_set' % base_prefix
        if member_variables:
            member_uri_list=['%s:variable_%s' % (base_prefix,var_name) 
                       for var_name in member_variables]
        else:
            member_uri_list=None
                            
        c.add_bdo_variable_set(
                             uri=variable_set_uri,
                             label=None,
                             comment=None,
                             member_uri_list=member_uri_list,
                             predicate_object_list=None
                             )
        
        return c
        
        
    def to_rdf_bdo_variable(self,
                   base_prefix,
                   base_uri,
                   variable_name,
                   characteristic_uri='default'
                   ):
        """Creates the rdf for a bdo:Variable
        
        :param base_prefix str: the base prefix 
        :param base_uri str: the base uri 
        :param variable_name str: the variable name
        :param characteristic_uri str: the characteristic uri
            - if None, then this is not added
          
        :return c: the rdf
        :rtype fairly.CreateRDF:
        
        """
        c=fairly.CreateRDF()
        c.add_bdo_prefixes()
        c.add_prefix(base_prefix,base_uri)
        
        var_dict=self.get_variable_dict(variable_name)
        variable = var_dict['variable']
        variable_label = var_dict['variable_label']
                
        uri='%s:variable_%s' % (base_prefix,variable_name)
        if characteristic_uri=='default':
            characteristic_uri='%s:characteristic_%s' % (base_prefix,variable_name)
        c.add_bdo_variable(
                         uri,
                         label='"%s"' % variable,
                         comment='"%s"' % variable_label,
                         characteristic_uri=characteristic_uri,
                         predicate_object_list=None
                         )

        return c
    
    
    def to_rdf_bdo_characteristic(self,
                   base_prefix,
                   base_uri,
                   variable_name,
                   add_category_set=False,
                   add_categories=False
                   ):
        """Creates the rdf for a bdo:Variable
        
        :param base_prefix str: the base prefix 
        :param base_uri str: the base uri 
        :param variable_name str: the variable name
        :param add_category_set bool: if True, the bdo:CategorySet is added
        :param add_categories bool: if True, the categories are added        
          
        :return c: the rdf
        :rtype fairly.CreateRDF:
        
        """
        c=fairly.CreateRDF()
        c.add_bdo_prefixes()
        c.add_prefix(base_prefix,base_uri)
        
        var_dict=self.get_variable_dict(variable_name)
        SPSS_measurement_level = var_dict['SPSS_measurement_level']
        value_labels = var_dict['value_labels']
        
        
        uri='%s:characteristic_%s' % (base_prefix,variable_name)
        if value_labels:
            category_set_uri='%s:category_set_%s' % (base_prefix,variable_name)
        else:
            category_set_uri=None
        
        if SPSS_measurement_level=='SCALE':
            characteristic_subclass_uri=None
            scale_subclass_uri=None
            #characteristic_subclass_uri='bdo:ContinuousCharacteristic'
            #scale_subclass_uri='bdo:RatioScale'
        elif SPSS_measurement_level=='NOMINAL':
            characteristic_subclass_uri='bdo:DiscreteCharacteristic'
            scale_subclass_uri='bdo:NominalScale'
        else:
            characteristic_subclass_uri=None
            scale_subclass_uri=None
        
        c.add_bdo_characteristic(
                               uri,
                               characteristic_subclass_uri=characteristic_subclass_uri,
                               scale_subclass_uri=scale_subclass_uri,
                               label=None,
                               comment=None,
                               category_set_uri=category_set_uri,
                               predicate_object_list=None
                               )

        if add_category_set:
            if category_set_uri:
                result=self.to_rdf_bdo_category_set(base_prefix,
                                                    base_uri,
                                                    variable_name,
                                                    add_categories=add_categories
                                                    )
                c.rdf+=result.rdf

        return c


    def to_rdf_bdo_category_set(self,
                   base_prefix,
                   base_uri,
                   variable_name,
                   add_categories=False
                   ):
        """Creates the rdf for a bdo:CategorySet
        
        :param base_prefix str: the base prefix 
        :param base_uri str: the base uri 
        :param variable_name str: the variable name

          
        :return c: the rdf
        :rtype fairly.CreateRDF:
        
        """
        c=fairly.CreateRDF()
        c.add_bdo_prefixes()
        c.add_prefix(base_prefix,base_uri)
        
        var_dict=self.get_variable_dict(variable_name)
        value_labels = var_dict['value_labels']
        
        uri='%s:category_set_%s' % (base_prefix,variable_name)
        member_uri_list=['%s:category_set_%s' % (base_prefix,x)
                         for x in value_labels.keys()]
        
        c.add_bdo_category_set(
                             uri,
                             label=None,
                             comment=None,
                             member_uri_list=member_uri_list,
                             predicate_object_list=None
                             )

        if add_categories:
            for value in value_labels.keys():
                result=self.to_rdf_bdo_category(base_prefix,
                                                base_uri,
                                                variable_name,
                                                value
                                                )
                c.rdf+=result.rdf

        return c
    
    
    def to_rdf_bdo_category(self,
                   base_prefix,
                   base_uri,
                   variable_name,
                   value
                   ):
        """Creates the rdf for a bdo:Category
        
        :param base_prefix str: the base prefix 
        :param base_uri str: the base uri 
        :param variable_name str: the variable name
        :param value float: the value of the value_label
                  
        :return c: the rdf
        :rtype fairly.CreateRDF:
        
        """
        c=fairly.CreateRDF()
        c.add_bdo_prefixes()
        c.add_prefix(base_prefix,base_uri)
        
        var_dict=self.get_variable_dict(variable_name)
        value_labels = var_dict['value_labels']
        label=value_labels[value]
        
        uri='%s:category_set_%s' % (base_prefix,value)
                                 
        c.add_bdo_category(
                         uri,
                         label='"%s"' % label,
                         comment=None,
                         order=None,
                         code=value,
                         concept_uri=None,
                         predicate_object_list=None
                         )

        return c
    

    ################


    def to_rdf(self,graph,prefix,uri):
        """Places the DataDictionary data in an rdflib Graph.
        
        Arguments:
            - graph (rdflib.Graph): a graph to place the data in
            - prefix (str): a prefix for the Data Dictionary ontology
            - uri (str): a uri for the Data Dictionary ontology
        
        Returns:
            - (rdflib.Graph): the input graph with the DataDictionary data inserted into it.
            
        """
        
        def add_variable_list_data(pos,
                                   variable,
                                   variable_label,
                                   variable_type,
                                   SPSS_measurement_level,
                                   SPSS_user_missing_values,
                                   value_labels):
            "Adds the data from a variable_list variable to the RDFlib graph"
    
            graph.add((dd_namespace[variable],RDF.type,RDF.Property))
            graph.add((dd_namespace[variable],ukds_namespace.pos,rdflib.Literal(int(pos))))
            graph.add((dd_namespace[variable],ukds_namespace.variable,rdflib.Literal(variable)))
            graph.add((dd_namespace[variable],ukds_namespace.variable_label,rdflib.Literal(variable_label)))
            graph.add((dd_namespace[variable],ukds_namespace.variable_type,rdflib.Literal(variable_type)))
            graph.add((dd_namespace[variable],ukds_namespace.SPSS_measurement_level,rdflib.Literal(SPSS_measurement_level)))
    
            if SPSS_user_missing_values:
                for x in SPSS_user_missing_values.split(','):
                    graph.add((dd_namespace[variable],ukds_namespace.SPSS_user_missing_values,rdflib.Literal(x)))
    
            if value_labels:
                for k,v in value_labels.items():
                    a=rdflib.BNode()
                    graph.add((dd_namespace[variable],ukds_namespace.value_labels,a))
                    graph.add((a,ukds_namespace.label,rdflib.Literal(v)))
                    graph.add((a,ukds_namespace.value,rdflib.Literal(str(k))))
        
        
        dd_namespace=rdflib.Namespace(uri)
        graph.bind(prefix,dd_namespace)
        ukds_namespace=rdflib.Namespace(r'http://purl.org/berg/ontology/UKDS/')
        graph.bind('ukds',ukds_namespace)
        
        for x in self.variable_list:
            add_variable_list_data(**x)
        
        return graph
    
    
#    def to_ttl(self,filename,prefix,uri):
#        """Places the DataDictionary data in an rdflib Graph.
#        
#        Arguments:
#            - filename (str): the name of the output .ttl file
#            - prefix (str): a prefix for the Data Dictionary ontology
#            - uri (str): a uri for the Data Dictionary ontology
#            
#        """
#        def write_variable_list_data(file,
#                                     prefix,
#                                     pos,
#                                     variable,
#                                     variable_label,
#                                     variable_type,
#                                     SPSS_measurement_level,
#                                     SPSS_user_missing_values,
#                                     value_labels):
#            """Writes the data from a variable_list variable to the file
#    
#            """
#    
#            l=[]
#            l.append('%s:%s a rdf:Property' % (prefix,variable))
#            l.append('ukds:pos %s' % pos)
#            l.append('ukds:variable "%s"' % variable)
#            l.append('ukds:variable_label "%s"' % variable_label)
#            l.append('ukds:variable_type "%s"' % variable_type)
#            l.append('ukds:SPSS_measurement_level "%s"' % SPSS_measurement_level)
#    
#            if SPSS_user_missing_values:
#                l1=[]
#                for x in SPSS_user_missing_values.split(','):
#                    l1.append('"%s"' % x)
#                l.append('ukds:SPSS_user_missing_values %s' % ' ,\t\t'.join(l1))
#    
#            if value_labels:
#                l2=[]
#                for k,v in value_labels.items():
#                    l2.append('[ ukds:label "%s" ; ukds:value "%s" ]' % (v,k))
#                l.append('ukds:value_labels %s' % ' ,\n\t\t'.join(l2))
#    
#            file.write(' ;\n\t'.join(l)+' .')
#    
#        
#        
#        
#        with open(filename,'w',encoding="UTF-8") as file:
#            file.write('@prefix %s: <%s> .\n' % (prefix,uri))
#            file.write('@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .\n')
#            file.write('@prefix ukds: <http://purl.org/berg/ontology/UKDS/> .\n')
#            file.write('\n')
#        
#            for x in self.variable_list:
#                write_variable_list_data(file,prefix,**x)
#                file.write('\n')
#                
#        return
#


    def to_ttl(self,filename,prefix,uri):
        """Places the DataDictionary data in an rdflib Graph.
        
        Creates multiple files if size > 30 MB
        
        Arguments:
            - filename (str): the name of the output .ttl file WITH EXTENSION
            - prefix (str): a prefix for the Data Dictionary ontology
            - uri (str): a uri for the Data Dictionary ontology
            
        """
        def write_variable_list_data(file,
                                     prefix,
                                     pos,
                                     variable,
                                     variable_label,
                                     variable_type,
                                     SPSS_measurement_level,
                                     SPSS_user_missing_values,
                                     value_labels):
            """Writes the data from a variable_list variable to the file
    
            """
    
            l=[]
            l.append('%s:%s a rdf:Property' % (prefix,variable))
            l.append('ukds:pos %s' % pos)
            l.append('ukds:variable "%s"' % variable)
            l.append('ukds:variable_label "%s"' % variable_label)
            l.append('ukds:variable_type "%s"' % variable_type)
            l.append('ukds:SPSS_measurement_level "%s"' % SPSS_measurement_level)
    
            if SPSS_user_missing_values:
                l1=[]
                for x in SPSS_user_missing_values.split(','):
                    l1.append('"%s"' % x)
                l.append('ukds:SPSS_user_missing_values %s' % ' ,\t\t'.join(l1))
    
            if value_labels:
                l2=[]
                for k,v in value_labels.items():
                    l2.append('[ ukds:label "%s" ; ukds:value "%s" ]' % (v,k))
                l.append('ukds:value_labels %s' % ' ,\n\t\t'.join(l2))
    
            file.write(' ;\n\t'.join(l)+' .\n\n')
    
        with open(filename,'w',encoding="UTF-8") as file:
            file.write('@prefix %s: <%s> .\n' % (prefix,uri))
            file.write('@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .\n')
            file.write('@prefix ukds: <http://purl.org/berg/ontology/UKDS/> .\n')
            file.write('\n')    
    
        for x in self.variable_list:
            
            write_variable_list_data(file,prefix,**x)
    
#        file_index=0
#        i=iter(self.variable_list)
#        index=0
#        
#        while True:
#            
#            with open(filename+'_'+str(file_index)+'.ttl','w',encoding="UTF-8") as file:
#                file.write('@prefix %s: <%s> .\n' % (prefix,uri))
#                file.write('@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .\n')
#                file.write('@prefix ukds: <http://purl.org/berg/ontology/UKDS/> .\n')
#                file.write('\n')
#    
#                while True: 
#    
#                    try:
#                        x = next(i)
#                    except StopIteration:
#                        return
#                
#                    write_variable_list_data(file,prefix,**x)
#                    
#                    if index%250==0:
#                        filesize_mb=os.path.getsize(filename+'_'+str(file_index)+'.ttl')/(1024*1024.0)
#                        if filesize_mb>10000:
#                            file_index+=1
#                            break
#                            
#                    index+=1
        return
    








