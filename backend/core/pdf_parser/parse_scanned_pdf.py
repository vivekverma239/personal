# import re
# import os 
# import binascii
# import time 
# import pandas as pd
# import sys
# import json
# from io import BytesIO, StringIO
# from pdf2image import convert_from_path 
# from decimal import Decimal
# import xml.etree.ElementTree as ET
# from collections import defaultdict, Counter
# import networkx as nx
# from decimal import Decimal, ROUND_HALF_UP
# from sklearn.cluster import AgglomerativeClustering
# import numpy as np
# import scipy.cluster.hierarchy as hcluster
# from collections import defaultdict
# from .extract_text import convert_pdf
# import pdfplumber
# import boto3
# import cv2

# from core.models import ProjectFile

# def get_rows_columns_map(table_result, blocks_map):
#     rows = {}
#     for relationship in table_result['Relationships']:
#         if relationship['Type'] == 'CHILD':
#             for child_id in relationship['Ids']:
#                 cell = blocks_map[child_id]
#                 if cell['BlockType'] == 'CELL':
#                     row_index = cell['RowIndex']
#                     col_index = cell['ColumnIndex']
#                     if row_index not in rows:
#                         # create new row
#                         rows[row_index] = {}
                        
#                     # get the text value
#                     rows[row_index][col_index] = get_text(cell, blocks_map)
#     return rows

# def get_text(result, blocks_map):
#     text = ''
#     if 'Relationships' in result:
#         for relationship in result['Relationships']:
#             if relationship['Type'] == 'CHILD':
#                 for child_id in relationship['Ids']:
#                     word = blocks_map[child_id]
#                     if word['BlockType'] == 'WORD':
#                         text += word['Text'] + ' '
#                     if word['BlockType'] == 'SELECTION_ELEMENT':
#                         if word['SelectionStatus'] =='SELECTED':
#                             text +=  'X '    
#     return text


# def generate_table_csv(table_result, blocks_map):
#     rows = get_rows_columns_map(table_result, blocks_map)
#     csv = ''
#     for row_index, cols in rows.items():
        
#         for col_index, text in cols.items():
#             csv += '"{}"'.format(text) + ","
#         csv += '\n'
        
#     df = pd.read_csv(StringIO(csv), sep=",")

#     return df



# # ROOT_PATH = os.path.join(settings.MEDIA_ROOT, "pdf_parser")
# ROOT_PATH = os.path.join("media", "pdf_parser")


    
# def generate() -> str:
#     timestamp = "{:x}".format(int(time.time()))
#     rest = binascii.b2a_hex(os.urandom(8)).decode("ascii")
#     return timestamp + rest



# class Page: 
#     def __init__(self, lines, tables, page_object):
#         """
#             page_object: A dict with Page properties like Text Bounding boxes 
#         """
#         self.id = generate()
#         self.tables = tables 
#         self.lines = lines
#         self.page_object = page_object 
#         self._merge_hz_boxes()
# #         self.merge_object_boxes()
#         self._merge_lines()
#         self.components =  self.para + self.tables
#         # self.components = sorted(self.components , key= lambda x: -(x["y0"] -5 ) if x["type"] = "bigbox" else -x["y0"])
#         self.components = sorted(self.components , key= lambda x: -x["y1"])


#     def _merge_hz_boxes(self): 
#         temp = self.lines
#         sorted_y = sorted(temp, key=lambda x: x["y1"])
#         sorted_x = sorted(temp, key=lambda x: x["x0"])
        
#         merged = []
#         graph = nx.Graph()
#         for idx, item in enumerate(sorted_x):

#             x0, y0, x1, y1 = item["x0"], item["y0"], item["x1"], item["y1"]
            
#             # Find nearest y index
#             found_match = False
#             match_idx = self._find_horizontal_nearest_line(sorted_x, sorted_y, x1)
#             final_match = None
            
#             while True:
#                 if not match_idx: 
#                     break
#                 if not item["text"].strip(): 
#                     break
#                 if match_idx >= len(sorted_x):
#                     break
#                 # Find idx corresponding to bbox
#                 match = sorted_x[match_idx]
# #                 print(idx, match_idx, abs(match["y1"] - y1), abs(match["x0"] - x1))

