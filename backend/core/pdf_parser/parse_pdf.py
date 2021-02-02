import re
import os 
import binascii
import time 
import json
from decimal import Decimal
import xml.etree.ElementTree as ET
from collections import defaultdict, Counter
import networkx as nx
from decimal import Decimal, ROUND_HALF_UP
from sklearn.cluster import AgglomerativeClustering
import numpy as np
import scipy.cluster.hierarchy as hcluster
from collections import defaultdict

from .extract_text import convert_pdf
from .poppler_parser import get_contexts

def generate() -> str:
    timestamp = "{:x}".format(int(time.time()))
    rest = binascii.b2a_hex(os.urandom(8)).decode("ascii")
    return timestamp + rest


class Page: 
    def __init__(self, page_object):
        """
            page_object: A dict with Page properties like Text Bounding boxes 
        """
        self.id = generate()
        self.page_object = page_object 
        self._merge_hz_boxes()
        self.merge_object_boxes()
        self._merge_lines()
        self.components =  self.para + self.bigbox
        # self.components = sorted(self.components , key= lambda x: -(x["y0"] -5 ) if x["type"] = "bigbox" else -x["y0"])
        self.components = sorted(self.components , key= lambda x: -x["y1"])

    def _check_bullets(self):
        pass 
    
    def _check_headings(self):
        pass 
    
    def _merge_hz_boxes(self): 
        temp = dict([(key, value) for key, value in self.page_object.items()])["lines"]
        sorted_y = sorted(temp, key=lambda x: x["y1"])
        sorted_x = sorted(temp, key=lambda x: x["x0"])
        
        merged = []
        graph = nx.Graph()
        for idx, item in enumerate(sorted_x):

            x0, y0, x1, y1 = item["x0"], item["y0"], item["x1"], item["y1"]
            
            # Find nearest y index
            found_match = False
            match_idx = self._find_horizontal_nearest_line(sorted_x, sorted_y, x1)
            final_match = None
            
            while True:
                if not match_idx: 
                    break
                if not item["text"].strip(): 
                    break
                if match_idx >= len(sorted_x):
                    break
                # Find idx corresponding to bbox
                match = sorted_x[match_idx]
#                 print(idx, match_idx, abs(match["y1"] - y1), abs(match["x0"] - x1))

                # Check if y is beyond a threshold in which case break
                if abs(match["x0"] - x1) > 100:
                    break
                # Check if x is within a threshold if yes match
                if abs(match["x0"] - x1) < 100 and abs(match["y0"] - y0) < 10 and  match["text"].strip():
                    found_match = True
                    final_match = match_idx
                    break
                match_idx += 1
                
            if found_match:
                    graph.add_edge(idx, final_match)
                    graph.add_node(idx)
                    
        matches = list(nx.connected_components(graph))
        lines = []
        all_matched_lines = []
        for match in matches: 
            x0 = []
            x1 = []
            y0 = []
            y1 = []
            all_matched_lines.extend(list(match))
            item = self._extract_textline_properties(list(sorted([sorted_x[idx] for idx in match], key=lambda x: x["x0"])))
            for match_item in match: 
                x0.append(sorted_x[match_item]["x0"])
                y0.append(sorted_x[match_item]["y0"])
                x1.append(sorted_x[match_item]["x1"])
                y1.append(sorted_x[match_item]["y1"])
                
#             item = {}
            item["x0"] = min(x0)
            item["y0"] = min(y0)
            item["x1"] = max(x1)
            item["y1"] = max(y1)
            item["top"] = Decimal(self.page_object["height"]) - item["y1"] 
            item["bottom"] = Decimal(self.page_object["height"]) - item["y0"] 
