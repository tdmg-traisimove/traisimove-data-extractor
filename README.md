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
    ],
    "ignored_tokens": [
        "nrelop_test-study_default_YLLzhIStsu9VFqYcs03aX1eekjQhIfdO"
    ]
}
```
`db_url`: The url to the database.  
`studies_names`: The names of the studies to extract.  
`ignored_tokens`: The tokens that should not be extracted.  

# Code quality checks
1. Install dependencies
```shell
pip install -r requirements-dev.txt
```
2. Run
```shell
./validate.sh
```
