# Downloading-Uploading-Unity-Data-Raw-Files-
Python script that downloads Unity Raw Data and uploads into local PostgreSQL database. This script works with the assumption that you have a JSONB Data table already set up for each data file (custom, appStarting, appRunning). If you don't then you'll need to create one for each and upload at least one day's worth of data to have the script pick up the most recent refresh date from the table. 

This script uses shinyshoe's ua2sql API request portion of their code:
https://github.com/shinyshoe/ua2sql

What the script does:
1. Checks the most recent date on
1. Submits a request via Unity Analytics' REST API for appRunning, custom, and appStart JSON data files.
2. Downloads each respective data file. 
3. Uploads each data file into its corresponding table in PostgreSQL.
4. Moves the downloaded files into an archived folder on user's computer. 

The script is best run on a daily basis, but can run up to a 30 day window (Unity's download limit). The tables in PostgreSQL maintains the JSON formatting of the data. It is not flattened and uses the JSON friendly features that PostgreSQL offers. 

