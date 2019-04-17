from xml.dom.minidom import parse

def write_draft(sddraft_path, doc):
    f = open(sddraft_path, 'w')
    doc.writexml(f)
    f.close()

def read_draft(sddraft_path):
    # Read the contents of the original SDDraft into an xml parser
    doc = parse(sddraft_path)
    return doc