#             item["text"] = 
            lines.append(item)
        
        individual_lines = [] 
        temp = [sorted_x[i] for i in range(0, len(sorted_x)) if i not in all_matched_lines and sorted_x[i]["text"].strip()]
        for i in temp: 
            i["text"] = i["text"].strip()
            individual_lines.append(i)
            
        self.lines = lines + individual_lines
        
    
    def _detect_bullets(self, item): 
        """
            Logic to detect bullets 
             - Look at the first word, if in format of 1.1, 1. , a. A) - . 
        """
        if item["text"] and item["text"][0]: 
            matches = re.findall(r'[a-z]', item["text"][0].lower())
            if len(matches) == 0: 
                return True 
        return False

    def _merge_lines(self):
        temp = []
        for line in self.lines: 
            parent_box = None 
            nearest_edge = 100000
            for box in self.bigbox: 
                if self._check_for_connnected(line, box):
                    parent_box = box["id"]
                    temp_nearest_edge = self._nearest_edge(box, line)
                    if temp_nearest_edge < nearest_edge: 
                        parent_box = box["id"]
                        nearest_edge = temp_nearest_edge
            line["parent_box"] = parent_box
            temp.append(line)
            
        sorted_y = sorted(temp, key=lambda x: x["y1"])
        sorted_x = sorted(temp, key=lambda x: x["x1"])
        
        merged = []
        graph = nx.Graph()
        for idx, item in enumerate(sorted_y):

            x0, y0, x1, y1 = item["x0"], item["y0"], item["x1"], item["y1"]
            
            # Find nearest y index
            found_match = False
            match_idx = self._find_vertical_nearest_line(sorted_x, sorted_y, y1)
            final_match = None
            item["is_bullet"] = self._detect_bullets(item)
            if item["is_bullet"]:
                item["text"] = "\n" + item["text"]
            
            x_thres = 60 if item["is_bullet"] else 20
            if item["text"] == "Employees will be eligible to 1 day holiday as Special Day Off. This is to enable the employee":
                print("ITEM", item["text"])
            while True:
                if not item["text"].strip(): 
                    break
                if match_idx < 0:
                    break
                # Find idx corresponding to bbox
                match = sorted_y[match_idx]
                if item["text"] == "Employees will be eligible to 1 day holiday as Special Day Off. This is to enable the employee":
                    if match: 
                        print("Match", match["text"])
                        print("S1", abs(match["y1"] - y1))
                        print("S2", abs(match["x0"] - x0) < x_thres, match["text"].strip())

#                 print(idx, match_idx, abs(match["y1"] - y1), abs(match["x0"] - x0))
                # Check if y is beyond a threshold in which case break
                if abs(match["y1"] - y1) > 20:
                    break
                # Check if x is within a threshold if yes match
                if abs(match["x0"] - x0) < x_thres and  match["text"].strip():
                    found_match = True
                    final_match = match_idx
                    break
                match_idx -= 1
                
            if found_match:
                # check_matched = self._check_for_merge(item, match)
                # if item["text"] == "Employees will be eligible to 1 day holiday as Special Day Off. This is to enable the employee":
                #     print("CHECK", item["font"], match["font"])
                # if check_matched:
#                     merged.append((idx, prop_idx))
                    graph.add_edge(idx, final_match)
                    graph.add_node(idx)
                    
        matches = list(nx.connected_components(graph))
        para = []
        all_matched_lines = []
        for match in matches: 
            x0 = []
            x1 = []
            y0 = []
            y1 = []
            all_matched_lines.extend(list(match))
            item = self._extract_textline_properties(list(sorted([sorted_y[idx] for idx in match], key=lambda x: -x["y1"])))
            for match_item in match: 
                x0.append(sorted_y[match_item]["x0"])
                y0.append(sorted_y[match_item]["y0"])
                x1.append(sorted_y[match_item]["x1"])
                y1.append(sorted_y[match_item]["y1"])
                
            item["x0"] = min(x0)
            item["y0"] = min(y0)
            item["x1"] = max(x1)
            item["y1"] = max(y1)
            item["top"] = Decimal(self.page_object["height"]) - item["y1"] 
            item["bottom"] = Decimal(self.page_object["height"]) - item["y0"] 
            item["type"] = "para"

            para.append(item)
        
        individual_lines = [sorted_y[i] for i in range(0, len(sorted_y)) if i not in all_matched_lines and sorted_y[i]["text"].strip()]
        self.para = para + individual_lines
        
    def _check_for_merge(self, item1, item2):
        bold1 = "bold" in item1["font"].lower()
        bold2 = "bold" in item2["font"].lower()
        return bold1 == bold2
        
        
    def merge_object_boxes(self):
        temp = [ i for i in self.page_object["others"] if i["type"] != "figure"]
        sorted_y = sorted(temp, key=lambda x: x["y0"])
        sorted_x = sorted(temp, key=lambda x: x["x0"])
        merged = []
        graph = nx.Graph()
        for idx, item in enumerate(sorted_y):
            # Iterate over items one by one and link to nearest boxes 
            x0, y0, x1, y1 = item["x0"], item["y0"], item["x1"], item["y1"]
            
            # Find nearest y index
            found_match = False
