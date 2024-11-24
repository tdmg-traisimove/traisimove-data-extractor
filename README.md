# TRAISI Move data extractor
Script to extract data into csv files

# Setup
1. Install dependencies. It is recommended to use a virtual environment such as venv
```shell
pip install -r requirements.txt
```
2. Create a configuration file
```json
{
    "db_url": "mongodb://127.0.0.1:27017/Stage_database",
    "studies_names": [
        "test-study"
    ]
}
```
`db_url` is the url to the database.
`studies_names` are the names of the studies to extract