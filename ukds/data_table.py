# -*- coding: utf-8 -*-

import pandas as pd
from .data_dictionary import DataDictionary
import rdflib
import os
import fairly


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
        
        This stored as a DataFrame with columns of strings
        
        Arguments:
            fp_tab (str): a filepath to a UK Data Service .tab data table file
        
        """
        self.tab=pd.read_csv(fp_tab,
                             sep='\t',
                             skipinitialspace=True,
                             #dtype=str,
                             low_memory=False,
                             na_filter=False,
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
            
            new_values=pd.to_numeric(df[col],errors='coerce').dropna().replace(value_labels)
            df.loc[new_values.index,col]=new_values
    
        return df
        
    
    def to_bso_survey(self,
                      base_prefix,
                      base_uri):
        """
        """
        c=fairly.CreateRDF()
        c.add_prefix(base_prefix,base_uri)
        
        
        survey_uri='%s:survey' % base_prefix
        sample_uri='%s:sample' % base_prefix
        c.add_subject_triples(survey_uri,[('a','bso:Survey'),
                                          ('bso:sample',sample_uri)])
        c.add_triple(sample_uri,'a','bso:Sample')
        
        l=[]
        for i in range(len(self.tab)):
            observation_uri='%s:observation_%s' % (base_prefix,str(i))
            l.append(observation_uri)
        c.add_subject_predicate_triples(survey_uri,'bso:observation',l)
    
        return c
    
    
    def to_bso_variable(self,
                       base_prefix,
                       base_uri,
                       variable):
        """
        """
        c=fairly.CreateRDF()
        c.add_prefix(base_prefix,base_uri)
        
        variable_uri='%s:variable_%s' % (base_prefix,variable)
        value_uri='%s:value_%s' % (base_prefix,variable)
        
        c.add_subject_triples(value_uri,[('rdfs:subPropertyOf','bso:value'),
                                        ('rdfs:seeAlso',variable_uri)
                                        ])
        
        variable_dict=self.datadictionary.variable_dict(variable)
        value_labels=variable_dict['value_labels']
        #print(value_labels)
        
        for i,v in enumerate(self.tab[variable].values):
            
            observation_uri='%s:observation_%s' % (base_prefix,str(i))
            
            try:                
                if float(v) in value_labels:
                    code_uri='%s:code_%s_%s' % (base_prefix,variable,float(v))
                    c.add_triple(observation_uri,value_uri,code_uri)
                else:
                    c.add_triple(observation_uri,value_uri,v)
            except ValueError:
                c.add_triple(observation_uri,value_uri,'"%s"' % v)
        
        
        return c
    
    
    def to_rdf_data_cube(self,
                         base_prefix,
                         base_uri,
                         dimension_columns,
                         column=None
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
        
        x=[]
        d=self.tab[[*dimension_columns]].to_dict()
        for k,v in d.items():
            dimension_property_uri='%s:dp-%s' % (base_prefix,k)
            x.append([(dimension_property_uri,value) for value in v.values()])
        dimension_lists=list(zip(*x))
        
        
#        for index,row in self.tab[[*dimension_columns]].iterrows():
#            l=[]
#            for col in row.index:
#                l.append(('%s:dp-%s' % (base_prefix,col),row[col]))
#            dimension_lists.append(l)
        
        columns=[column] if column else self.tab.columns
        
        for col in columns:
            
            df=self.tab[col]
            variable_type=self.datadictionary.get_variable_dict(col)['variable_type']
            
            measure_property_uri='%s:mp-%s' % (base_prefix,col)
            slice_uri='%s:slice-%s' % (base_prefix,col)
            
            for index,value in df.iteritems():
                
                # add qb:Observation
                observation_uri='%s:obs-%s-%s' % (base_prefix,col,str(index))
                dimension_list=dimension_lists[index]
                measure_list=[(measure_property_uri,value if variable_type=='numeric' else '"%s"' % value)]
                c.add_data_cube_observation(
                        observation_uri,
                        dataset_uri=dataset_uri,
                        dimension_list=dimension_list,
                        measureType_uri=None,
                        measure_list=measure_list,
                        attribute_list=None)
                c.add_triple(slice_uri,'qb:observation',observation_uri)
    
        return c
    
### bdo - BERG Data Ontology
    
    def to_rdf_bdo_observation_datum(self,
                                     base_prefix,
                                     base_uri,
                                     column_name,
                                     row_index
                                     ):
        """Creates the rdf for a bdo:ObservationDatum
        
        :param base_prefix str: the prefix for the resource uri
            - e.g. 'eg'
        :param base_uri str: the base uri for the resource uri
            - e.g. 'https://www.example.org/'
        :param column_name str: the table column name
        :param row_index int: the table row index        
        
        :return c: the rdf
        :rtype fairly.CreateRDF:
        
        """
        
        c=fairly.CreateRDF()
        c.add_bdo_prefixes()
        c.add_prefix(base_prefix,base_uri)
        
        uri='%s:observation_datum_%s_%s' % (base_prefix,row_index,column_name)
        variable_uri='%s:variable_%s' % (base_prefix,column_name)
        observation_uri='%s:observation_%s' % (base_prefix,row_index)
        value=self.tab.loc[row_index,column_name]
        
        c.add_bdo_observation_datum(
                                  uri,
                                  label=None,
                                  comment=None,
                                  variable_uri=variable_uri,
                                  observation_uri=observation_uri,
                                  value=value,
                                  predicate_object_list=None
                                  )

        return c
    
    
    
    def to_rdf_bdo_observation_datums(self,
                                      base_prefix,
                                      base_uri,
                                      column_names,
                                      ):
        """Creates the rdf for a series of bdo:ObservationDatum resources
        
        :param base_prefix str: the prefix for the resource uri
            - e.g. 'eg'
        :param base_uri str: the base uri for the resource uri
            - e.g. 'https://www.example.org/'
        :param column_names list: a list of column names to be created
          
        :return c: the rdf
        :rtype fairly.CreateRDF:
        
        """
        
        c=fairly.CreateRDF()
        c.add_bdo_prefixes()
        c.add_prefix(base_prefix,base_uri)
        
        for column_name in column_names:
            for row_index in self.tab.index:
                result=self.to_rdf_bdo_observation_datum(base_prefix,
                                                     base_uri,
                                                     column_name,
                                                     row_index
                                                     )
                c.rdf+=result.rdf

        return c
    

    
    def to_rdf_bdo_observation(self,
                               base_prefix,
                               base_uri,
                               row_index
                               ):
        """Creates the rdf for a bdo:Observation
        
        :param base_prefix str: the prefix for the resource uri
            - e.g. 'eg'
        :param base_uri str: the base uri for the resource uri
            - e.g. 'https://www.example.org/'
        :param row_index int: the table row index         
        
        :return c: the rdf
        :rtype fairly.CreateRDF:
        
        """
                
        c=fairly.CreateRDF()
        c.add_bdo_prefixes()
        c.add_prefix(base_prefix,base_uri)
        
        uri='%s:observation_%s' % (base_prefix,row_index)
                
        c.add_bdo_observation(
                            uri,
                            label=None,
                            comment=None,
                            entity_uri=None,
                            predicate_object_list=None
                            )

        return c
    
    def to_rdf_bdo_observation_set(self,
                                   base_prefix,
                                   base_uri,
                                   add_members=False
                                   ):
        """Creates the rdf for a bdo:ObservationSet
        
        :param base_prefix str: the prefix for the resource uri
            - e.g. 'eg'
        :param base_uri str: the base uri for the resource uri
            - e.g. 'https://www.example.org/'
        :param add_member bool: if True, the member triples are added         
        
        :return c: the rdf
        :rtype fairly.CreateRDF:
        
        """
        
        c=fairly.CreateRDF()
        c.add_bdo_prefixes()
        c.add_prefix(base_prefix,base_uri)
        
        uri='%s:observation_set' % (base_prefix)
        if add_members:
            member_uri_list=['%s:observation_%s' % (base_prefix,i) 
                             for i in self.tab.index]
        else:
            member_uri_list=[]
                
        c.add_bdo_observation_set(
                                uri,           
                                label=None,
                                comment=None,
                                member_uri_list=member_uri_list,
                                predicate_object_list=None
                                )

        return c
    
    def to_rdf_bdo_observation_data_set(self,
                                        base_prefix,
                                        base_uri,
                                        member_columns=None,
                                        ):
        """Creates the rdf for a bdo:ObservationDataSet
        
        :param base_prefix str: the prefix for the resource uri
            - e.g. 'eg'
        :param base_uri str: the base uri for the resource uri
            - e.g. 'https://www.example.org/'
        :param member_columns list: list of column names
            - member triples are added for each column in the list
            - if None, then no member triples are added
        
        :return c: the rdf
        :rtype fairly.CreateRDF:
        
        """
        
        c=fairly.CreateRDF()
        c.add_bdo_prefixes()
        c.add_prefix(base_prefix,base_uri)
        
        uri='%s:data_set' % (base_prefix)
        if member_columns:
            member_uri_list=['%s:observation_datum_%s_%s' % (base_prefix,i,column_name) 
                             for i in self.tab.index for column_name in member_columns]
        else:
            member_uri_list=None
        variable_set_uri='%s:variable_set' % base_prefix
        observation_set_uri='%s:observation_set' % (base_prefix)
        
        c.add_bdo_observation_data_set(
                                      uri,
                                      label=None,
                                      comment=None,
                                      member_uri_list=member_uri_list,
                                      variable_set_uri=variable_set_uri,
                                      observation_set_uri=observation_set_uri,
                                      predicate_object_list=None
                                      )

        return c
    
#    def add_data_cube_observations_by_table(self,
#                      createRDF,
#                      base_uri,
#                      row_dimension_property_suffix,
#                      row_dimension_value_function,
#                      include_pos=True,
#                      include_variable=True,
#                      include_variable_label=True,
#                      include_variable_type=True,
#                      include_SPSS_measurement_level=True,
#                      include_SPSS_user_missing_values=True,
#                      include_value_labels=True
#                      ):
#        """Adds a series of qb:Observation for the entire table
#        
#        :param createRDF fairly.CreateRDF: a fairly.CreateRDF instance
#        :param base_uri str: the base uri for the data table
#            e.g. 'http://purl.org/berg/ukds/8128/household/'
#        :param row_dimension_property_suffix: the qb:DimensionProperty suffix
#            e.g. 'household'
#        :param row_dimension_value_function func: a function to calculate the row_dimension_value
#            e.g. lambda df,index: df.loc[index,'serial']
#        :param include_pos bool: if True, this attribute is included
#        :param include_variable bool: if True, this attribute is included
#        :param include_variable_label bool: if True, this attribute is included
#        :param include_variable_type bool: if True, this attribute is included
#        :param include_SPSS_measurement_level bool: if True, this attribute is included 
#        :param include_SPSS_user_missing_values bool: if True, this attribute is included
#        :param include_value_labels bool: if True, this attribute is included
#        
#        """
#        for column_variable in self.tab.columns:
#            createRDF=self.add_data_cube_observations_by_column(
#                   createRDF=createRDF,
#                   base_uri=base_uri,
#                   column_variable=column_variable,
#                   row_dimension_property_suffix=row_dimension_property_suffix,
#                   row_dimension_value_function=row_dimension_value_function,
#                   include_pos=include_pos,
#                   include_variable=include_variable,
#                   include_variable_label=include_variable_label,
#                   include_variable_type=include_variable_type,
#                   include_SPSS_measurement_level=include_SPSS_measurement_level,
#                   include_SPSS_user_missing_values=include_SPSS_user_missing_values,
#                   include_value_labels=include_value_labels
#                   )
#        
#        return createRDF
#    
#    
#    def add_data_cube_observations_by_column(self,
#                                               createRDF,
#                                               base_uri,
#                                               column_variable,
#                                               row_dimension_property_suffix,
#                                               row_dimension_value_function,
#                                               include_pos=True,
#                                               include_variable=True,
#                                               include_variable_label=True,
#                                               include_variable_type=True,
#                                               include_SPSS_measurement_level=True,
#                                               include_SPSS_user_missing_values=True,
#                                               include_value_labels=True
#                                               ):
#        """Adds a series of qb:Observation based on a table column
#        
#        :param createRDF fairly.CreateRDF: a fairly.CreateRDF instance
#        :param base_uri str: the base uri for the data table
#            e.g. 'http://purl.org/berg/ukds/8128/household/'
#        :param column_variable str: the column variable
#            e.g. 'strata'
#        :param row_dimension_property_suffix: the qb:DimensionProperty suffix
#            e.g. 'household'
#        :param row_dimension_value_function func: a function to calculate the row_dimension_value
#            e.g. lambda df,index: df.loc[index,'serial']
#        :param include_pos bool: if True, this attribute is included
#        :param include_variable bool: if True, this attribute is included
#        :param include_variable_label bool: if True, this attribute is included
#        :param include_variable_type bool: if True, this attribute is included
#        :param include_SPSS_measurement_level bool: if True, this attribute is included 
#        :param include_SPSS_user_missing_values bool: if True, this attribute is included
#        :param include_value_labels bool: if True, this attribute is included
#        
#        """
#        
#        d=self.datadictionary.get_variable_dict(column_variable)
#        pos=d['pos'] if include_pos else None
#        variable=d['variable'] if include_variable else None
#        variable_label=d['variable_label'] if include_variable_label else None
#        variable_type=d['variable_type'] if include_variable_type else None
#        SPSS_measurement_level=d['SPSS_measurement_level'] if include_SPSS_measurement_level else None
#        SPSS_user_missing_values=True if include_SPSS_user_missing_values and d['SPSS_user_missing_values'] else False
#        value_labels=True if include_value_labels and d['value_labels'] else False
#    
#        s=self.tab[column_variable]
#        for index,cell_value in s.iteritems():
#            
#            createRDF=self.add_data_cube_observation(
#                    createRDF=createRDF,
#                    base_uri=base_uri,
#                    row=index,
#                    row_dimension_property_suffix=row_dimension_property_suffix,
#                    row_dimension_value=row_dimension_value_function(self.tab,index),
#                    column_variable=column_variable,
#                    cell_value=cell_value,
#                    pos=pos,
#                    variable=variable,
#                    variable_label=variable_label,
#                    variable_type=variable_type,
#                    SPSS_measurement_level=SPSS_measurement_level,
#                    SPSS_user_missing_values=SPSS_user_missing_values,
#                    value_labels=value_labels
#                    )
#    
#            #break
#    
#        return createRDF
#    
#    @staticmethod
#    def add_data_cube_observation(createRDF,
#                                  base_uri,
#                                  row,
#                                  row_dimension_property_suffix,
#                                  row_dimension_value,
#                                  column_variable,
#                                  cell_value,
#                                  pos=None,
#                                  variable=None,
#                                  variable_label=None,
#                                  variable_type=None,
#                                  SPSS_measurement_level=None,
#                                  SPSS_user_missing_values=False,
#                                  value_labels=False
#                                  ):
#        """Adds a qb:Observation based on a table cell
#        
#        :param createRDF fairly.CreateRDF: a fairly.CreateRDF instance
#        :param base_uri str: the base uri for the data table
#            e.g. 'http://purl.org/berg/ukds/8128/household/'
#        :param row int: the table row
#            e.g. 0
#        :param row_dimension_property_suffix: the qb:DimensionProperty suffix
#            e.g. 'household'
#        :param row_dimension_value str: the qb:DimensionProperty value
#            e.g. '11010903'
#        :param column_variable str: the column variable
#            e.g. 'strata'
#        :param cell_value str: the value of the observation
#        :param pos str: the value for the 'ukds-attribute:pos' qb:AttributeProperty
#        :param variable str: the value for the 'ukds-attribute:variable' qb:AttributeProperty
#        :param variable_label str: the value for the 'ukds-attribute:variable_label' qb:AttributeProperty
#        :param variable_type str: the value for the 'ukds-attribute:variable_type' qb:AttributeProperty
#        :param SPSS_measurement_level str: the value for the 'ukds-attribute:SPSS_measurement_level' qb:AttributeProperty
#        :param SPSS_user_missing_values bool: if True, this attribute is included 
#        :param value_labels bool: if True, this attribute is included
#        
#        :return createRDF: 
#        :rtype fairly.CreateRDF:
#        
#        --- example RDF ---
#        
#        <http://purl.org/berg/ukds/8128/uktus15_household/observation#0_strata>  a qb:Observation;
#            qb:dataSet <http://purl.org/berg/ukds/8128/uktus15_household/dataset>;
#            <http://purl.org/berg/ukds/8128/uktus15_household/dimension#household> 
#                <http://purl.org/berg/ukds/8128/uktus15_household/household#11010903>;
#            qb:measureType <http://purl.org/berg/ukds/8128/uktus15_household/measure#strata> ;
#            <http://purl.org/berg/ukds/8128/uktus15_household/measure#strata> "-2" ;
#            ukds-attribute:pos 2 ;
#            ukds-attribute:variable "strata" ;
#            ukds-attribute:variableLabel "Strata" ;
#            ukds-attribute:variableType ukds-code:variableType-numeric ;
#            ukds-attribute:SPSSMeasurementLevel ukds-code:SPSSMeasurementLevel-SCALE ;
#            ukds-attribute:SPSSUserMissingValues  <http://purl.org/berg/ukds/8128/uktus15_household/code#missingValues-strata> ;
#            ukds-attribute:valueLabels  <http://purl.org/berg/ukds/8128/uktus15_household/code#valueLabels-strata> ;
#            .
#        
#        --- end ---
#        
#        """
#        observation_uri='<%sobservation#%s_%s>' % (base_uri,str(row),column_variable)
#        dataset_uri='<%sdataset>' % base_uri
#        dimension_list=[('<%sdimension#%s>' % (base_uri,row_dimension_property_suffix),
#                         '<%s%s#%s>' % (base_uri,row_dimension_property_suffix,row_dimension_value))]
#        measureType_uri='<%smeasure#%s>' % (base_uri,column_variable)
#        measure_list=[('<%smeasure#%s>' % (base_uri,column_variable),'"%s"' % cell_value)]
#        attribute_list=[]
#        if pos: attribute_list.append(('ukds-attribute:pos',pos))
#        if variable: attribute_list.append(('ukds-attribute:variable','"%s"' % variable))
#        if variable_label: attribute_list.append(('ukds-attribute:variableLabel','"%s"' % variable_label))
#        if variable_type: attribute_list.append(('ukds-attribute:variableType','ukds-code:variableType-%s' % variable_type))
#        if SPSS_measurement_level: attribute_list.append(('ukds-attribute:SPSSMeasurementLevel','ukds-code:SPSSMeasurementLevel-%s' % SPSS_measurement_level))
#        if SPSS_user_missing_values: attribute_list.append(('ukds-attribute:SPSSUserMissingValues','<%scode#SPSSUserMissingValues-%s>' % (base_uri,column_variable)))
#        if value_labels: attribute_list.append(('ukds-attribute:value_labels','<%scode#ValueLabels-%s>' % (base_uri,column_variable)))
#        
#        createRDF.add_data_cube_observation(
#                        observation_uri,
#                        dataset_uri,
#                        dimension_list,
#                        measureType_uri,
#                        measure_list,
#                        attribute_list)
#    
#        return createRDF
#    
#    
#    
#    
#    
#    
#    
#    
#    
#    
#    
#    
#    
#    def to_rdf(self,graph,prefix,uri):
#        """Places the DataTable data in an rdflib Graph.
#        
#        Arguments:
#            - graph (rdflib.Graph): a graph to place the data in
#            - prefix (str): a prefix for the Data Dictionary ontology (used to describe the variables)
#            - uri (str): a uri for the Data Dictionary ontology (used to describe the variables)
#        
#        Returns:
#            - (rdflib.Graph): the input graph with the DataTable data inserted into it.
#            
#        """
#        
#        dd_namespace=rdflib.Namespace(uri)
#        graph.bind(prefix,dd_namespace)
#        
#        for index,row in self.tab.iterrows():
#            
#            data_dict=row.to_dict()
#            
#            a=rdflib.BNode()
#        
#            for k,v in data_dict.items():
#                graph.add((a,dd_namespace[k],rdflib.Literal(v)))
#                
#        return graph
#    
#    
#    def to_ttl(self,filename,prefix,uri):
#        """Places the DataTable data in an rdflib Graph.
#        
#        Arguments:
#            - filename (str): the name of the output .ttl file
#            - prefix (str): a prefix for the Data Dictionary ontology (used to describe the variables)
#            - uri (str): a uri for the Data Dictionary ontology (used to describe the variables)
#        
#        """
#        
#        with open(filename,'w',encoding="UTF-8") as file:
#            file.write('@prefix %s: <%s> .\n' % (prefix,uri))
#            file.write('\n')
#        
#            for index,row in self.tab.iterrows():
#    
#                data_dict=row.to_dict()
#    
#                l=[]
#                for k,v in data_dict.items():
#                    l.append('%s:%s "%s"' % (prefix,k,v))
#                
#                file.write('[] %s . \n\n' % ' ;\n\t'.join(l))
        

    def to_ttl(self,filename,prefix,uri):
        """Places the DataTable data in an rdflib Graph.
        
        Creates multiple files is size > 30 MB
        
        Arguments:
            - filename (str): the name of the output .ttl file 
            - prefix (str): a prefix for the Data Dictionary ontology (used to describe the variables)
            - uri (str): a uri for the Data Dictionary ontology (used to describe the variables)
        
        Returns:
            - (rdflib.Graph): the input graph with the DataTable data inserted into it.
            
        """
        
        with open(filename,'w',encoding="UTF-8") as file:
            file.write('@prefix %s: <%s> .\n' % (prefix,uri))
            file.write('\n')
        
            for index,row in self.tab.iterrows():
                data_dict=row.to_dict()
                l=[]
                for k,v in data_dict.items():
                    l.append('%s:%s "%s"' % (prefix,k,v))
                file.write('[] %s . \n\n' % ' ;\n\t'.join(l))
        
        
#        file_index=0
#        i=self.tab.iterrows()
#        
#        while True:
#            
#            with open(filename+'_'+str(file_index)+'.ttl','w',encoding="UTF-8") as file:
#                file.write('@prefix %s: <%s> .\n' % (prefix,uri))
#                file.write('\n')
#        
#                while True: 
#    
#                    try:
#                        index,row = next(i)
#                    except StopIteration:
#                        return
#                    
#                    data_dict=row.to_dict()
#    
#                    l=[]
#                    for k,v in data_dict.items():
#                        l.append('%s:%s "%s"' % (prefix,k,v))
#    
#                    file.write('[] %s . \n\n' % ' ;\n\t'.join(l))
#        
#                    if index%250==0:
#                        filesize_mb=os.path.getsize(filename+'_'+str(file_index)+'.ttl')/(1024*1024.0)
#                        if filesize_mb>10000:
#                            file_index+=1
#                            break
