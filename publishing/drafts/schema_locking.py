"""
    search for and replace the schema locking key
"""

def disable_locking(doc):
    keyTags = doc.getElementsByTagName('Key')
    for keyTag in keyTags:
            if keyTag.firstChild.data == 'schemaLockingEnabled':
                    keyTag.nextSibling.firstChild.data = 'false'