#             match_idx = self._find_vertical_nearest_box(sorted_x, sorted_y, y0)
            match_idx = 0 
            final_match = []
            
            while True:
                if match_idx == None  or match_idx >= len(sorted_y):
                    break
                if match_idx == idx: 
                    match_idx += 1
                    continue
                # Find idx corresponding to bbox
                match = sorted_y[match_idx]
                if self._check_for_connnected(item, match):
                    found_match = True
                    final_match.append(match_idx)
                match_idx += 1

            if found_match:
                for match_idx in final_match:
                    graph.add_edge(idx, match_idx)
                    graph.add_node(idx)
                    
        matches = list(nx.connected_components(graph))
        bigbox = []
        all_matched_lines = []
        for idx, match in enumerate(matches): 
            x0 = []
            x1 = []
            y0 = []
            y1 = []
            all_matched_lines.extend(list(match))
            item = {}
            for match_item in match: 
                x0.append(sorted_y[match_item]["x0"])
                y0.append(sorted_y[match_item]["y0"])
                x1.append(sorted_y[match_item]["x1"])
                y1.append(sorted_y[match_item]["y1"])
                
            item["x0"] = min(x0) 
            item["y0"] = min(y0) 
            item["x1"] = max(x1)
            item["y1"] = max(y1)
            item["top"] = Decimal(self.page_object["height"]) - item["y1"] 
            item["bottom"] = Decimal(self.page_object["height"]) - item["y0"] 
            item["type"] = "bigbox"
            item["id"] = self.id + "_box_" + str(idx)
            bigbox.append(item)
        
        
        individual_box = [sorted_y[i] for i in range(0, len(sorted_y)) if i not in all_matched_lines]
        for idx, item in enumerate(individual_box):
            individual_box[idx]["id"] = self.id + "_in_box_" + str(idx)
            individual_box[idx]["type"] = "bigbox"
            

        self.bigbox = [] 
        for box in  bigbox  + individual_box: 
            # Filter whole page boxes: 
            if  (box["y1"] - box["y0"]) > (self.page_object["height"] - 50) and \
                (box["x1"] - box["x0"]) > (self.page_object["width"] - 50): 
                continue
            # Filter small height boxes: 
            if (box["y1"] - box["y0"]) > 35: 
                self.bigbox.append(box)
        
        print(self.bigbox)  
            
    
    def _nearest_edge(self, box1, box2):
        ax0, ay0, ax1, ay1 = box1["x0"], box1["y0"], box1["x1"], box1["y1"]
        bx0, by0, bx1, by1 = box2["x0"], box2["y0"], box2["x1"], box2["y1"]
        return min(abs(ax0 - ax0), abs(ay0 - ay0), abs(ax1 - ax1), abs(ay1 - ay1))

    def _check_for_connnected(self, item_a, item_b):
        # Expand bounding boxes and see if they intersect 
        ax0, ay0, ax1, ay1 = item_a["x0"], item_a["y0"], item_a["x1"], item_a["y1"]
        bx0, by0, bx1, by1 = item_b["x0"], item_b["y0"], item_b["x1"], item_b["y1"]
        
        X_EXPAND_LIMIT = 1
        Y_EXPAND_LIMIT = 1
        
        ax0 = ax0 - X_EXPAND_LIMIT
        ax1 = ax1 + X_EXPAND_LIMIT
        ay0 = ay0 - Y_EXPAND_LIMIT
        ay1 = ay1 + Y_EXPAND_LIMIT
        bx0 = bx0 - X_EXPAND_LIMIT
        bx1 = bx1 + X_EXPAND_LIMIT
        by0 = by0 - Y_EXPAND_LIMIT
        by1 = by1 + Y_EXPAND_LIMIT
        
        # Now check for interaction 
        # If one rectangle is on left side of other 
        if(ax0 >= bx1 or ax1 <= bx0): 
            return False

        # If one rectangle is above other 
        if(ay1 <= by0 or ay0 >= by1): 
            return False

        return True
        

    def _find_vertical_nearest_box(self, sorted_x, sorted_y, y):
        match_idx = None 
        for idx in range(len(sorted_y)):
            if sorted_y[idx]['y0'] >= y:
                match_idx = idx
                break
        return match_idx 
    
    def _find_vertical_nearest_line(self, sorted_x, sorted_y, y):
        match_idx = None 
        for idx in range(len(sorted_y)):
            if sorted_y[idx]['y1'] >= y:
                match_idx = idx
                break
        return match_idx - 1
    
    def _find_horizontal_nearest_line(self, sorted_x, sorted_y, x):
        match_idx = None 
        for idx in range(len(sorted_x)):
            if sorted_x[idx]['x0'] >= x:
                match_idx = idx
                break
        return match_idx 
    
    
    def _extract_textline_properties(self, items):
        """
        """
        reslist = items
        text = ' '.join([element["text"].strip() for element in reslist])
        properties = items
        property_dict = defaultdict(list)
        for property in properties:
            for key in property:
                property_dict[key].append(property[key])
        property_dict = dict(property_dict)
        for key in property_dict:
            val = Counter(list(property_dict[key])).most_common(1)[0][0]
            property_dict[key] = val
        property_dict["text"] = text
        property_dict["font"] = property_dict["font"].replace("-BoldItalic", "")
        property_dict["font"] = property_dict["font"].replace("-Italic", "")
        property_dict["font"] = property_dict["font"].replace("-Bold", "")
        return property_dict

    
