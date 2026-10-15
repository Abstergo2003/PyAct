import re
from docx import Document
from docx.shared import Pt, RGBColor, Inches, Cm, Mm
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn
import math2docx
from . import css2json


def style_parser(css_path: str) -> dict:
    """
    Parses a CSS file and converts it into a Python dictionary containing style maps.
    
    Why it is needed:
    To allow users to style their exported Word Documents using standard CSS syntax, 
    we must first translate that CSS into a structured Python dictionary that the 
    DOCX generation engine can query.
    
    Inputs:
        css_path (str): The absolute or relative file path to the target .css file.
        
    Outputs:
        dict: A nested dictionary where keys are CSS selectors (e.g., 'h1', 'p') 
              and values are dictionaries of property-value pairs (e.g., {'color': '#000', 'font-size': '12pt'}).
              Returns an empty dictionary {} if parsing fails.
    """
    try:
        return css2json.parse_css_file(css_path)
    except Exception as e:
        print(f"Warning: Could not parse CSS ({e})")
        return {}

def markdown_parser(md_text: str) -> list:
    """
    Parses raw Markdown text into a structured list of block tuples.
    
    Why it is needed:
    Because python-docx generates documents block-by-block (paragraphs, tables, headings), 
    we need to break down the raw string of Markdown text into distinct, classified chunks 
    that our DOCX writer can loop through and translate into native Word elements.
    
    Inputs:
        md_text (str): The complete raw Markdown text string.
        
    Outputs:
        list: A list of tuples where each tuple represents a block element.
              Examples: 
              - ('heading', 2, 'Title Text')
              - ('paragraph', 'Some plain text')
              - ('list', 'List item text', 'ordered')
              - ('math', 'x = 2')
              - ('table', ['|Header|', '|---|', '|Data|'])
    """
    blocks = []
    lines = md_text.split('\n')
    
    current_table = []
    
    for line in lines:
        line_s = line.strip()
        
        # Table Parsing
        if line_s.startswith('|') and line_s.endswith('|'):
            current_table.append(line_s)
            continue
        elif current_table:
            blocks.append(('table', current_table))
            current_table = []
            
        if not line_s:
            continue
            
        # Heading Parsing
        if line_s.startswith('#'):
            level = len(line_s) - len(line_s.lstrip('#'))
            text = line_s.lstrip('#').strip()
            blocks.append(('heading', level, text))
            
        # List Parsing
        elif line_s.startswith('- ') or line_s.startswith('* '):
            text = line_s[2:].strip()
            blocks.append(('list', text, 'unordered'))
            
        elif re.match(r'^\d+\.\s+', line_s):
            m = re.match(r'^(\d+)\.\s+(.*)', line_s)
            blocks.append(('list', m.group(2), 'ordered', int(m.group(1))))
            
        # Math Block Parsing
        elif (line_s.startswith('$$') and line_s.endswith('$$')) or (line_s.startswith('$') and line_s.endswith('$') and len(line_s) >= 2):
            blocks.append(('math', line_s.strip('$').strip()))
            
        # Standard Paragraph
        else:
            blocks.append(('paragraph', line_s))
            
    if current_table:
        blocks.append(('table', current_table))
        
    return blocks

