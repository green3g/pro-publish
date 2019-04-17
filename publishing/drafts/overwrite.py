"""
    find and replace the overwrite part of the sddraft xml document
"""
def enable_overwrite(doc):
    stateTags = doc.getElementsByTagName('State')
    for stateTag in stateTags:
        if stateTag.firstChild.data == 'esriSDState_Draft':
            stateTag.firstChild.data = 'esriSDState_Published'
            
    typeTags = doc.getElementsByTagName('Type')
    for typeTag in typeTags:
            if typeTag.firstChild.data == 'esriServiceDefinitionType_New':
                    typeTag.firstChild.data = 'esriServiceDefinitionType_Replacement'
    