class PDFParser:
    """
        :: DOCSTRING ::
    """
    def __init__(self, file_name):
        self.file_name = file_name
        self.xml = convert_pdf(self.file_name, format='xml')  + "</pages>"
        # self.pdf = pdfplumber.open(file_name)
        self.text = convert_pdf(self.file_name, format='text')
        self.root = ET.fromstring(self.xml)
        self._parse_xml()
        self.all_lines, self.contexts = get_contexts(file_name)
        # self._detect_cluster()

    def _extract_textline_properties(self, item):
        """
        """
        attrib = item.attrib
        reslist = list(item.iter())
        text = ''.join([element.text for element in reslist])
        properties = [element.attrib for element in reslist]
        property_dict = defaultdict(list)
        for property in properties:
            for key in property:
                property_dict[key].append(property[key])
        property_dict = dict(property_dict)
        property_dict.pop("bbox")
        for key in property_dict:
            val = Counter(list(property_dict[key])).most_common(1)[0][0]
            property_dict[key] = val
        property_dict["text"] = text
        return property_dict

    def _is_a_bullet(self, text):
        pass

    def is_a_section_breaker(self, text):
        # Simple rules as number of words and content of words
        pass

    def _parse_xml(self):
        """
            Parse the XML Format of PDF 
        """
        self.properties = {}
        pages = self.root.findall('page')
        self.pages = {} 

        for page_num, page in enumerate(pages): 

            _, _ , width, height = page.attrib["bbox"].split(",")
            width, height = float(width), float(height)
            
            page_object = {"page": page_num + 1 , "width": width, "height": height} 
            lines = self.root.findall('page[@id=\'{}\']/textbox/textline'.format(page_num+1)) 
            print("{} Number of Lines in Page {}".format(len(lines), page_num))
            
            self.bbox = {'x1': [] , 'y1':[], 'x2':[], 'y2':[]}
            textlines = self.root.findall('page[@id=\'{}\']/textbox/textline'.format(page_num+1)) 
            textlines = sorted(textlines, key= lambda x: -float(x.attrib['bbox'].split(',')[3]))
            
            
            line_objects = []
            for idx, item in enumerate(textlines):
                item_props = self._extract_textline_properties(item)
                bbox = item.attrib['bbox'].split(',')
                item_props["x0"] = Decimal(bbox[0])
                item_props["x1"] = Decimal(bbox[2])
                item_props["y0"] = Decimal(bbox[1])
                item_props["y1"] = Decimal(bbox[3])
                item_props["top"] = Decimal(height - float(bbox[3]))
                item_props["bottom"] = Decimal(height - float(bbox[1]))

                line_objects.append(item_props)
            page_object["lines"] = line_objects
   
            
            others = [] 
#             for key in ["rect", "figure", "layout/textgroup", "curve"]: 
            for key in ["curve", "rect", "figure"]: 
                other_objs = self.root.findall('page[@id=\'{}\']/{}'.format(page_num+1, key)) 
                for idx, item in enumerate(other_objs):
                    
                    item_props = {"type": key}