#                 # Check if y is beyond a threshold in which case break
#                 if abs(match["x0"] - x1) > 200:
#                     break
#                 # Check if x is within a threshold if yes match
#                 if abs(match["x0"] - x1) < 200 and abs(match["y0"] - y0) < 30 and  match["text"].strip():
#                     found_match = True
#                     final_match = match_idx
#                     break
#                 match_idx += 1
                
#             if found_match:
#                     graph.add_edge(idx, final_match)
#                     graph.add_node(idx)
                    
#         matches = list(nx.connected_components(graph))
#         lines = []
#         all_matched_lines = []
#         for match in matches: 
#             x0 = []
#             x1 = []
#             y0 = []
#             y1 = []
#             all_matched_lines.extend(list(match))
#             item = self._extract_textline_properties(list(sorted([sorted_x[idx] for idx in match], key=lambda x: x["x0"])))
#             for match_item in match: 
#                 x0.append(sorted_x[match_item]["x0"])
#                 y0.append(sorted_x[match_item]["y0"])
#                 x1.append(sorted_x[match_item]["x1"])
#                 y1.append(sorted_x[match_item]["y1"])
                
# #             item = {}
#             item["x0"] = min(x0)
#             item["y0"] = min(y0)
#             item["x1"] = max(x1)
#             item["y1"] = max(y1)
#             item["top"] = Decimal(self.page_object["height"]) - item["y1"] 
#             item["bottom"] = Decimal(self.page_object["height"]) - item["y0"] 
# #             item["text"] = 
#             lines.append(item)
        
#         individual_lines = [] 
#         temp = [sorted_x[i] for i in range(0, len(sorted_x)) if i not in all_matched_lines and sorted_x[i]["text"].strip()]
#         for i in temp: 
#             i["text"] = i["text"].strip()
#             individual_lines.append(i)
            
#         self.lines = lines + individual_lines
        
    
#     def _detect_bullets(self, item): 
#         """
#             Logic to detect bullets 
#              - Look at the first word, if in format of 1.1, 1. , a. A) - . 
#         """
#         if item["text"] and item["text"][0]: 
#             matches = re.findall(r'[a-z]', item["text"][0].lower())
#             if len(matches) == 0: 
#                 return True 
#         return False

#     def _merge_lines(self):
#         temp = []
#         for line in self.lines: 
#             parent_box = None 
#             nearest_edge = 100000
#             for box in self.tables: 
#                 if self._check_for_connnected(line, box):
#                     parent_box = box["id"]
#                     temp_nearest_edge = self._nearest_edge(box, line)
#                     if temp_nearest_edge < nearest_edge: 
#                         parent_box = box["id"]
#                         nearest_edge = temp_nearest_edge
#             line["parent_box"] = parent_box
#             if not parent_box: 
#                 temp.append(line)
            
#         sorted_y = sorted(temp, key=lambda x: x["y1"])
#         sorted_x = sorted(temp, key=lambda x: x["x1"])
        
#         merged = []
#         graph = nx.Graph()
#         for idx, item in enumerate(sorted_y):

#             x0, y0, x1, y1 = item["x0"], item["y0"], item["x1"], item["y1"]
            
#             # Find nearest y index
#             found_match = False
#             match_idx = self._find_vertical_nearest_line(sorted_x, sorted_y, y1)
#             final_match = None
#             item["is_bullet"] = self._detect_bullets(item)
#             if item["is_bullet"]:
#                 item["text"] = "\n" + item["text"]
            
#             x_thres = 600 if item["is_bullet"] else 300
# #             print("Main", idx, item.get("text"))
# #             print("Searching...")
#             while True:
#                 if not item["text"].strip(): 
#                     break
#                 if match_idx < 0:
#                     break
#                 # Find idx corresponding to bbox
#                 match = sorted_y[match_idx]
# #                 print(match.get("text"), abs(match["y1"] - y0), abs(match["x0"] - x0))
# #                 print(idx, match_idx, abs(match["y1"] - y1), abs(match["x0"] - x0))
#                 # Check if y is beyond a threshold in which case break
#                 if abs(match["y1"] - y0) > 150:
#                     break
#                 # Check if x is within a threshold if yes match
#                 if abs(match["x0"] - x0) < x_thres and  match["text"].strip() and\
#                     match.get("parent_box") == item.get("parent_box"):
#                     found_match = True
# #                     print("FOUND MATCH", found_match)
#                     final_match = match_idx
#                     break
#                 match_idx -= 1
            
