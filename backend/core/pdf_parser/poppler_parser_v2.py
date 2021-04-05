# First post processing combine horizontal lines 
import re
import statistics
import numpy 
import os, django
from PIL import Image 
from pdf2image import convert_from_path 
import os
import base64
import tabula

from core.pdf_parser.parse_pdf import parse
HEADER_FOOTER_THRES = 70
# Threshold to match text in same line 
VERTICAL_DIFF_THRES = 7
SENT_SPAN = 3
SENT_STRIDE = 2



def _check_for_connnected( item, boxes, scale_x, scale_y):
    for box in boxes:
        # Expand bounding boxes and see if they intersect 
        ax0, ay0, ax1, ay1 = box["x0"]*scale_x, box["top"]*scale_y, box["x1"]*scale_x, box["bottom"]*scale_y
        bx0, by0, bx1, by1 = item["left"], item["top"], item["right"], item["bottom"]

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
        intersecting = True
        # If one rectangle is on left side of other 
        if(ax0 >= bx1 or ax1 <= bx0): 
            intersecting = False

        # If one rectangle is above other 
        if(ay1 <= by0 or ay0 >= by1): 
            intersecting = False
        if intersecting:
            return True


def _get_text(item): 
    data = {'text': item.text or ""} 
    text_list = [] 
    
    for key in item.attrib:
        data[key] = item.attrib[key]
    data['text'] = " ".join(item.itertext())

    for item in item.iter(): 
        if item.tag == 'b': 
            if item.text == data.get("text"):
                data['bold'] = True
                data['text'] = item.text
            else:
                data['bold'] = False
        if item.tag == 'i': 
            if item.text == data.get("text"):
                data['italics']  = True
                data['text'] = item.text
            else:
                data['italics']  = True
        if item.tag == 'text': 
            data['text'] = data.get('text') or item.text 
    return data

def _check_bullets(text): 
    pattern = r'^(\u2022|\u2023|\u25E6|\u2043|\u2219|\d\s|\d.\d\s|\d.\d.\d\s|\d\.\s|[abc]\.)\s?\s?'
    if len(re.findall(pattern, text)) > 0:
        return True
    else: 
        pattern = r'^[^A-Za-z0-9\,\s\(\)\[\]]'
        if len(re.findall(pattern, text)) > 0:
            return True
    return False

def _is_heading_candidate(item, page_width): 
    print(item)
    width_thres = 0.75*int(page_width) if item.get('is_bullet') else 0.65*int(page_width)
    if item['text'].strip() and  item['complete_bold'] and (int(item['right']) - int(item['left'])) < width_thres:
        print("yes")
        return True 
    print("NO")
    return False

def _load_pdf_n_extract_text_section(file_path):
    xml = convert_pdf_to_html(file)
    root = ET.fromstring(xml)
    pages = root.findall('page')
    page_data = {}
    all_lines = [] 
    font_map = {}
    idx = 0 
    for page_num, page in enumerate(pages): 
        fonts = root.findall('page[@number=\'{}\']/fontspec'.format(page_num+1)) 
        for font in fonts: 
            font_map[font.attrib["id"]] = {"size": font.attrib["size"], 'family': font.attrib["family"], 'color': font.attrib["color"]}

        lines = root.findall('page[@number=\'{}\']/text'.format(page_num+1)) 
        for box in lines: 
            temp = _get_text(box)
            temp['id'] = idx 
            idx += 1
            temp['page'] = page.attrib['number']
            temp["font"] = font_map[box.attrib["font"]]
            temp["left"] = int(temp["left"])
            temp["top"] = int(temp["top"])
            temp["right"] = int(temp["left"]) + int(temp["width"])
            temp["bottom"] = int(temp["top"]) + int(temp["height"])
            
            all_lines.append(temp)
        page_data[page.attrib['number']] = {"width": page.attrib["width"], "height": page.attrib["height"],}
    
    return page_data, all_lines, font_map