#                     print(key, ET.tostring(item))
                    bbox = item.attrib['bbox'].split(',')
                    item_props["x0"] = Decimal(bbox[0])
                    item_props["x1"] = Decimal(bbox[2])
                    item_props["y0"] = Decimal(bbox[1])
                    item_props["y1"] = Decimal(bbox[3]) 
                    item_props["top"] = Decimal(height - float(bbox[3]))
                    item_props["bottom"] = Decimal(height - float(bbox[1]))
                    others.append(item_props)
            
            page_object["others"] = others
            page = Page(page_object)
            page_object["para"] = page.para
            page_object["plines"] = page.lines
            page_object["bigbox"] = page.bigbox
            page_object["components"] = page.components

            self.pages[page_num+1] = page_object
            
            
    def _analyze_page(self, page=1): 
        pass 
    
    def _detect_cluster(self) :
        all_para = [] 
        for i in self.pages: 
            all_para.extend(self.pages[i]["para"])
    
        features = [] 
        for item in all_para:
            try:
                r, b, g = item["ncolour"][1:-1].split(",") if item["ncolour"] != 'None' and item["ncolour"] != '0' else [0,0 ,0 ]
            except:
                r, b, g = [0, 0 ,0 ]

            bold = 1 if "bold" in item["font"].lower() else 0
            features.append([float(item["size"])/6, float(r), float(b), float(g), bold])
        
        thres = 0.1
        clusters = hcluster.fclusterdata(np.array(features), thres, criterion="distance")
        
        cluster_text = defaultdict(list)
        for cluster_id, para in zip(clusters, all_para):
            cluster_text[int(cluster_id)].append(para["text"])
        
        self.cluster_text = cluster_text
        
        count = 0 
        
        for i in self.pages:
            for para_idx, _ in enumerate(self.pages[i]["para"]):
                self.pages[i]["para"][para_idx]["cluster_id"] = clusters[count]
                count += 1
        
    def parse_text(self, cluster_id):
        num_pages = len(self.pages) 
        
        active_heading = ""
        current_para = []
        heading = {} 
        
        for i in range(1, num_pages + 1):
            paras = self.pages[i]["para"]
            paras = sorted(paras, key=lambda x: -x["y0"])
            for item in paras:
                if item["cluster_id"] == cluster_id:
                    if active_heading : 
                        heading[active_heading] = current_para 
                        print(active_heading)
                        for text in current_para: 
                            print(text)
                        print("*"*10)
                        print("*"*10)

                    active_heading = item["text"]
                    current_para = []
                if active_heading: 
                    current_para.append(item["text"])
        
        if active_heading: 
            heading[active_heading] = current_para 
            print(active_heading)
            for text in current_para: 
                print(text)
            print("*"*10)
            print("*"*10)

        
    def _detect_footers(self):
        pass
    
    def _detect_headers(self):
        pass 
    
    def draw_bb(self, page=1, type="lines"):
        im = self.pdf.pages[page-1].to_image()
        if type=="lines":
            im.draw_rects(self.pages[page]["plines"])
        elif type=="others":
            im.draw_rects(self.pages[page]["others"])
        elif type=="bigbox":
            im.draw_rects(self.pages[page]["bigbox"])
        else: 
            im.draw_rects(self.pages[page]["para"])
        return im

    def _detect_clusters(self):
        pass 

    def export(self):
        data = {
            "pages": self.pages,
            "contexts": self.contexts,
            'all_lines': self.all_lines
            # "cluster_texts": self.cluster_text
        }
        return data

class ComplexEncoder(json.JSONEncoder):
     def default(self, obj):
         if isinstance(obj, Decimal):
             return float(obj)
         if isinstance(obj, np.integer):
             return int(obj)

        #  if isinstance(obj, int32):
        #      return int(obj)
         # Let the base class default method raise the TypeError
         return json.JSONEncoder.default(self, obj)

def parse(file):
    parser = PDFParser(file) 
    data = parser.export()
    return json.loads(json.dumps(data, cls=ComplexEncoder))

if __name__ == '__main__':
    parse("/Users/vivek/flutter_apps/skipping/backend/media/34962b79-3ed8-49f5-a6d7-cbb639d4065a.pdf")