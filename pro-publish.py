import arcpy
from os.path import join
from xml.dom.minidom import parse, parseString

output = 'C:/tmp'
default_server = 'C:/ArcGISConnections/groemhildt@dev.gis.wsbeng.com.ags'
server_url = 'https://dev.gis.wsbeng.com/arcgis/'

arcpy.env.overwriteOutput = True

def write_xml(sddraft_path, doc):
    f = open(sddraft_path, 'w')
    doc.writexml(f)
    f.close()

def read_xml(sddraft_path):
    # Read the contents of the original SDDraft into an xml parser
    doc = parse(sddraft_path)
    return doc

def disable_locking(doc):
    # search for and replace the schema locking key
    keyTags = doc.getElementsByTagName('Key')
    for keyTag in keyTags:
            if keyTag.firstChild.data == 'schemaLockingEnabled':
                    keyTag.nextSibling.firstChild.data = 'false'
	
	
def enable_overwrite(doc):
    stateTags = doc.getElementsByTagName('State')
    for stateTag in stateTags:
        if stateTag.firstChild.data == 'esriSDState_Draft':
            stateTag.firstChild.data = 'esriSDState_Published'
            
    typeTags = doc.getElementsByTagName('Type')
    for typeTag in typeTags:
            if typeTag.firstChild.data == 'esriServiceDefinitionType_New':
                    typeTag.firstChild.data = 'esriServiceDefinitionType_Replacement'
    

def enable_feature_access(doc, capabilities):

    # The follow code piece modifies the SDDraft from a new MapService with caching capabilities
    # to a FeatureService with Map, Create and Query capabilities.
    typeNames = doc.getElementsByTagName('TypeName')
    for typeName in typeNames:
        if typeName.firstChild.data == "FeatureServer":
            extention = typeName.parentNode
            for extElement in extention.childNodes:
                if extElement.tagName == 'Enabled':
                    extElement.firstChild.data = 'true'

    # Turn off caching
    configProps = doc.getElementsByTagName('ConfigurationProperties')[0]
    propArray = configProps.firstChild
    propSets = propArray.childNodes
    for propSet in propSets:
        keyValues = propSet.childNodes
        for keyValue in keyValues:
            if keyValue.tagName == 'Key':
                if keyValue.firstChild.data == "isCached":
                    keyValue.nextSibling.firstChild.data = "false"

    # turn on feature access capabilities
    configProps = doc.getElementsByTagName('Info')[0]
    propArray = configProps.firstChild
    propSets = propArray.childNodes
    for propSet in propSets:
        keyValues = propSet.childNodes
        for keyValue in keyValues:
            if keyValue.tagName == 'Key':
                if keyValue.firstChild.data == "WebCapabilities":
                    keyValue.nextSibling.firstChild.data = capabilities

"""
Publish a arcgis pro service
    service_name - The name of the service
    project - The path to the project file to pull the map from.
        Default is 'CURRENT'
    server_type - Default is STANDALONE_SERVER (leave this)
    service_type - Default is MAP_SERVICE (leave this)
    server - ArcGIS Server connection file path
    folder - Folder to publish to on ArcGIS Server
    feature_access - Set True to enable feature access
    feature_capabilities - Capabilities (comma separated string) to enable
    schema_locks - True of False to toggle schema locks
	overwrite - whether we should overwrite an existing service (service must exist)
"""
def publish(map_name,
            service_name = None, 
            project='CURRENT',
            server_type='STANDALONE_SERVER',
            service_type='MAP_SERVICE',
            server=default_server,
            folder = None,
            feature_access = False,
            feature_capabilities = 'Map,Query,Data',
            schema_locks = False,
			overwrite = False):
    
    if not service_name:
        service_name = map_name
    
    # get the map
    sddraft_filename = f'{service_name}.sddraft'
    sddraft_output_filename = join(output, sddraft_filename)
    pro = arcpy.mp.ArcGISProject(project)
    mp = pro.listMaps(map_name)
    
    if not len(mp):
        arcpy.AddError(f'could not locate map {map_name} in project {project}')
        return
    mp = mp[0]

    # create service draft and export to draft file
    arcpy.AddMessage('Creating service draft...')
    service_draft = arcpy.sharing.CreateSharingDraft(
        server_type,
        service_type,
        service_name,
        mp)
    service_draft.targetServer = server
    # set folder if necessary
    if folder:
        service_draft.serverFolder = folder
        
    service_draft.exportToSDDraft(sddraft_output_filename)

    # open the xml for potential modifications
    doc = read_xml(sddraft_output_filename)

    # enable feature service?
    if feature_access:
        enable_feature_access(doc, feature_capabilities)

    if not schema_locks:
        disable_locking(doc)
	
        if overwrite:
            enable_overwrite(doc)

    # save the modified xml
    write_xml(sddraft_output_filename, doc)

    # stage service
    arcpy.AddMessage('Staging service...')
    sd_filename = f"{service_name}.sd"
    sd_output_filename = join(output, sd_filename)
    arcpy.StageService_server(sddraft_output_filename, sd_output_filename)

    # share to server
    arcpy.UploadServiceDefinition_server(sd_output_filename, server)
    arcpy.AddMessage(f'Successfully published service {service_name} to {server}')