# #             print("FOUND MATCH", found_match)
#             if found_match:
#                 graph.add_edge(idx, final_match)
#                 graph.add_node(idx)
                    
#         matches = list(nx.connected_components(graph))
#         para = []
#         all_matched_lines = []
#         for match in matches: 
#             x0 = []
#             x1 = []
#             y0 = []
#             y1 = []
#             all_matched_lines.extend(list(match))
#             item = {}
#             item["text"] = "<br/>".join([i["text"] for i in list(sorted([sorted_y[idx] for idx in match], key=lambda x: -x["y1"]))])

#             for match_item in match: 
#                 x0.append(sorted_y[match_item]["x0"])
#                 y0.append(sorted_y[match_item]["y0"])
#                 x1.append(sorted_y[match_item]["x1"])
#                 y1.append(sorted_y[match_item]["y1"])
                
#             item["x0"] = min(x0)
#             item["y0"] = min(y0)
#             item["x1"] = max(x1)
#             item["y1"] = max(y1)
#             item["top"] = Decimal(self.page_object["height"]) - item["y1"] 
#             item["bottom"] = Decimal(self.page_object["height"]) - item["y0"] 
#             item["type"] = "para"

#             para.append(item)
        
#         individual_lines = [sorted_y[i] for i in range(0, len(sorted_y)) if i not in all_matched_lines and sorted_y[i]["text"].strip()]
#         self.para = para + individual_lines
        
#     def _check_for_merge(self, item1, item2):
#         bold1 = "bold" in item1["font"].lower()
#         bold2 = "bold" in item2["font"].lower()
#         return bold1 == bold2
        
        
#     def merge_object_boxes(self):
#         temp = [ i for i in self.page_object["others"] if i["type"] != "figure"]
#         sorted_y = sorted(temp, key=lambda x: x["y0"])
#         sorted_x = sorted(temp, key=lambda x: x["x0"])
#         merged = []
#         graph = nx.Graph()
#         for idx, item in enumerate(sorted_y):
#             # Iterate over items one by one and link to nearest boxes 
#             x0, y0, x1, y1 = item["x0"], item["y0"], item["x1"], item["y1"]
            
#             # Find nearest y index
#             found_match = False
# #             match_idx = self._find_vertical_nearest_box(sorted_x, sorted_y, y0)
#             match_idx = 0 
#             final_match = []
            
#             while True:
#                 if match_idx == None  or match_idx >= len(sorted_y):
#                     break
#                 if match_idx == idx: 
#                     match_idx += 1
#                     continue
#                 # Find idx corresponding to bbox
#                 match = sorted_y[match_idx]
#                 if self._check_for_connnected(item, match):
#                     found_match = True
#                     final_match.append(match_idx)
#                 match_idx += 1

#             if found_match:
#                 for match_idx in final_match:
#                     graph.add_edge(idx, match_idx)
#                     graph.add_node(idx)
                    
#         matches = list(nx.connected_components(graph))
#         bigbox = []
#         all_matched_lines = []
#         for idx, match in enumerate(matches): 
#             x0 = []
#             x1 = []
#             y0 = []
#             y1 = []
#             all_matched_lines.extend(list(match))
#             item = {}
#             for match_item in match: 
#                 x0.append(sorted_y[match_item]["x0"])
#                 y0.append(sorted_y[match_item]["y0"])
#                 x1.append(sorted_y[match_item]["x1"])
#                 y1.append(sorted_y[match_item]["y1"])
                
#             item["x0"] = min(x0) 
#             item["y0"] = min(y0) 
#             item["x1"] = max(x1)
#             item["y1"] = max(y1)
#             item["top"] = Decimal(self.page_object["height"]) - item["y1"] 
#             item["bottom"] = Decimal(self.page_object["height"]) - item["y0"] 
#             item["type"] = "bigbox"
#             item["id"] = self.id + "_box_" + str(idx)
#             bigbox.append(item)
        
        
#         individual_box = [sorted_y[i] for i in range(0, len(sorted_y)) if i not in all_matched_lines]
#         for idx, item in enumerate(individual_box):
#             individual_box[idx]["id"] = self.id + "_in_box_" + str(idx)

