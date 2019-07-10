# Grabs Unity Raw Data using its REST API. Does not update ad revenue from Google Admob.
# I have no idea how to do that yet.

import datetime as dt
import gzip
import io
import json
import os
import shutil
import time
import psycopg2
import requests
from requests.auth import HTTPBasicAuth

destination_directory = 'C:/Users/BReyes/Desktop/UnityFiles/L&L'
unity_keys_LL = {'unity_project_id': 'a11b29e8-3a17-4ef6-be75-3a7b20034ba4', 'unity_api_key': '453e24ac3a7134edffc7d7d9794b5fa9'}

# Checks corresponding dataset tables for their most recent date.
def get_last_updated_date(data_table):
    conn = psycopg2.connect("host=localhost dbname=Bryan/Test user=postgres password=lolque12")
    cur = conn.cursor()
    cur.execute(
                """
                select max(to_timestamp(((values -> 'submit_time')::text)::bigint /1000) at time zone 'utc')::date
                from {table}
                """.format(table=data_table))

    last_updated = cur.fetchone()[0]
    start_date = last_updated + dt.timedelta(days=1)
    start_date_string = dt.datetime.strftime(start_date, '%Y-%m-%d')
    end_date = dt.datetime.today()
    end_date_string = dt.datetime.strftime(end_date,'%Y-%m-%d')

    conn.commit()
    conn.close()
    return start_date_string, end_date_string


# Requests data from Unity's REST API for corresponding data sets.
def request_data(data_table, data_set):
    start_date, end_date = get_last_updated_date(data_table=data_table)
    uri = 'https://analytics.cloud.unity3d.com/api/v2/projects/' + unity_keys_LL['unity_project_id'] + '/rawdataexports'
    postBodyJson = {'startDate': start_date, 'endDate': end_date, 'format': 'json', 'dataset': data_set}
    headers = {'content-type': 'application/json'}

    r = requests.post(uri, json.dumps(postBodyJson), auth=HTTPBasicAuth(unity_keys_LL['unity_project_id'],
                                                          unity_keys_LL['unity_api_key']), headers=headers)
    if r.status_code == 200:
        return r.json()['id']
    else:
        print('Request not received.')


# Downloads files for data sets.
def download_file(data_table, data_set, download_folder):
    id = request_data(data_table=data_table, data_set=data_set)
    while True:
        try:
            uri = 'https://analytics.cloud.unity3d.com/api/v2/projects/' + unity_keys_LL['unity_project_id'] + '/rawdataexports/' + id
            time.sleep(30)
            r2 = requests.get(uri, auth=HTTPBasicAuth(unity_keys_LL['unity_project_id'], unity_keys_LL['unity_api_key']))
            responseJson = r2.json()
            for fileToDownload in responseJson['result']['fileList']:
                fileUri = fileToDownload['url']
                fileName = os.path.splitext(fileToDownload['name'])[0]  # file name w/o extension
                fileRequest = requests.get(fileUri)

                if fileRequest.status_code == 200:
                    compressed_file = io.BytesIO(fileRequest.content)
                    decompressed_file = gzip.GzipFile(fileobj=compressed_file)
                    with open(os.path.join(destination_directory + download_folder, fileName), 'w+b') as outFile:
                        outFile.write(decompressed_file.read())
                    print(data_set + ' file has been downloaded!')
            break
        except KeyError:
            print(data_set + ' file is not ready for download. Trying to download again...')
            continue


# Uploads downloaded data files for data sets into PostgreSQL tables.
def upload_to_postgres(download_folder, data_table):
    directory = os.listdir(destination_directory + download_folder)
    os.chdir(destination_directory + download_folder)
    conn = psycopg2.connect("host=localhost dbname=Bryan/Test user=postgres password=lolque12")
    cur = conn.cursor()

    for file in directory:
        open_file = open(file, 'r', encoding='utf-8')
        cur.copy_from(open_file, data_table)

    conn.commit()
    cur.close()
    conn.close()


# Moves downloaded files into archive folder directory.
def move_files(download_folder, moved_folder):
    directory = os.listdir(destination_directory + download_folder)
    os.chdir(destination_directory + download_folder)
    for move_file in directory:
        shutil.move(move_file, destination_directory + moved_folder)


# Executes all above functions.
def do_everything(data_set, download_folder, data_table, moved_folder):
    get_last_updated_date(data_table=data_table)
    download_file(data_table=data_table, data_set=data_set, download_folder=download_folder)
    upload_to_postgres(download_folder=download_folder, data_table=data_table)
    move_files(download_folder=download_folder, moved_folder=moved_folder)


# Functions being executed.
do_everything(data_set='custom', download_folder='/custom/Import/', data_table='legendsandletters_custom', moved_folder='/custom/old/rest of files v2')
do_everything(data_set='appStart', download_folder='/appStart/Import/', data_table='legendsandletters_appstart', moved_folder='/appStart/old/rest of files v2')
do_everything(data_set='appRunning', download_folder='/appRunning/Import/', data_table='legendsandletters_apprunning', moved_folder='/appRunning/old/rest of files v2')

print('Completed!')








