"""
 find and replace the feature access section in an sddraft xml document
 and enable feature access capabilities
 
"""
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
