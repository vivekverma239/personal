import webbrowser, os
import json
import boto3
import io
from io import BytesIO, StringIO
import sys
import pandas as pd
from pprint import pprint
import tempfile
from pdf2image import convert_from_path 
from django.conf import settings

# set the default Django settings module for the 'celery' program.

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'intent_model.settings')
# boto3.setup_default_session(profile_name='aws-leena')

ROOT_PATH = os.path.join(settings.MEDIA_ROOT, "pdf_parser")

if not os.path.exists(ROOT_PATH): 
    os.mkdir(ROOT_PATH)

def get_rows_columns_map(table_result, blocks_map):
    rows = {}
    for relationship in table_result['Relationships']:
        if relationship['Type'] == 'CHILD':
            for child_id in relationship['Ids']:
                cell = blocks_map[child_id]
                if cell['BlockType'] == 'CELL':
                    row_index = cell['RowIndex']
                    col_index = cell['ColumnIndex']
                    if row_index not in rows:
                        # create new row
                        rows[row_index] = {}
                        
                    # get the text value
                    rows[row_index][col_index] = get_text(cell, blocks_map)
    return rows


def get_text(result, blocks_map):
    text = ''
    if 'Relationships' in result:
        for relationship in result['Relationships']:
            if relationship['Type'] == 'CHILD':
                for child_id in relationship['Ids']:
                    word = blocks_map[child_id]
                    if word['BlockType'] == 'WORD':
                        text += word['Text'] + ' '
                    if word['BlockType'] == 'SELECTION_ELEMENT':
                        if word['SelectionStatus'] =='SELECTED':
                            text +=  'X '    
    return text


def get_table_csv_results(file_name):

    with open(file_name, 'rb') as file:
        img_test = file.read()
        bytes_test = bytearray(img_test)
        print('Image loaded', file_name)

    # process using image bytes
    # get the results
    client = boto3.client('textract')

    response = client.analyze_document(Document={'Bytes': bytes_test}, FeatureTypes=['TABLES'])

    # Get the text blocks
    blocks=response['Blocks']
    # pprint(blocks)

    blocks_map = {}
    table_blocks = []

    for block in blocks:
        blocks_map[block['Id']] = block
        if block['BlockType'] == "TABLE":
            table_blocks.append(block)

    if len(table_blocks) <= 0:
        return [pd.DataFrame([{"Table": "No Table Detected"}])], [(0, 0)]

    csv = []
    bounding_boxes = []
    for index, table in enumerate(table_blocks):
        csv.append(generate_table_csv(table, blocks_map, index +1))
        box = table["Geometry"]["BoundingBox"] 
        bounding_boxes.append((box["Left"], box["Top"]))

    return csv, bounding_boxes


def generate_table_csv(table_result, blocks_map, table_index):
    rows = get_rows_columns_map(table_result, blocks_map)
    print(json.dumps(table_result))
    csv = ''
    for row_index, cols in rows.items():
        
        for col_index, text in cols.items():
            csv += '"{}"'.format(text) + ","
        csv += '\n'
        
    df = pd.read_csv(StringIO(csv), sep=",")

    return df

def extract_table_aws(file_id, filepath, page, top_coord):
    path = os.path.join(ROOT_PATH, file_id)
    if not os.path.exists(path):
        os.mkdir(path)
        images = convert_from_path(filepath, 500, fmt='jpg', output_folder=path)
    images = sorted(os.listdir(path))
    file_name = os.path.join(path, images[page-1])
    tables, bounding_boxes = get_table_csv_results(file_name)
    # print(top_ces)
    valid_table = sorted(zip(tables, bounding_boxes), key=lambda x: abs(x[1][0] - top_coord[0]) + abs(x[1][1] - top_coord[1]) )[0][0]
    valid_table.dropna(how='all', axis=0, inplace=True)
    valid_table.dropna(how='all', axis=1, inplace=True)
    return valid_table.to_html(index=False)

if __name__ == "__main__":
    pdf_path = '/Users/vivek/Leena AI Inc/Mayank Goyal - All Bots Intents Sheet/AIR ASIA (5c8b2bea9ee9ea0063f44eaf)/Documents/Policy/150501_AAIRCSOP02_Disciplinary-Policy_02_00-goqa-.pdf'
    print(extract_table_aws(pdf_path, 3, (0, 0)))