def _apply_css_to_run(run, css_rules):
    """Helper to apply CSS rules to a docx run or font."""
    font = run.font if hasattr(run, 'font') else run
    
    if 'color' in css_rules:
        hex_col = css_rules['color'].replace('#', '').strip()
        if len(hex_col) == 6:
            try:
                r, g, b = tuple(int(hex_col[i:i+2], 16) for i in (0, 2, 4))
                font.color.rgb = RGBColor(r, g, b)
            except ValueError:
                pass
                
    if 'font-size' in css_rules:
        size = css_rules['font-size'].replace('pt', '').strip()
        try:
            font.size = Pt(float(size))
        except ValueError:
            pass
            
    if 'font-family' in css_rules:
        font.name = css_rules['font-family'].strip("'\"")
        
    if 'font-weight' in css_rules:
        font.bold = (css_rules['font-weight'].lower() == 'bold')
        
    if 'font-style' in css_rules:
        font.italic = (css_rules['font-style'].lower() == 'italic')
        
    if 'text-decoration' in css_rules:
        dec = css_rules['text-decoration'].lower()
        if dec == 'underline':
            font.underline = True
        elif dec == 'line-through':
            font.strike = True
        elif dec == 'none':
            font.underline = False
            font.strike = False
            
    if 'text-transform' in css_rules:
        trans = css_rules['text-transform'].lower()
        if trans == 'uppercase':
            font.all_caps = True
        elif trans == 'small-caps':
            font.small_caps = True
            
    if 'background-color' in css_rules:
        # Maps text background to highlight color index
        from docx.enum.text import WD_COLOR_INDEX
        color_map = {
            'auto': WD_COLOR_INDEX.AUTO, 'black': WD_COLOR_INDEX.BLACK, 'blue': WD_COLOR_INDEX.BLUE,
            'bright-green': WD_COLOR_INDEX.BRIGHT_GREEN, 'dark-blue': WD_COLOR_INDEX.DARK_BLUE,
            'dark-red': WD_COLOR_INDEX.DARK_RED, 'dark-yellow': WD_COLOR_INDEX.DARK_YELLOW,
            'gray-25': WD_COLOR_INDEX.GRAY_25, 'gray-50': WD_COLOR_INDEX.GRAY_50,
            'green': WD_COLOR_INDEX.GREEN, 'pink': WD_COLOR_INDEX.PINK, 'red': WD_COLOR_INDEX.RED,
            'teal': WD_COLOR_INDEX.TEAL, 'turquoise': WD_COLOR_INDEX.TURQUOISE,
            'violet': WD_COLOR_INDEX.VIOLET, 'white': WD_COLOR_INDEX.WHITE, 'yellow': WD_COLOR_INDEX.YELLOW
        }
        bg_col = css_rules['background-color'].lower()
        if bg_col in color_map:
            font.highlight_color = color_map[bg_col]

def _apply_paragraph_formatting(p, css_rules):
    """Helper to apply CSS rules to paragraph formatting."""
    fmt = p.paragraph_format
    
    if 'text-align' in css_rules:
        align = css_rules['text-align'].lower()
        if align == 'center':
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        elif align == 'right':
            p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        elif align == 'justify':
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        elif align == 'distribute':
            p.alignment = WD_ALIGN_PARAGRAPH.DISTRIBUTE
        elif align == 'left':
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            
    if 'margin-top' in css_rules:
        val = css_rules['margin-top'].replace('pt', '').strip()
        try:
            fmt.space_before = Pt(float(val))
        except ValueError:
            pass
            
    if 'margin-bottom' in css_rules:
        val = css_rules['margin-bottom'].replace('pt', '').strip()
        try:
            fmt.space_after = Pt(float(val))
        except ValueError:
            pass
            
    if 'line-height' in css_rules:
        try:
            fmt.line_spacing = float(css_rules['line-height'])
        except ValueError:
            pass
            
    if 'page-break-before' in css_rules:
        if css_rules['page-break-before'].lower() == 'always':
            fmt.page_break_before = True

import docx.opc.constants
from docx.oxml.shared import OxmlElement, qn
import urllib.request
import io
import random

def _add_internal_hyperlink(paragraph, text, anchor):
    """Adds a clickable internal hyperlink to a bookmark anchor in the docx."""
    hyperlink = OxmlElement('w:hyperlink')
    hyperlink.set(qn('w:anchor'), anchor)
    
    new_run = OxmlElement('w:r')
    rPr = OxmlElement('w:rPr')
    
    # Make it superscript since it's usually a footnote marker
    vertAlign = OxmlElement('w:vertAlign')
    vertAlign.set(qn('w:val'), 'superscript')
    rPr.append(vertAlign)
    
    # Make it blue
    c = OxmlElement('w:color')
    c.set(qn('w:val'), '0563C1')
    rPr.append(c)
    
    new_run.append(rPr)
    
    text_elem = OxmlElement('w:t')
    text_elem.text = text
    new_run.append(text_elem)
    
    hyperlink.append(new_run)
    paragraph._p.append(hyperlink)