def _get_images(file):
    ROOT_PATH="media/images/"
    path = os.path.join(ROOT_PATH, os.path.basename(file))
    if not os.path.exists(path):
        os.makedirs(path)
        images = convert_from_path(file, 500, fmt='jpg', output_folder=path)
    images = sorted(os.listdir(path))
    file_names = [os.path.join(path, i) for i in images]
    return file_names
    
def _crop_images(image, box, box_id, page_dim):
    left, top, right, bottom = box
    im = Image.open(image) 

    # Size of the image in pixels (size of orginal image) 
    # (This is not mandatory) 
    width, height = im.size 
    pagewidth, pageheight = page_dim

    scale_w = width/pagewidth
    scale_h = height/pageheight
    # Cropped image of above dimension 
    # (It will not change orginal image) 
    im1 = im.crop((left*scale_w, top*scale_h, right*scale_w, bottom*scale_h)) 
    crop_file = image.split(".")[0] + "-" + box_id + ".jpg"
    im1.save(crop_file)
    return crop_file
    
def _merge_hz_boxes(boxes, page_data):
    top = min([int(i["top"]) for i in boxes])
    bottom = max([int(i["top"]) + int(i["height"]) for i in boxes])
    left = min([int(i["left"]) for i in boxes])
    right = min([int(i["left"]) + int(i["width"]) for i in boxes])
    temp = {"merged": boxes, "text": " ".join([i["text"] for i in boxes]), \
            "top": top, "bottom": bottom, "left": left, "right": right}
    temp["is_bullet"] = _check_bullets(temp["text"])
    temp["is_first_bold"] = boxes[0].get("bold", False)
    temp["is_last_bold"] = boxes[-1].get("bold", False)
    valid_items = []
    for idx, item in enumerate(boxes): 
        if idx == 0 and len(boxes) > 0 and temp['is_bullet']:
            continue 
        if item["text"].strip():
            valid_items.append(item)
    temp["complete_bold"] = all([i.get("bold", False) for i in  valid_items])
    temp["page"] = min([int(i["page"]) for i in boxes])
    temp['_heading_candidate'] = _is_heading_candidate(temp, page_data[str(temp["page"])]['width'])
#     temp['font'] = max([int(i['font']['size']) for i in valid_items or boxes])
    temp['font_size'] = max([int(i['font']['size']) for i in valid_items or boxes])
    temp['font'] = [i['font']['family'] for i in valid_items or boxes][0]
    temp['font_color'] = [i['font']['color'] for i in valid_items or boxes][0]        
    return temp 

def _check_for_merge(top, bottom, page_thres):
    # Check first 
    if (bottom["top"] - top["top"]) > page_thres :
        return False
    if bottom["is_bullet"] :
        return False
    if bottom["is_first_bold"] and not top["is_last_bold"]  :
        return False
    if not bottom["text"].strip(): 
        return False   
    if top['_heading_candidate']:
        return False
    if (top["font_size"] - bottom['font_size']) != 0: 
        return False
#     # Check if there is a very large gap between right coordinates of box 
#     if (page_width - top['right']) != 0: 
#         return False
    return True 




def _merge_text_boxes_same_line(all_lines, page_data):
    all_merged_lines = []
    last_line = None 
    current = []
    thresh = 10
    count = 0 
    for idz, line in enumerate(all_lines): 
        if last_line == None:
            last_line = line 
            current.append(line)
            continue
        
        # don't use items at very top or bottom
        height, width = int(page_data[line['page']]['height']), int(page_data[line['page']]['width'])

        if int(line['top']) < HEADER_FOOTER_THRES or int(line['top']) > height - HEADER_FOOTER_THRES:
            continue

        if last_line and abs(int(line["top"]) - int(last_line["top"])) < VERTICAL_DIFF_THRES : 
            current.append(line)
        else: 
            merged = _merge_hz_boxes(current, page_data)
            merged["id"] = count
            count += 1
            all_merged_lines.append(merged)
            current = [line]
            last_line = line 
    if current:
        merged = _merge_hz_boxes(current, page_data)
        merged["id"] = count
        all_merged_lines.append(merged)
    return all_merged_lines
    
