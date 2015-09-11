# Script to interact with the datastore
# on the Data Team's end.

import os
import csv
import sys
import json
import requests
import urllib
import hashlib
import scraperwiki
import ckanapi

# Collecting configuration variables
remote = 'https://test-data.hdx.rwlabs.org'
resource_id = sys.argv[1]
apikey = sys.argv[2]

# path to the locally stored CSV file
PATH = 'temp.csv'

# ckan will be an instance of ckan api wrapper
ckan = None

# Function to download a resource from CKAN.
def downloadResource(filename):

    # querying
    url = 'https://test-data.hdx.rwlabs.org/api/action/resource_show?id=' + resource_id
    r = requests.get(url, auth=('dataproject', 'humdata'))
    doc = r.json()
    fileUrl = doc["result"]["url"]

    # downloading
    try:
        urllib.urlretrieve(fileUrl, filename)
    except:
        print 'There was an error downlaoding the file.'


# Function that checks for old SHA hash
# and stores as a SW variable the new hash
# if they differ. If this function returns true,
# then the datastore is created.
def checkHash(filename, first_run):
    hasher = hashlib.sha1()
    with open(filename, 'rb') as afile:
        buf = afile.read()
        hasher.update(buf)
        new_hash = hasher.hexdigest()

    # checking if the files are identical or if
    # they have changed
    if first_run:
        scraperwiki.sqlite.save_var('stag', new_hash)
        new_data = False

    else:
        old_hash = scraperwiki.sqlite.get_var('stag')
        scraperwiki.sqlite.save_var('stag', new_hash)
        new_data = old_hash != new_hash

    # returning a boolean
    return new_data


def updateDatastore(filename):

    # Checking if there is new data
    # pass True to the first_run parameter
    # if this is the first run.
    update_data = checkHash(filename, first_run = False)
    if (update_data == False):
        print "\nDataStore Status: No new data. Not updating datastore."
        return

    # proceed if the hash is different, i.e. update
    print "DataStore Status: New data. Updating datastore."

    # defining the schema
    resources = [
        {
            'resource_id': resource_id,
            'path': filename,
            'schema': {
                "fields": [
                    {"id": "org_name", "type": "text"},
                    {"id": "screen_cap_asset_selector", "type": "text"},
                    {"id": "highlight_asset_type", "type": "text"},
                    {"id": "highlight_asset_id", "type": "text"},
                    {"id": "hightlight_asset_row_code", "type": "text"}
                ],
                "primary_key": "org_name"
            },
        }
    ]

    def upload_data_to_datastore(ckan_resource_id, resource, delete):

        # if the delete flag is True, then delete the current
        # datastore before creating a new one
        if delete:
            try:
                ckan.action.datastore_delete(resource_id=ckan_resource_id, force=True)
            except:
                pass

        ckan.action.datastore_create(
            resource_id=ckan_resource_id,
            force=True,
            fields=resource['schema']['fields'],
            primary_key=resource['schema'].get('primary_key'))

        reader = csv.DictReader(open(resource['path']))
        rows = [row for row in reader]
        chunksize = 10000
        offset = 0
        print('Uploading data for file: %s' % resource['path'])
        while offset < len(rows):
            rowset = rows[offset:offset + chunksize]
            ckan.action.datastore_upsert(
                resource_id=ckan_resource_id,
                force=True,
                method='upsert',
                records=rowset)
            offset += chunksize
            print('Done: %s' % offset)


    # if running as a command line script
    if __name__ == '__main__':
        if len(sys.argv) <= 2:
            usage = '''python scripts/create-datastore.py {ckan-resource-id} {api-key}

                    e.g.

                    python scripts/create-datastore.py CKAN_RESOURCE_ID API-KEY
                    '''
            print(usage)
            sys.exit(1)

        ckan = ckanapi.RemoteCKAN(remote, apikey=apikey)

        resource = resources[0]
        upload_data_to_datastore(resource['resource_id'], resource, delete=True)


# wrapper call for all functions
def runEverything(p):
    downloadResource(p)
    updateDatastore(p)

# ScraperWiki-specific error handler
try:
    runEverything(PATH)
    # if everything ok
    print "Everything seems to be just fine."
    scraperwiki.status('ok')

except Exception as e:
    print e
    scraperwiki.status('error', 'Creating datastore failed')
    os.system("mail -s 'Ebola toplines: creating datastore failed.' luiscape@gmail.com")