def _add_bookmark(paragraph, text, anchor):
    """Creates a bookmark anchor in the document and places text inside it."""
    # We need a random ID to prevent collisions
    bm_id = str(random.randint(10000, 99999))
    
    bm_start = OxmlElement('w:bookmarkStart')
    bm_start.set(qn('w:id'), bm_id)
    bm_start.set(qn('w:name'), anchor)
    paragraph._p.append(bm_start)
    
    run = paragraph.add_run(text)
    
    bm_end = OxmlElement('w:bookmarkEnd')
    bm_end.set(qn('w:id'), bm_id)
    paragraph._p.append(bm_end)
    return run

def _add_hyperlink(paragraph, text, url, styles, tag):
    """Adds a real hyperlink to a docx paragraph."""
    part = paragraph.part
    r_id = part.relate_to(url, docx.opc.constants.RELATIONSHIP_TYPE.HYPERLINK, is_external=True)
    
    hyperlink = OxmlElement('w:hyperlink')
    hyperlink.set(qn('r:id'), r_id)
    
    new_run = OxmlElement('w:r')
    rPr = OxmlElement('w:rPr')
    
    c = OxmlElement('w:color')
    if 'hyperlink' in styles and 'color' in styles['hyperlink']:
        color_hex = styles['hyperlink']['color'].replace('#', '').strip()
        c.set(qn('w:val'), color_hex)
    else:
        c.set(qn('w:val'), '0563C1')
    rPr.append(c)
    
    u = OxmlElement('w:u')
    if 'hyperlink' in styles and 'text-decoration' in styles['hyperlink'] and styles['hyperlink']['text-decoration'] == 'none':
        pass
    else:
        u.set(qn('w:val'), 'single')
        rPr.append(u)
        
    new_run.append(rPr)
    
    text_elem = OxmlElement('w:t')
    text_elem.text = text
    new_run.append(text_elem)
    
    hyperlink.append(new_run)
    paragraph._p.append(hyperlink)

def _add_image(paragraph, url, caption, styles):
    """Adds an inline image fetched from URL."""
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            image_stream = io.BytesIO(response.read())
        
        run = paragraph.add_run()
        
        # Apply CSS dimensions if available
        width = None
        if 'image' in styles and 'width' in styles['image']:
            w_str = styles['image']['width']
            if 'in' in w_str: width = docx.shared.Inches(float(w_str.replace('in', '').strip()))
            
        if width:
            run.add_picture(image_stream, width=width)
        else:
            run.add_picture(image_stream, width=docx.shared.Inches(4))
            
    except Exception as e:
        paragraph.add_run(f"[Image Failed: {url}]")

def _process_inline(paragraph, text, styles, tag):
    """Parses text for images, links, math, and bold/italic."""
    # Simple regex to split by math, image, or link. Captures the match as a group.
    # Group 1: Double $$ math
    # Group 2: Single $ math
    # Group 6: Footnote definition [^1]: ...
    # Group 7: Footnote annotation [^1]
    pattern = r'(\$\$.*?\$\$)|(\$.*?\$)|(!\[.*?\]\(.*?\))|(\[.*?\]\(.*?\))|(<span.*?>.*?</span>)|(\[\^.*?\]:.*?$)|(\[\^.*?\])'
    parts = re.split(pattern, text)
    
    for part in parts:
        if not part: continue
        
        if (part.startswith('$$') and part.endswith('$$')) or (part.startswith('$') and part.endswith('$') and len(part) >= 2):
            math_text = part.strip('$').strip()
            try:
                math2docx.add_math(paragraph, math_text)
            except Exception:
                run = paragraph.add_run(part)
                if tag in styles: _apply_css_to_run(run, styles[tag])
                
        elif part.startswith('![') and part.endswith(')'):
            m = re.match(r'!\[(.*?)\]\((.*?)\)', part)
            if m:
                _add_image(paragraph, m.group(2), m.group(1), styles)
                
        elif part.startswith('[') and part.endswith(')'):
            m = re.match(r'\[(.*?)\]\((.*?)\)', part)
            if m:
                _add_hyperlink(paragraph, m.group(1), m.group(2), styles, tag)
                
        elif part.startswith('<span') and part.endswith('</span>'):
            m = re.match(r'<span.*?>(.*?)</span>', part)
            if m:
                caption_text = m.group(1)
                run = paragraph.add_run(caption_text)
                run.italic = True
                paragraph.alignment = docx.enum.text.WD_ALIGN_PARAGRAPH.CENTER
                if tag in styles: _apply_css_to_run(run, styles[tag])
                
        elif part.startswith('[^') and ']:' in part:
            # Footnote definition e.g. [^1]: The text
            m = re.match(r'\[\^(.*?)\]:\s*(.*)', part)
            if m:
                fn_id = m.group(1)
                fn_text = m.group(2)
                # Create a bookmark here for the annotation to jump to
                run = _add_bookmark(paragraph, f"[{fn_id}]: {fn_text}", f"footnote_{fn_id}")
                if tag in styles: _apply_css_to_run(run, styles[tag])
                
        elif part.startswith('[^') and part.endswith(']'):
            # Footnote annotation e.g. [^1]
            m = re.match(r'\[\^(.*?)\]', part)
            if m:
                fn_id = m.group(1)
                _add_internal_hyperlink(paragraph, f"[{fn_id}]", f"footnote_{fn_id}")
                
        else:
            # Handle plain text + bold/italic
            subparts = re.split(r'(\*\*.*?\*\*|\*.*?\*)', part)
            for subpart in subparts:
                if not subpart: continue
                if subpart.startswith('**') and subpart.endswith('**'):
                    run = paragraph.add_run(subpart[2:-2])
                    run.bold = True
                    if tag in styles: _apply_css_to_run(run, styles[tag])
                elif subpart.startswith('*') and subpart.endswith('*'):
                    run = paragraph.add_run(subpart[1:-1])
                    run.italic = True
                    if tag in styles: _apply_css_to_run(run, styles[tag])
                else:
                    run = paragraph.add_run(subpart)
                    if tag in styles: _apply_css_to_run(run, styles[tag])

