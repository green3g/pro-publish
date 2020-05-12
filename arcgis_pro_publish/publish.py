from arcpy import env, AddMessage, AddError, StageService_server, UploadServiceDefinition_server, Exists
from arcpy.sharing import CreateSharingDraft
from arcpy.mp import ArcGISProject
from os.path import join
from xml.dom.minidom import parse, parseString

env.overwriteOutput = True
output = env.scratchFolder
"""
    search for and replace the schema locking key
"""


def disable_locking(doc):
    key_tags = doc.getElementsByTagName('Key')
    for keyTag in key_tags:
        if keyTag.firstChild.data == 'schemaLockingEnabled':
            keyTag.nextSibling.firstChild.data = 'false'


"""
    Set an instance count for min and max instances.
    We set them both the same so that end users never
    have to wait for spin ups.

"""


def set_instance_count(doc, instance_count):
    key_tags = doc.getElementsByTagName('Key')
    for keyTag in key_tags:
        # if instance count is 0 set up shared instances
        if instance_count == 0:
                if keyTag.firstChild.data == 'provider':
                    keyTag.nextSibling.firstChild.data = 'DMaps'

        if keyTag.firstChild.data == 'MinInstances' or \
                keyTag.firstChild.data == 'MaxInstances' or \
                keyTag.firstChild.data == 'InstancesPerContainer':
            keyTag.nextSibling.firstChild.data = instance_count


"""
    find and replace the overwrite part of the sddraft xml document
"""


def enable_overwrite(doc):
    state_tags = doc.getElementsByTagName('State')
    for stateTag in state_tags:
        if stateTag.firstChild.data == 'esriSDState_Draft':
            stateTag.firstChild.data = 'esriSDState_Published'

    typeTags = doc.getElementsByTagName('Type')
    for typeTag in typeTags:
        if typeTag.firstChild.data == 'esriServiceDefinitionType_New':
            typeTag.firstChild.data = 'esriServiceDefinitionType_Replacement'


"""
 find and replace the feature access section in an sddraft xml document
 and enable feature access capabilities
 
"""


def enable_feature_access(doc, capabilities):
    # The follow code piece modifies the SDDraft from a new MapService with caching capabilities
    # to a FeatureService with Map, Create and Query capabilities.
    type_names = doc.getElementsByTagName('TypeName')
    for typeName in type_names:
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
        key_values = propSet.childNodes
        for keyValue in key_values:
            if keyValue.tagName == 'Key':
                if keyValue.firstChild.data == "isCached":
                    keyValue.nextSibling.firstChild.data = "false"

    # turn on feature access capabilities
    configProps = doc.getElementsByTagName('Info')[0]
    propArray = configProps.firstChild
    propSets = propArray.childNodes
    for propSet in propSets:
        key_values = propSet.childNodes
        for keyValue in key_values:
            if keyValue.tagName == 'Key':
                if keyValue.firstChild.data == "WebCapabilities":
                    keyValue.nextSibling.firstChild.data = capabilities


def write_draft(sddraft_path, doc):
    f = open(sddraft_path, 'w')
    doc.writexml(f)
    f.close()


def read_draft(sddraft_path):
    # Read the contents of the original SDDraft into an xml parser
    doc = parse(sddraft_path)
    return doc


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
            server,
            service_name=None,
            folder=None,
            schema_locks=False,
            overwrite=False,
            feature_access=False,
            feature_capabilities='Map,Query,Data',
            instance_count=1,
            project='CURRENT',
            server_type='STANDALONE_SERVER',
            service_type='MAP_SERVICE'):
    if not service_name:
        service_name = map_name

    # get the map
    sddraft_filename = f'{service_name}.sddraft'
    sddraft_output_filename = join(output, sddraft_filename)
    if type(project) == str:
        pro = ArcGISProject(project)
    else:
        pro = project
    mp = pro.listMaps(map_name)

    if not len(mp):
        AddError(f'could not locate map {map_name} in project {project}')
        return
    mp = mp[0]

    # create service draft and export to draft file
    AddMessage('Creating service draft...')
    service_draft = CreateSharingDraft(
        server_type,
        service_type,
        service_name,
        mp)
    service_draft.targetServer = server

    # set folder if necessary
    if folder:
        service_draft.serverFolder = folder

    service_draft.exportToSDDraft(sddraft_output_filename)

    # xml schema modifications
    # open the xml for potential modifications
    doc = read_draft(sddraft_output_filename)

    # set instance count
    set_instance_count(doc, instance_count)

    # enable feature service?
    if feature_access:
        enable_feature_access(doc, feature_capabilities)

    if not schema_locks:
        disable_locking(doc)

        if overwrite:
            enable_overwrite(doc)

    # save the modified xml
    write_draft(sddraft_output_filename, doc)

    # stage service
    AddMessage('Staging service...')
    sd_filename = f"{service_name}.sd"
    sd_output_filename = join(output, sd_filename)
    StageService_server(sddraft_output_filename, sd_output_filename)

    # share to server
    AddMessage('Uploading to server...')
    UploadServiceDefinition_server(sd_output_filename, server)
    AddMessage(f'Successfully published service {service_name} to {server}')
