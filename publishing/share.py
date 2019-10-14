
# coding: utf-8

# In[1]:


from arcgis import GIS
from os import environ
import requests


# ## Set up env and connect to gis

# In[2]:


username = environ.get('AGO_USERNAME')
password = environ.get('AGO_PASSWORD')
ags_username = environ.get('AGS_USERNAME')
ags_password = environ.get('AGS_PASSWORD')
ags_url = environ.get('AGS_URL')
gis = GIS('https://wsbeng.maps.arcgis.com/', username, password)


# debug 
ags_url = 'https://services.wsbeng.com:6443/arcgis'


# ## Define some utility methods

# In[3]:


def share_item(url, item_type, properties = {}):    
    types = {
        'MapServer': 'Map Service',
        'FeatureServer': 'Feature Service',
    }
    
    if not item_type in types:
        print(f'Invalid type: {item_type}')
        return
    item_type = types[item_type]
    
    defaults = {
        'url': url,
        'serviceUsername': ags_username,
        'servicePassword': ags_password,
        'type': item_type,
    }
    defaults.update(properties)
    gis.content.add(defaults)
    print(f'{url} has been successfully shared!')
    
def get_token(url, username, password):
    token = requests.post(f'{url}/tokens/generateToken', params={
        'f': 'json', 
        'username': username,
        'password': password,
        'client': 'requestip',
        'expiration': 60,
    }, verify=False).json()['token']
    return token

def get_folders(url, token):
    json = requests.get(f'{url}/rest/services', params={
        'f': 'json',
        'token': token,
    }, verify=False).json()
    if not 'folders' in json:
        print('Warning! "folders" was not found in json response.')
        print(json)
        return []
    return json['folders']

def get_services(url, token, folder=''):
    json = requests.get(f'{url}/rest/services/{folder}', params={
        'f': 'json',
        'token': token,
    }, verify=False).json()
    return json['services']

def get_info(url, token):
    json = requests.get(url, params={
        'f': 'json',
        'token': token,
    }, verify=False).json()
    return json


# ## Get a token

# In[4]:


token = get_token(ags_url, ags_username, ags_password)


# ## Share the items!

# In[19]:


def share_unshared_items():
    external_url = ags_url.replace(':6443', '')
    folders = get_folders(ags_url, token)

    # for all the folders
    for folder in folders:

        # get the services
        services = get_services(ags_url, token, folder)
        for service in services:

            # create the metadata 
            path = service['name']
            type = service['type']
            internal_url = f'{ags_url}/rest/services/{path}/{type}'
            service_url = f'{external_url}/rest/services/{path}/{type}'
            
            items = gis.content.search(f'{service_url} owner:{username}')
            if len(items):
                print(f'Item {service_url} is already shared.')
                continue
    
            service = get_info(internal_url, token)

            layer_list = [layer['name'] for layer in service['layers']] if 'layers' in service else []

            description = """
                Description: {} <br />
                Layers: {} <br />
                Server URL: {} <br />
            """.format(
                service['serviceDescription'],
                ', '.join(layer_list),
                service_url,
            )

            summary = f"""
                {type} for {path}. Shared with the ArcGIS Python API from {external_url}
            """

            tags = layer_list + [type, path, external_url.replace('https://', '')]

            # only use first 120 tags to avoid
            # ago issues with too many tags
            if len(tags) > 120:
                tags = tags[0:120]
                
            # create the item and share it
            item = {
                'url': service_url,
                'title': f'{path} ({type})',
                'description': description,
                'snippet': summary,
                'tags': ','.join(tags),
            }
            share_item(service_url, type, item)
     
    
# call our method
if __name__ == '__main__':
    share_unshared_items()
    