#         self.bigbox = [] 
#         for box in  bigbox  + individual_box: 
#             # Filter small height boxes: 
#             if (box["y1"] - box["y0"]) > 35: 
#                 self.bigbox.append(box)
#         print(self.bigbox[:2])  
            
    
#     def _nearest_edge(self, box1, box2):
#         ax0, ay0, ax1, ay1 = box1["x0"], box1["y0"], box1["x1"], box1["y1"]
#         bx0, by0, bx1, by1 = box2["x0"], box2["y0"], box2["x1"], box2["y1"]
#         return min(abs(ax0 - ax0), abs(ay0 - ay0), abs(ax1 - ax1), abs(ay1 - ay1))

#     def _check_for_connnected(self, item_a, item_b):
#         # Expand bounding boxes and see if they intersect 
#         ax0, ay0, ax1, ay1 = item_a["x0"], item_a["y0"], item_a["x1"], item_a["y1"]
#         bx0, by0, bx1, by1 = item_b["x0"], item_b["y0"], item_b["x1"], item_b["y1"]
        
#         X_EXPAND_LIMIT = 1
#         Y_EXPAND_LIMIT = 1
        
#         ax0 = ax0 - X_EXPAND_LIMIT
#         ax1 = ax1 + X_EXPAND_LIMIT
#         ay0 = ay0 - Y_EXPAND_LIMIT
#         ay1 = ay1 + Y_EXPAND_LIMIT
#         bx0 = bx0 - X_EXPAND_LIMIT
#         bx1 = bx1 + X_EXPAND_LIMIT
#         by0 = by0 - Y_EXPAND_LIMIT
#         by1 = by1 + Y_EXPAND_LIMIT
        
#         # Now check for interaction 
#         # If one rectangle is on left side of other 
#         if(ax0 >= bx1 or ax1 <= bx0): 
#             return False

#         # If one rectangle is above other 
#         if(ay1 <= by0 or ay0 >= by1): 
#             return False

#         return True
        

#     def _find_vertical_nearest_box(self, sorted_x, sorted_y, y):
#         match_idx = None 
#         for idx in range(len(sorted_y)):
#             if sorted_y[idx]['y0'] >= y:
#                 match_idx = idx
#                 break
#         return match_idx 
    
#     def _find_vertical_nearest_line(self, sorted_x, sorted_y, y):
#         match_idx = None 
#         for idx in range(len(sorted_y)):
#             if sorted_y[idx]['y1'] >= y:
#                 match_idx = idx
#                 break
#         return match_idx - 1
    
#     def _find_horizontal_nearest_line(self, sorted_x, sorted_y, x):
#         match_idx = None 
#         for idx in range(len(sorted_x)):
#             if sorted_x[idx]['x0'] >= x:
#                 match_idx = idx
#                 break
#         return match_idx 
    
    
#     def _extract_textline_properties(self, items):
#         """
#         """
#         reslist = items
#         text = ' '.join([element["text"].strip() for element in reslist])
#         properties = items
#         property_dict = defaultdict(list)
#         for property in properties:
#             for key in property:
#                 property_dict[key].append(property[key])
#         property_dict = dict(property_dict)
#         for key in property_dict:
#             val = Counter(list(property_dict[key])).most_common(1)[0][0]
#             property_dict[key] = val
#         property_dict["text"] = text
#         return property_dict

    
# class PDFParser:
#     """
#         :: DOCSTRING ::
#     """
#     def __init__(self, file_id, filepath):
#         self.filepath = filepath
#         self.file_id = file_id
#         self.xml = convert_pdf(self.filepath, format='xml')  + "</pages>"
#         self.root = ET.fromstring(self.xml)
#         self.image_path = os.path.join(ROOT_PATH, file_id)
#         if not os.path.exists(self.image_path):
#             os.mkdir(self.image_path)
#             images = convert_from_path(filepath, 500, fmt='jpg', output_folder=self.image_path)
#         self.images = sorted(os.listdir(self.image_path))
#         self._parse_pages()
#         # self._detect_cluster()