def _restart_list_numbering(doc, p):
    try:
        num_part = doc.part.numbering_part
        numbering = num_part.numbering_definitions._numbering
        nums = numbering.xpath('w:num')
        if not nums: return None
        max_id = max([int(n.get(qn('w:numId'))) for n in nums])
        new_id = max_id + 1
        
        list_num = numbering.xpath('w:num[@w:numId="5"]')
        if not list_num: list_num = nums
        abstract_id = list_num[0].xpath('w:abstractNumId/@w:val')[0]
        
        new_num = OxmlElement('w:num')
        new_num.set(qn('w:numId'), str(new_id))
        ab_num_id = OxmlElement('w:abstractNumId')
        ab_num_id.set(qn('w:val'), abstract_id)
        new_num.append(ab_num_id)
        
        lvl_override = OxmlElement('w:lvlOverride')
        lvl_override.set(qn('w:ilvl'), "0")
        start_override = OxmlElement('w:startOverride')
        start_override.set(qn('w:val'), "1")
        lvl_override.append(start_override)
        new_num.append(lvl_override)
        
        numbering.append(new_num)
        
        pPr = p._p.get_or_add_pPr()
        numPr = OxmlElement('w:numPr')
        ilvl = OxmlElement('w:ilvl')
        ilvl.set(qn('w:val'), "0")
        numId_el = OxmlElement('w:numId')
        numId_el.set(qn('w:val'), str(new_id))
        numPr.append(ilvl)
        numPr.append(numId_el)
        pPr.append(numPr)
        
        return new_id
    except Exception:
        return None

def _add_xml_field(run, field_name: str):
    """Inserts a dynamic Word field (like PAGE or NUMPAGES) into a run."""
    fldChar1 = OxmlElement('w:fldChar')
    fldChar1.set(qn('w:fldCharType'), 'begin')
    instrText = OxmlElement('w:instrText')
    instrText.set(qn('xml:space'), 'preserve')
    instrText.text = f" {field_name} "
    fldChar2 = OxmlElement('w:fldChar')
    fldChar2.set(qn('w:fldCharType'), 'separate')
    t = OxmlElement('w:t')
    t.text = "1"
    fldChar3 = OxmlElement('w:fldChar')
    fldChar3.set(qn('w:fldCharType'), 'end')
    
    r = run._r
    r.append(fldChar1)
    r.append(instrText)
    r.append(fldChar2)
    r.append(t)
    r.append(fldChar3)

