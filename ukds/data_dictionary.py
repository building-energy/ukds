# -*- coding: utf-8 -*-

class DataDictionary(): 
    """A class for reading a UK Data Service .rtf data dictionary file
    """
    
    def __init__(self,fp=None):
        """
        
        Arguments:
            fp (str): a filepath to a UK Data Service .rtf data dictionary file
        
        """
        
        if fp: self.read_rtf(fp)


    def get_variable_list(self):
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
            a=rtf
            b=a.split('Variable label = ')[1]
            return b[b.find(' ')+1:b.find('\\par')]
        
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
            if not 'SPSS user missing values = ' in rtf: return ''
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
            if not 'Value = ' in rtf: return ''
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
        with open (fp, "r") as myfile:
            self.rtf=myfile.read()
        
        self.variable_list=self.get_variable_list()


    def get_variable_dict(self,variable):
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
        return [x for x in self.variable_list if x['variable']==variable][0]


    def get_variable_names(self):
        """Returns a list of all variable names
       
        Returns:
            - (list): A list of strings
        
        """
        
        return [x['variable'] for x in self.variable_list]



















