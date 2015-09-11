# Series of Scripts Push data to CKAN's DataStore
The scripts in this repository were designed to:

- Download a CSV file from a particular CKAN resource
- Parse that CSV file based on a defined schema
- Push that file into CKAN's DataStore

This scripts checks the original files by storing and comparing a SHA-1 hash. Those take advantage of ScraperWiki's environmental variables (stored in a SQLite database). The DataStore is only updated if the file actually changes. This allows to configure the script to run on a frequent cron job (e.g. `@hourly`) without causing problems to the CKAN instance.

The file `run.sh` contains an example usage:

```bash
> python code/create-datastore.py RESOURCE_ID API_KEY
```

This script uses primary keys to upsert data to the database. If the `delete` parameter is passed as `True` to the function `upload_data_to_datastore(delete=False)` it will also delete any existing DataStores before creating a new one.
