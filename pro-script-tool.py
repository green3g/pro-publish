from publishing.publish import publish
from sys import argv
import arcpy
#from argparse import ArgumentParser
#
#parser = ArgumentParser(description = 'Publish an arcgis pro map to a arcgis server')


if __name__ == '__main__':
    arcpy.AddMessage(argv)
    map_name, server, service_name, folder, feature_access, \
          feature_capabilities, schema_locks, overwrite, instance_count = argv[1:]
    
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