def _get_page_spacing(all_hz_lines):
    diffs = [] 
    last_page = 1
    page_line_spacing = {}
    for idx  in range(len(all_hz_lines) -1):
        diff = all_hz_lines[idx+1]["top"] - all_hz_lines[idx]["top"]
        diffs.append(diff)
        if int(all_hz_lines[idx]["page"]) > last_page: 
            page_line_spacing[last_page] = numpy.percentile(diffs, 90)
            last_page += 1
            diffs = []
    print(diffs)
    page_line_spacing[last_page] = numpy.percentile(diffs, 90)
    return page_line_spacing
    
def _is_bbox_in_between(current, last, bboxes):
    valid_boxes = [] 
    for box in bboxes: 
        if box["top"] > last["top"] and box["bottom"] < current["top"]:
            valid_boxes.append(box)
    return valid_boxes 


def _get_table_boxes(file_path, page_data, page_images):
    """
    """
    parsed_data = parse(file_path)
    for page in parsed_data['pages']:
        page_image = page_images[int(page) -1]
        # Iterate over each box and scale coordinated according to poopler scale 
        for box_id, box in enumerate(parsed_data['pages'][page]['bigbox']):
            h1, w1 = parsed_data['pages'][page]['height'], parsed_data['pages'][page]['width']
            h2, w2 = float(page_data[page]['height']), float(page_data[page]['width'])
            scale_x, scale_y = h2/h1, w2/w1
            box['x0'] = box['x0']*scale_x
            box['x1'] = box['x1']*scale_x
            box['top'] = box['top']*scale_y
            box['bottom'] = box['bottom']*scale_y
            box['y0'] = box['y0']*scale_y
            box['y1'] = box['y1']*scale_y
            box_boundary = [box['x0'], box['top'], box['x1'], box['bottom']]
            page_dim = (int(page_data[page]['width']), int(page_data[page]['height']))
            box['image'] = _crop_images(page_image, box_boundary, "{}-{}".format(page, box_id), page_dim)
            box['imageb64'] = base64.b64encode(open(box['image'], "rb").read())
            parsed_data['pages'][page]['bigbox'][box_id] = box
    
    return parsed_data

def _remove_table_lines(all_lines, parsed_data):
    all_valid_lines = [ ]
    for item in all_lines: 
        boxes = parsed_data['pages'][str(item['page'])]['bigbox']
        scale_x, scale_y = 1, 1
        if not _check_for_connnected(item, boxes, scale_x, scale_y): 
            all_valid_lines.append(item) 
    return all_valid_lines


def get_contexts(all_lines):
    sentences = [] 
    current_line = ""
    current_index = []
    current_blank = 0 
    for idx, line in  enumerate(all_lines): 
        text =  line["text"].replace("\n", " ")
        temp = sent_tokenize(text)
        if text.strip() == "": 
            current_blank += 1
        if current_blank == 3: 
            sentences.append({"text": current_line, "line_index": current_index})
            current_line = ""
            current_index = []
            current_blank = 0 
            continue
        if len(temp) == 0: 
            continue
        if len(temp) == 1:
            current_line += text + " "
            current_index.append(idx)
        else:
            current_line += temp[0] 
            current_index.append(idx)
            sentences.append({"text": current_line, "line_index": current_index})
            
            for i in temp[1: -1]:
                sentences.append({"text": i, "line_index": [idx]})
            current_line = temp[-1] + " "
            current_index = [idx]
            current_blank = 0 

    contexts = [] 
    k = 3 
    stride = 2
    for idx in range(0, max(len(sentences) - k, 1), stride): 
        valid_sentences = sentences[idx: idx + k]
        context = {"text" : " ".join([i["text"] for i in valid_sentences])}
        line_idx = [] 
        for i in valid_sentences: 
            line_idx.extend(i['line_index'])
        context["rects"] = [{'height': all_lines[i]['height'], 
                            'width': all_lines[i]['width'], 
                            'left': all_lines[i]['left'], 
                            'top': all_lines[i]['top'],
                            'page': all_lines[i]['page'],
                            'page_data': page_data[all_lines[i]['page']],
                            'line_idx': i
                            } for i in line_idx]
        if len(line_idx) > 0:
            context["page"] = all_lines[line_idx[0]]['page']
            contexts.append(context)
    return all_lines, sentences,  contexts


