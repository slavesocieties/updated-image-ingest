import os
import csv
import json

def load_dates(csv_path):
    with open(csv_path, mode='r') as file:
        # Create a csv.DictReader object
        reader = csv.DictReader(file)
        
        # Convert it into a list of dictionaries
        list_of_dicts = list(reader)
    return list_of_dicts

def create_metadata(vol_path='thumbnails'):
    month_lengths = [31,28,31,30,31,30,31,31,30,31,30,31]
    new_vols = []
    dates = load_dates('aurora_months.csv')
    for folder, subfolders, files in os.walk(vol_path):
        for file in files:
            with open(os.path.join(folder, file), 'r', encoding='utf-8') as f:
                data = json.load(f)
            data['volumeTitle'] = 'La Aurora ' + data['volumeTitle']
            with open(os.path.join(folder, file), 'w', encoding='utf-8') as f:
                json.dump(data, f)
            vol = {}
            vol['type'] = 'add'
            vol['id'] = data['volumeID']
            vol['fields'] = {}
            vol['fields']['title'] = data['volumeTitle']
            vol['fields']['creator'] = 'Slave Societies Digital Archive'
            vol['fields']['subject'] = ['News', 'Cuba']
            vol['fields']['description'] = 'La Aurora '
            vol['fields']['publisher'] = 'Slave Societies Digital Archive'
            vol['fields']['identifier'] = int(vol['id'])
            vol['fields']['type'] = ['Newspaper']
            vol['fields']['language'] = ['Spanish']
            vol['fields']['images'] = data['thumbnailCount']
            vol['fields']['format'] = ''
            vol['fields']['institution'] = 'La Aurora'
            vol['fields']['country'] = 'Cuba'
            vol['fields']['state'] = 'Matanzas'
            vol['fields']['city'] = 'Matanzas'
            vol['fields']['coords'] = "23.04603, -81.57895"
            for date in dates:
                if date['id'] == vol['id']:
                    vol['fields']['start_date'] = f"{date['year']}-{'0' * (2 - len(date['start_month']))}{date['start_month']}-01T00:00:00Z"
                    vol['fields']['end_date'] = f"{date['year']}-{'0' * (2 - len(date['end_month']))}{date['end_month']}-{month_lengths[int(date['end_month']) - 1]}T23:59:59Z"
            new_vols.append(vol)

    with open('Volume-Catalog.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f'There was metadata about {len(data)} volumes.')
    for vol in new_vols:
        data.append(vol)
    print(f'Metadata about {len(new_vols)} volumes was created.')            
    with open('Volume-Catalog.json', 'w', encoding='utf-8') as f:
        json.dump(data, f)
    print(f'There is now metadata about {len(data)} volumes.')            

# create_metadata()