def _add_styled_header_footer_text(paragraph, text: str, font_rules: dict):
    """
    Appends text to a header/footer paragraph, replacing {page} and {pages}
    tokens with native Word dynamic field elements and applying font styling.
    """
    if not text:
        return
        
    pattern = r'(\{page\}|\{pages\}|\{page_number\}|\{total_pages\})'
    tokens = re.split(pattern, text, flags=re.IGNORECASE)
    
    for token in tokens:
        if not token:
            continue
        tok_lower = token.lower()
        if tok_lower in ('{page}', '{page_number}'):
            run = paragraph.add_run()
            _add_xml_field(run, 'PAGE')
            if font_rules:
                _apply_css_to_run(run, font_rules)
        elif tok_lower in ('{pages}', '{total_pages}'):
            run = paragraph.add_run()
            _add_xml_field(run, 'NUMPAGES')
            if font_rules:
                _apply_css_to_run(run, font_rules)
        else:
            run = paragraph.add_run(token)
            if font_rules:
                _apply_css_to_run(run, font_rules)

def _configure_header_or_footer(hf_obj, conf_dict: dict, section):
    """
    Configures a header or footer object (section.header or section.footer).
    Supports:
      - text / content (with align = left|center|right)
      - left / center / right 3-zone layout
      - page_number = true
      - font styling (font_name, font_size, color, italic, bold)
    """
    if not conf_dict:
        return
        
    p = hf_obj.paragraphs[0]
    p.text = ""  # Clear default empty paragraph
    
    # Extract font styling options
    font_rules = {}
    if 'font_name' in conf_dict:
        font_rules['font-family'] = conf_dict['font_name']
    elif 'font' in conf_dict:
        font_rules['font-family'] = conf_dict['font']
        
    if 'font_size' in conf_dict:
        sz = str(conf_dict['font_size']).strip()
        if not sz.endswith('pt'): sz = f"{sz}pt"
        font_rules['font-size'] = sz
    elif 'size' in conf_dict:
        sz = str(conf_dict['size']).strip()
        if not sz.endswith('pt'): sz = f"{sz}pt"
        font_rules['font-size'] = sz
        
    if 'color' in conf_dict:
        font_rules['color'] = conf_dict['color']
        
    if 'bold' in conf_dict:
        font_rules['font-weight'] = 'bold' if str(conf_dict['bold']).strip().lower() in ('true', 'yes', '1') else 'normal'
    if 'italic' in conf_dict:
        font_rules['font-style'] = 'italic' if str(conf_dict['italic']).strip().lower() in ('true', 'yes', '1') else 'normal'

    left_val = conf_dict.get('left')
    center_val = conf_dict.get('center')
    right_val = conf_dict.get('right')
    
    # Check if page_number is enabled
    has_page_num = str(conf_dict.get('page_number', '')).strip().lower() in ('true', 'yes', '1') or \
                   str(conf_dict.get('page_numbers', '')).strip().lower() in ('true', 'yes', '1')
                   
    text_val = conf_dict.get('text') or conf_dict.get('content') or conf_dict.get('title')
    
    if has_page_num and not (left_val or center_val or right_val or text_val):
        center_val = "Page {page} of {pages}"
        
    if left_val is not None or center_val is not None or right_val is not None:
        # Multi-zone layout using tab stops
        content_width = section.page_width - section.left_margin - section.right_margin
        tab_center = int(content_width // 2)
        tab_right = int(content_width)
        
        p.paragraph_format.tab_stops.add_tab_stop(tab_center, WD_TAB_ALIGNMENT.CENTER)
        p.paragraph_format.tab_stops.add_tab_stop(tab_right, WD_TAB_ALIGNMENT.RIGHT)
        
        # Left zone
        if left_val:
            _add_styled_header_footer_text(p, left_val, font_rules)
            
        # Center zone
        if center_val:
            p.add_run('\t')
            _add_styled_header_footer_text(p, center_val, font_rules)
        elif right_val:
            p.add_run('\t')
            
        # Right zone
        if right_val:
            p.add_run('\t')
            _add_styled_header_footer_text(p, right_val, font_rules)
            
    elif text_val:
        align = conf_dict.get('align', 'left').lower()
        if align == 'center':
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        elif align == 'right':
            p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        else:
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            
        _add_styled_header_footer_text(p, text_val, font_rules)

def _apply_metadata(doc, meta_conf: dict):
    if not meta_conf:
        return
        
    cp = doc.core_properties
    meta_map = {
        'author': 'author',
        'autor': 'author',
        'creator': 'author',
        'title': 'title',
        'tytul': 'title',
        'subject': 'subject',
        'temat': 'subject',
        'keywords': 'keywords',
        'slowa_kluczowe': 'keywords',
        'tags': 'keywords',
        'category': 'category',
        'kategoria': 'category',
        'comments': 'comments',
        'komentarze': 'comments',
        'description': 'comments',
        'opis': 'comments',
        'status': 'content_status',
        'content_status': 'content_status',
        'language': 'language',
        'lang': 'language',
        'jezyk': 'language',
        'version': 'version',
        'wersja': 'version',
        'revision': 'revision',
        'last_modified_by': 'last_modified_by',
        'identifier': 'identifier',
        'id': 'identifier',
    }
    
    for k, v in meta_conf.items():
        norm_k = k.strip().lower()
        attr = meta_map.get(norm_k, norm_k)
        if hasattr(cp, attr):
            try:
                setattr(cp, attr, str(v))
            except Exception:
                pass

def _parse_length(val_str: str):
    if not val_str:
        return None
    s = str(val_str).strip().lower()
    try:
        if s.endswith('in') or s.endswith('"'):
            return Inches(float(s.rstrip('in"').strip()))
        elif s.endswith('cm'):
            return Cm(float(s[:-2].strip()))
        elif s.endswith('mm'):
            return Mm(float(s[:-2].strip()))
        elif s.endswith('pt'):
            return Pt(float(s[:-2].strip()))
        else:
            return Inches(float(s))
    except ValueError:
        return None

def _apply_page_settings(doc, page_conf: dict):
    if not page_conf:
        return
        
    for s in doc.sections:
        if 'orientation' in page_conf:
            orient = page_conf['orientation'].lower()
            from docx.enum.section import WD_ORIENT
            if orient == 'landscape':
                s.orientation = WD_ORIENT.LANDSCAPE
                if s.page_width < s.page_height:
                    s.page_width, s.page_height = s.page_height, s.page_width
            elif orient == 'portrait':
                s.orientation = WD_ORIENT.PORTRAIT
                if s.page_width > s.page_height:
                    s.page_width, s.page_height = s.page_height, s.page_width
                    
        if 'size' in page_conf or 'paper_size' in page_conf:
            size_name = str(page_conf.get('size') or page_conf.get('paper_size')).lower()
            if size_name == 'a4':
                s.page_width = Mm(210)
                s.page_height = Mm(297)
            elif size_name == 'letter':
                s.page_width = Inches(8.5)
                s.page_height = Inches(11)
            elif size_name == 'legal':
                s.page_width = Inches(8.5)
                s.page_height = Inches(14)
                
        # Margins
        if 'margin' in page_conf or 'margins' in page_conf:
            m = _parse_length(page_conf.get('margin') or page_conf.get('margins'))
            if m:
                s.top_margin = m
                s.bottom_margin = m
                s.left_margin = m
                s.right_margin = m
                
        if 'margin_top' in page_conf or 'top_margin' in page_conf:
            m = _parse_length(page_conf.get('margin_top') or page_conf.get('top_margin'))
            if m: s.top_margin = m
        if 'margin_bottom' in page_conf or 'bottom_margin' in page_conf:
            m = _parse_length(page_conf.get('margin_bottom') or page_conf.get('bottom_margin'))
            if m: s.bottom_margin = m
        if 'margin_left' in page_conf or 'left_margin' in page_conf:
            m = _parse_length(page_conf.get('margin_left') or page_conf.get('left_margin'))
            if m: s.left_margin = m
        if 'margin_right' in page_conf or 'right_margin' in page_conf:
            m = _parse_length(page_conf.get('margin_right') or page_conf.get('right_margin'))
            if m: s.right_margin = m

def _apply_docx_config(doc: Document, config: dict):
    """Applies global settings from pamd.conf to the Word document."""
    if not config:
        return
        
    normalized_config = {k.lower(): v for k, v in config.items() if isinstance(v, dict)}
    
    # 1. Page settings
    page_conf = normalized_config.get('page') or normalized_config.get('margins') or normalized_config.get('document')
    if page_conf:
        _apply_page_settings(doc, page_conf)
        
    # 2. Metadata
    meta_conf = normalized_config.get('metadata')
    if meta_conf:
        _apply_metadata(doc, meta_conf)
        
    # 3. Header & Footer
    header_conf = normalized_config.get('header')
    footer_conf = normalized_config.get('footer')
    
    for section in doc.sections:
        if header_conf:
            _configure_header_or_footer(section.header, header_conf, section)
        if footer_conf:
            _configure_header_or_footer(section.footer, footer_conf, section)

def docx_writer(blocks: list, styles: dict, output_file: str, config: dict = None):
    """
    Translates parsed markdown blocks into a Word document and applies CSS styling.
    
    Why it is needed:
    This is the core generation engine. It takes the abstract syntax structure generated 
    by `markdown_parser()` and the style rules from `style_parser()`, loops through them, 
    and issues the corresponding `python-docx` commands to physically build the `.docx` file.
    
    Inputs:
        blocks (list): The list of parsed Markdown block tuples (from `markdown_parser`).
        styles (dict): The nested dictionary of CSS rules (from `style_parser`).
        output_file (str): The absolute or relative file path where the resulting .docx should be saved.
        config (dict): Optional dictionary of global settings parsed from pamd.conf (header, footer, metadata).
        
    Outputs:
        None: This function does not return a value, but it writes a binary .docx file to disk.
    """
    doc = Document()
    current_ordered_numId = None
    
    # Global document settings from pamd.conf
    if config:
        _apply_docx_config(doc, config)
    
    # Global body style
    if 'body' in styles:
        normal_style = doc.styles['Normal']
        _apply_css_to_run(normal_style, styles['body'])
        _apply_paragraph_formatting(normal_style, styles['body'])

    for block in blocks:
        btype = block[0]
        
        if btype == 'heading':
            level, text = block[1], block[2]
            p = doc.add_heading('', level=level)
            _process_inline(p, text, styles, f'h{level}')
            if f'h{level}' in styles:
                _apply_paragraph_formatting(p, styles[f'h{level}'])
                
        elif btype == 'paragraph':
            text = block[1]
            p = doc.add_paragraph()
            if 'p' in styles:
                _apply_paragraph_formatting(p, styles['p'])
            _process_inline(p, text, styles, 'p')
                
        elif btype == 'list':
            text = block[1]
            list_type = block[2] if len(block) > 2 else 'unordered'
            num_val = block[3] if len(block) > 3 else None
            
            style = 'List Number' if list_type == 'ordered' else 'List Bullet'
            p = doc.add_paragraph(style=style)
            
            if list_type == 'ordered':
                if num_val == 1:
                    new_id = _restart_list_numbering(doc, p)
                    if new_id:
                        current_ordered_numId = new_id
                elif current_ordered_numId:
                    pPr = p._p.get_or_add_pPr()
                    numPr = OxmlElement('w:numPr')
                    ilvl = OxmlElement('w:ilvl')
                    ilvl.set(qn('w:val'), "0")
                    numId_el = OxmlElement('w:numId')
                    numId_el.set(qn('w:val'), str(current_ordered_numId))
                    numPr.append(ilvl)
                    numPr.append(numId_el)
                    pPr.append(numPr)
                    
            if 'list' in styles:
                _apply_paragraph_formatting(p, styles['list'])
            _process_inline(p, text, styles, 'list')
                
        elif btype == 'math':
            math_text = block[1]
            p = doc.add_paragraph()
            try:
                math2docx.add_math(p, math_text)
                if 'equation' in styles:
                    _apply_paragraph_formatting(p, styles['equation'])
            except Exception:
                p.add_run(f"$$ {math_text} $$")
                
        elif btype == 'table':
            table_lines = block[1]
            rows = [
                [cell.strip() for cell in line.strip('|').split('|')]
                for line in table_lines if '---' not in line
            ]
            if rows:
                table = doc.add_table(rows=len(rows), cols=len(rows[0]))
                for r_idx, row in enumerate(rows):
                    for c_idx, val in enumerate(row):
                        table.cell(r_idx, c_idx).text = val
                if 'table' in styles:
                    pass

    doc.save(output_file)


if __name__ == "__main__":
    # Example Usage:
    styles = style_parser('engine/style.css')
    md_blocks = markdown_parser('## Hello World\nThis is a **bold** test.')
    docx_writer(md_blocks, styles, 'output.docx')
    