def parse_pdf_poppler(file_path):
    """
    """
    
    page_data, all_lines, font_map = _load_pdf_n_extract_text_section(file_path)
    parsed_data = parse(file_path)
    page_images = _get_images(file_path)
    parsed_data = _get_table_boxes(file_path, page_data, page_images)        
    all_valid_lines = _remove_table_lines(all_lines, parsed_data) 
    all_hz_lines = _merge_text_boxes_same_line(all_valid_lines, page_data)
    page_line_spacing = _get_page_spacing(all_hz_lines)
    
    all_contexts = get_contexts(all_valid_lines)

    all_sections = [] 

    current = [all_hz_lines[0]]
    last_line = all_hz_lines[0] 
    for idx in range(1, len(all_hz_lines)): 
        item = all_hz_lines[idx]
        mergable = _check_for_merge(last_line, item, page_line_spacing[item["page"]])
    #     print(mergable, page_line_spacing[temp["page"]], temp["page"] )
    #     print(last_line["text"])
    #     print(item["text"])
    #     print(mergable)

        if mergable : 
            current.append(item)
            last_line = item
        else:
            top = min([int(i["top"]) for i in current])
            bottom = max([int(i["bottom"]) for i in current])
            left = min([int(i["left"]) for i in current])
            new_merged = [] 
            for x in current: 
                new_merged.extend(x["merged"])
            temp = {"merged": new_merged, "text": " ".join([i["text"] for i in current]), \
                    "top": top, "bottom": bottom, "left": "left"}
            temp["is_bullet"] = current[0]['is_bullet']
            temp["page"] = min([int(i["page"]) for i in current])
            temp["_heading_candidate"] = current[0]["_heading_candidate"]
            temp["complete_bold"] = current[0]["complete_bold"]
#             print(current[0])
            temp["color"] = tuple(int(current[0]["font_color"][i:i+2], 16) for i in (1, 3, 5))
            
            
            all_sections.append(temp)
#             print(idx, temp["page"])
#             print(temp["text"])
#             print("*"*80)
            current = [item] 
            last_line = item
    
    markdown = [] 
    last_section = None
    for section in all_sections: 
        if last_section and section: 
            page = section["page"]
            valid_boxes = _is_bbox_in_between(section, last_section, parsed_data['pages'][str(page)]['bigbox'])
            for box in valid_boxes:
#                 markdown.append('![alt text]({} "Title")'.format(box['image']))
                area = [ box['top'], box['x0'], box['bottom'], box['x1'] ]
                dfs = tabula.read_pdf(file_path, area=area, pages=int(page))
                if len(dfs) > 0: 
                    df = dfs[0]
                    df.fillna("", inplace=True)
#                     markdown.append('![Table](data:image/png;base64,{})'.format(box['imageb64'].decode('utf-8')))
                    markdown.append(df.to_html(index=False))
        if section.get("text", "").strip():
            text = []
            for item in section["merged"]:
                item_text = item.get("text")
                if item.get("bold") and not section.get("complete_bold"): 
                    item_text = "**{}**".format(item_text.strip())
                text.append(item_text.strip())
            text = " ".join(text)


            if section.get("_heading_candidate"): 
                text = "# {}".format(text.strip())
            elif section.get("complete_bold"):
                text = "**{}**".format(text.strip())
            
            if section.get("is_bullet") and not section.get("_heading_candidate"): 
                text = "- {}".format(text)
            markdown.append(text)
            markdown.append("")
            
        else: 
            markdown.append("")
        last_section = section
        
    with open("temp.md", "w") as file_:
        file_.write("\n".join(markdown))

    return {"all_lines": all_lines, "all_hz_lines": all_hz_lines, "all_sections": all_sections,\
            "page_data": page_data, 
            "context": all_contexts}
