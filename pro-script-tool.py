from arcgis_pro_publish.publish import publish
from arcgis_pro_publish.share import share_unshared_items

from sys import argv
import arcpy

import sys
_stdout = sys.stdout

class ArcPyStream(object):
    def write(self, s):
        print(str(s))
sys.stdout = ArcPyStream()

def parse_bool(bool_val):
    if bool_val == 'true':
        return True
    return False

# 'D:\\tools\\pro-publishing\\pro-script-tool.py',
# 'inspections_survey',
# 'C:\\Users\\groemhildt\\Documents\\ArcGIS\\Projects\\Pipeline2019Migration\\groemhildt@services.wsbeng.com_6443.ags',
# 'inspections_survey',
# 'wsb',
# 'true',
# 'Map,Query,Data',
# 'false',
# 'true'
if __name__ == '__main__':
    
    map_name, server, service_name, \
        folder, feature_access, \
        feature_capabilities, schema_locks, \
        overwrite, instance_count = argv[1:]

    # convert args
    feature_access = parse_bool(feature_access)
    schema_locks = parse_bool(schema_locks)
    overwrite = parse_bool(overwrite)
    
    instance_count = int(instance_count)
    
    
    publish(
        map_name,
        server,
        service_name,
        folder,
        schema_locks,
        overwrite,
        feature_access,
        feature_capabilities,
        instance_count)

    print('Publishing Completed!')
    print('Tool is now sharing newly published items to ArcGIS Online')
	
    try:
        share_unshared_items()
    except Exception as e:
        arcpy.AddWarning('An error occurred while sharing items.')
        arcpy.AddWarning(e)

# NOT USED -> 
# copy of tool validation just in case something wonky happens in pro tools
class ToolValidator(object):
    """Class for validating a tool's parameter values and controlling
    the behavior of the tool's dialog."""

    def __init__(self):
        """Setup arcpy and the list of tool parameters.""" 
        self.params = arcpy.GetParameterInfo()

    def initializeParameters(self): 
        """Refine the properties of a tool's parameters. This method is 
        called when the tool is opened."""

    def updateParameters(self):
        """Modify the values and properties of parameters before internal
        validation is performed. This method is called whenever a parameter
        has been changed."""
        
        # set service name if map name exists and not service name
        if not self.params[0].altered:
            self.params[2].value = str(self.params[0].value)
                
        # disable feature access if feature access not selected
        self.params[5].enabled = self.params[4].value
        
        if not self.params[9].value:
            self.params[8].value = 0
            self.params[8].enabled = False
        else:
            if not self.params[8].value:
                self.params[8].value = 1
            self.params[8].enabled = True

    def updateMessages(self):
        """Modify the messages created by internal validation for each tool
        parameter. This method is called after internal validation."""