#     def _parse_pages(self):
#         """
#             Parse the XML Format of PDF 
#         """
#         self.properties = {}
#         self.pages = {} 

#         pages = self.root.findall('page')
#         self.pages = {} 
#         _, _ , width, height = pages[0].attrib["bbox"].split(",")

#         for page_num, _ in enumerate(self.images): 
#             page_image_path = os.path.join(self.image_path, self.images[page_num])
            
#             with open(page_image_path, 'rb') as file:
#                 img_test = file.read()
#                 bytes_test = bytearray(img_test)

#             client = boto3.client('textract')
#         #     response = client.detect_document_text(Document={'Bytes': bytes_test})
#             response = client.analyze_document(Document={'Bytes': bytes_test}, FeatureTypes=[
#                 'TABLES',
#             ])
            
#             lines = [] 
#             tables = [] 
#             image = cv2.imread(page_image_path)
#             # page_height, page_width, _ = image.shape 
#             page_height, page_width = int(float(height)), int(float(width))
#             print( page_height, page_width)
#             block_map = {block['Id']: block for block in response["Blocks"]}
#             for item in response["Blocks"]:
#                 bb = item["Geometry"]['BoundingBox']
#                 x0, y1 = int(bb["Left"] * page_width), page_height - int(bb["Top"] * page_height)
#                 x1, y0 = int(x0 + bb["Width"] * page_width),int(y1 - bb["Height"] * page_height)
#                 top = Decimal(page_height - y1)
#                 bottom = Decimal(page_height - y0)

#                 if item["BlockType"] == "LINE":
#                     lines.append({"x0": x0, "y0": y0, "x1": x1, "y1": y1, "top": top, "bottom": bottom, \
#                                   "text": item["Text"], "id": item["Id"]}) 
#                 elif item["BlockType"] == "TABLE":
#                     df = generate_table_csv(item, block_map)
#                     df.dropna(how='all', axis=0, inplace=True)
#                     df.dropna(how='all', axis=1, inplace=True)
#                     text = df.to_csv(sep="\t", index=False)
#                     html = df.to_html(index=False)
#                     tables.append({"x0": x0, "y0": y0, "x1": x1, "y1": y1,  "top": top, "bottom": bottom, \
#                                   "id": item["Id"], "type" : "table", "text": text, "html": html})


#             page_obj = Page(lines=lines, tables=tables, page_object={"height": page_height, "width": page_width})

    
#             self.pages[page_num+1] = {"components": page_obj.components, "page": page_num+1, "height": page_height, "width": page_width}
            
            
    
#     def draw_bb(self, page=1):
#         page_image_path = os.path.join(self.image_path, self.images[page-1])
#         image = cv2.imread(page_image_path)
#         page_height, page_width, _ = image.shape 
#         for component in self.pages[page]["components"]:
#             x_min, x_max = component["x0"], component["x1"]
#             y_min, y_max = page_height - component["y1"], page_height - component["y0"]
#             image = cv2.rectangle(image, (x_min,y_min), (x_max,y_max), (0,255,0), 2) # add rectangle to image
#         plt.imshow(image)


#     def export(self):
#         data = {
#             "pages": self.pages,
#             # "cluster_texts": self.cluster_text
#         }
#         return data

# class ComplexEncoder(json.JSONEncoder):
#      def default(self, obj):
#          if isinstance(obj, Decimal):
#              return float(obj)
#          if isinstance(obj, np.integer):
#              return int(obj)

#         #  if isinstance(obj, int32):
#         #      return int(obj)
#          # Let the base class default method raise the TypeError
#          return json.JSONEncoder.default(self, obj)


# def parse_scanned(, filepath):
#     file_id = instances.id
#     try: 
#         parser = PDFParser(str(file_id), file_path) 
#         data = parser.export()
#         instances.parsed_data = json.loads(json.dumps(data, cls=ComplexEncoder))
#         instances.auto_parse_status = "success" 
#     except: 
#         import traceback
#         traceback.print_exc()
#         instances.auto_parse_status = "failed" 
#     instances.save()