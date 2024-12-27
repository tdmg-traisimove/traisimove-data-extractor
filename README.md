# TRAISI Move data extractor
Script to extract data into csv files

# Setup
1. Install dependencies. It is recommended to use a virtual environment such as venv or virtualenv.
```shell
virtualenv venv # Recommended
source venv/bin/activate # Recommended
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

# Extract data
Launch the script main.py and specify the config.
``` shell
source venv/bin/activate # Recommended
python main.py config.json
```

The following files will be generated:
- traisimove_database.csv
- traisimove_traces.csv
- traisimove_users.csv

# Code quality checks
The following script is for development purpose.
1. Install dependencies
```shell
pip install -r requirements-dev.txt
```
2. Run
```shell
./lint.sh
```
