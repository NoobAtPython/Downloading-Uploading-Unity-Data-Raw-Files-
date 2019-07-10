# Downloading-Uploading-Unity-Data-Raw-Files-
Python script that downloads Unity Raw Data and uploads into local PostgreSQL database. 

What the script does:
1. Submits a request via Unity Analytics' REST API for appRunning, custom, and appStart JSON data files.
2. Downloads each respective data file. 
3. Uploads each data file into its corresponding table in PostgreSQL.
4. Moves the uploaded file into an archived folder on user's computer. 

The script is best run on a daily basis, but can run up to a 30 day window (Unity's download limit). 

