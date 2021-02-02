import tempfile
import os 
import subprocess 
import shutil
import xml.etree.ElementTree as ET
from nltk import sent_tokenize

def convert_pdf_to_html(pdf_file, opts=None):
    tmpdir = tempfile.mkdtemp(prefix='pdf2html-')
    xml_data = ''
    try:
        xml_file = os.path.join(tmpdir, 'data') # pdf2html always adds .xml
        subprocess.check_call(['pdftohtml', '-hidden', '-nodrm', '-c', '-xml',
                               pdf_file, xml_file])
        xml_file += '.xml'
        xml_data = open(xml_file).read()
    finally:
            shutil.rmtree(tmpdir)
    return xml_data


def _get_text(item): 
    data = {'text': item.text or ""} 
    for key in item.attrib:
        data[key] = item.attrib[key]
    for item in item.iter(): 
        if item.tag == 'b': 
            data['bold'] = True
            data['text'] = item.text
        if item.tag == 'i': 
            data['italics']  = True
            data['text'] = item.text
        if item.tag == 'text': 
            data['text'] = item.text or data.get('text')
    return data


def get_contexts(path):
    xml = convert_pdf_to_html(path)
    root = ET.fromstring(xml)
    pages = root.findall('page')

    page_data = {}
    all_lines = [] 
    for page_num, page in enumerate(pages): 

        lines = root.findall('page[@number=\'{}\']/text'.format(page_num+1)) 
        print("{} Number of Lines in Page {}".format(len(lines), page_num))

        for box in lines: 
            temp = _get_text(box)
            temp['page'] = page.attrib['number']
            all_lines.append(temp)
        page_data[page.attrib['number']] = {"width": page.attrib["width"], "height": page.attrib["height"],}
    
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
    k = 5 
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