import json
import pandas as pd
from yandex_music import Track, Client


def get_data_from_file(file):
    with open(file, "r") as f:
        data = json.load(f)['trackIds']
        for i in range(len(data)):
            if ':' in str(data[i]):
                data[i] = data[i].split(':')[0]
            data[i] = int(data[i])
        return data


def link_two_dbs(a, b):
    i = 0
    while i < len(a):
        j = i
        k = 0
        while True:
            if j == len(a):
                return a + b[k:]
            if k == len(b):
                return a
            if a[j] != b[k]:
                break
            j += 1
            k += 1
        i += 1
    return a + b


def link_data(data):
    result = list(reversed(data[0]))
    i = 1
    while i < len(data):
        result = link_two_dbs(result, list(reversed(data[i])))
        i += 1
    return result


def link_files(files):
    data = []
    count = 0
    for file in files:
        filedata = get_data_from_file(file)
        data.append(filedata)
        count += len(filedata)
    linked = link_data(data)
    print("Recieved {} lines of raw data, cutted {} duplicates\n\
Total {} lines ready for analysis".format(count, count-len(linked), len(linked)))
    return linked

def form_dataframe(data):
    df = pd.DataFrame({'id' : data, 'count' : 1})
    df = df.groupby(by='id').count().reset_index()
    client = Client()
    df['data'] = client.tracks(df['id'])
    df['name'] = ""
    df['artist'] = ""
    
    pd.options.mode.chained_assignment = None
    for i in range(len(df)):
        df['name'][i] = df['data'][i]['title']
        try:
            df['artist'][i] = df['data'][i]['artists'][0]['name']
            for artist in df['data'][i]['artists'][1:]:
                df['artist'][i] += ", " + artist['name']
        except IndexError as e:
            df['artist'][i] = "Unknown"
    
    
    df = df.sort_values(['count'], ascending=False)
    df = df.reset_index()
    
    return df
   
def print_to_file(df, file="result.txt"):
    with open(file, 'w') as f3:
        for i in range(len(df)):
            f3.write("{0:<5} {1} - {2}\n".format(df['count'][i], df['artist'][i], df['name'][i]))


if __name__ == '__main__':
    from settings import CACHED_DATA

    data = link_files(CACHED_DATA)
    df = form_dataframe(data)

    print_to_file(df)