import os
import re
from docx import Document
from docx.shared import Pt, RGBColor, Inches, Cm, Mm
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT, WD_TAB_LEADER
from docx.enum.section import WD_SECTION, WD_ORIENT
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

def _parse_quote_block(quote_lines: list) -> tuple:
    """Parses a group of quote lines into an alert callout or standard blockquote."""
    clean_lines = [re.sub(r'^>\s?', '', ql).strip() for ql in quote_lines]
    first_line = clean_lines[0] if clean_lines else ""
    m = re.match(r'^\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\](?:\s+(.*))?$', first_line, re.IGNORECASE)
    if m:
        c_type = m.group(1).upper()
        header_text = m.group(2).strip() if m.group(2) else ""
        if len(clean_lines) > 1:
            title = header_text if header_text else c_type.capitalize()
            body = clean_lines[1:]
        else:
            title = c_type.capitalize()
            body = [header_text] if header_text else []
        return ('callout', c_type, title, body)
    else:
        return ('callout', 'BLOCKQUOTE', '', clean_lines)

def markdown_parser(md_text: str) -> list:
    """
    Parses raw Markdown text into a structured list of block tuples.
    """
    blocks = []
    lines = md_text.split('\n')
    
    current_table = []
    current_quote = []
    
    for line in lines:
        line_s = line.strip()
        
        # Blockquote / Callout Parsing
        if line_s.startswith('>'):
            if current_table:
                blocks.append(('table', current_table))
                current_table = []
            current_quote.append(line_s)
            continue
        elif current_quote:
            blocks.append(_parse_quote_block(current_quote))
            current_quote = []
            
        # Table Parsing
        if line_s.startswith('|') and line_s.endswith('|'):
            current_table.append(line_s)
            continue
        elif current_table:
            blocks.append(('table', current_table))
            current_table = []
            
        if not line_s:
            continue
            
        # Table of Contents Parsing
        if line_s.lower() in ('<toc/>', '<toc>', '[toc]'):
            blocks.append(('toc', 'Table of Contents'))
            
        elif re.match(r'^<toc\s+title=["\'](.*?)["\']\s*/?>', line_s, re.IGNORECASE):
            m = re.match(r'^<toc\s+title=["\'](.*?)["\']\s*/?>', line_s, re.IGNORECASE)
            blocks.append(('toc', m.group(1)))
            
        # Page Break Parsing
        elif line_s.lower() in ('<pagebreak/>', '<pagebreak>', '<page-break/>', '<pb/>', '<pb>', '<div style="page-break-after: always;"></div>'):
            blocks.append(('pagebreak',))
            
        # Section Break Parsing
        elif line_s.lower() in ('<sectionbreak/>', '<sectionbreak>', '<sb/>', '<sb>'):
            blocks.append(('sectionbreak',))
            
        # Landscape Orientation Blocks
        elif line_s.lower() in ('<landscape>', '<landscape/>'):
            blocks.append(('landscape_start',))
            
        elif line_s.lower() in ('</landscape>',):
            blocks.append(('landscape_end',))

        # Heading Parsing
        elif line_s.startswith('#'):
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
    if current_quote:
        blocks.append(_parse_quote_block(current_quote))
        
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
    """Adds an inline image fetched from URL or local file path."""
    try:
        image_stream = None
        if url.startswith(('http://', 'https://')):
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                image_stream = io.BytesIO(response.read())
        elif os.path.exists(url):
            with open(url, 'rb') as f:
                image_stream = io.BytesIO(f.read())
        elif os.path.exists(os.path.abspath(url)):
            with open(os.path.abspath(url), 'rb') as f:
                image_stream = io.BytesIO(f.read())
                
        if image_stream is None:
            paragraph.add_run(f"[Image Failed: {url}]")
            return
            
        run = paragraph.add_run()
        
        # Apply CSS dimensions if available
        width = None
        if 'image' in styles and 'width' in styles['image']:
            w_str = str(styles['image']['width']).strip().lower()
            if 'in' in w_str: width = Inches(float(w_str.replace('in', '').strip()))
            elif 'cm' in w_str: width = Cm(float(w_str.replace('cm', '').strip()))
            elif 'mm' in w_str: width = Mm(float(w_str.replace('mm', '').strip()))
            elif 'pt' in w_str: width = Pt(float(w_str.replace('pt', '').strip()))
            
        if width:
            run.add_picture(image_stream, width=width)
        else:
            run.add_picture(image_stream, width=Inches(4))
            
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

def _add_callout_box(doc, callout_type: str, title: str, body_lines: list, styles: dict):
    """Renders an alert callout box or blockquote as a styled 1x1 table."""
    table = doc.add_table(rows=1, cols=1)
    table.autofit = False
    
    theme = {
        'NOTE': {'border': '0969DA', 'bg': 'F0F7FF', 'title_col': (9, 105, 218)},
        'TIP': {'border': '1A7F37', 'bg': 'F0FFF4', 'title_col': (26, 127, 55)},
        'IMPORTANT': {'border': '8250DF', 'bg': 'F8F5FF', 'title_col': (130, 80, 223)},
        'WARNING': {'border': '9A6700', 'bg': 'FFFBEB', 'title_col': (154, 103, 0)},
        'CAUTION': {'border': 'CF222E', 'bg': 'FFF1F2', 'title_col': (207, 34, 46)},
        'BLOCKQUOTE': {'border': 'D0D7DE', 'bg': 'F6F8FA', 'title_col': (87, 96, 106)},
    }
    cfg = theme.get(callout_type.upper(), theme['NOTE'])
    
    tblPr = table._tbl.tblPr
    tblW = parse_xml(f'<w:tblW {nsdecls("w")} w:w="5000" w:type="pct"/>')
    tblPr.append(tblW)
    
    tblBorders = parse_xml(f'''
        <w:tblBorders {nsdecls("w")}>
            <w:top w:val="none"/>
            <w:left w:val="none"/>
            <w:bottom w:val="none"/>
            <w:right w:val="none"/>
            <w:insideH w:val="none"/>
            <w:insideV w:val="none"/>
        </w:tblBorders>
    ''')
    tblPr.append(tblBorders)
    
    cell = table.cell(0, 0)
    tcPr = cell._tc.get_or_add_tcPr()
    
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{cfg["bg"]}"/>')
    tcPr.append(shd)
    
    tcBorders = parse_xml(f'''
        <w:tcBorders {nsdecls("w")}>
            <w:top w:val="none"/>
            <w:left w:val="single" w:sz="36" w:space="0" w:color="{cfg['border']}"/>
            <w:bottom w:val="none"/>
            <w:right w:val="none"/>
        </w:tcBorders>
    ''')
    tcPr.append(tcBorders)
    
    tcMar = parse_xml(f'''
        <w:tcMar {nsdecls("w")}>
            <w:top w:w="120" w:type="dxa"/>
            <w:bottom w:w="120" w:type="dxa"/>
            <w:left w:w="180" w:type="dxa"/>
            <w:right w:w="180" w:type="dxa"/>
        </w:tcMar>
    ''')
    tcPr.append(tcMar)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(3)
    
    if title:
        run_title = p.add_run()
        if callout_type != 'BLOCKQUOTE':
            if title.upper() == callout_type:
                run_title.text = callout_type
            else:
                run_title.text = f"{callout_type}: {title}"
        else:
            run_title.text = title
        run_title.bold = True
        r, g, b = cfg['title_col']
        run_title.font.color.rgb = RGBColor(r, g, b)
        
    for idx, line in enumerate(body_lines):
        if not title and idx == 0:
            p_body = p
        else:
            p_body = cell.add_paragraph()
        p_body.paragraph_format.space_before = Pt(0)
        p_body.paragraph_format.space_after = Pt(2)
        _process_inline(p_body, line, styles, 'p')
        
    p_spacer = doc.add_paragraph()
    p_spacer.paragraph_format.space_before = Pt(0)
    p_spacer.paragraph_format.space_after = Pt(4)

def _add_table_of_contents(doc, title="Table of Contents", headings=None, styles=None):
    """Inserts a native Word Table of Contents with dynamic updating and pre-populated entries."""
    if headings is None:
        headings = []
    if styles is None:
        styles = {}
        
    try:
        settings = doc.settings.element
        if not settings.xpath('w:updateFields'):
            update_fields = OxmlElement('w:updateFields')
            update_fields.set(qn('w:val'), 'true')
            settings.append(update_fields)
    except Exception:
        pass
        
    if title and title.lower() not in ('none', 'false', 'no'):
        p_title = doc.add_heading(title, level=1)
        if 'h1' in styles:
            _apply_paragraph_formatting(p_title, styles['h1'])
        
    p_first = doc.add_paragraph()
    p_first.paragraph_format.space_before = Pt(2)
    p_first.paragraph_format.space_after = Pt(2)
    
    r_begin = p_first.add_run()
    fld1 = OxmlElement('w:fldChar')
    fld1.set(qn('w:fldCharType'), 'begin')
    r_begin._r.append(fld1)
    
    r_instr = p_first.add_run()
    instr = OxmlElement('w:instrText')
    instr.set(qn('xml:space'), 'preserve')
    instr.text = ' TOC \\o "1-3" \\h \\z \\u '
    r_instr._r.append(instr)
    
    r_sep = p_first.add_run()
    fld2 = OxmlElement('w:fldChar')
    fld2.set(qn('w:fldCharType'), 'separate')
    r_sep._r.append(fld2)
    
    if headings:
        base_level = min(h[1] for h in headings)
        section = doc.sections[-1]
        content_width = section.page_width - section.left_margin - section.right_margin
        
        for i, h_block in enumerate(headings):
            h_level, h_text = h_block[1], h_block[2]
            bm_name = f"_Toc_{i}"
            rel_level = h_level - base_level
            indent_in = max(0, rel_level * 0.25)
            
            p = p_first if i == 0 else doc.add_paragraph()
            p.paragraph_format.space_before = Pt(1)
            p.paragraph_format.space_after = Pt(2)
            if indent_in > 0:
                p.paragraph_format.left_indent = Inches(indent_in)
                
            tab_pos = content_width - Inches(indent_in)
            p.paragraph_format.tab_stops.add_tab_stop(tab_pos, WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)
            
            hyperlink = OxmlElement('w:hyperlink')
            hyperlink.set(qn('w:anchor'), bm_name)
            
            r_text = OxmlElement('w:r')
            t = OxmlElement('w:t')
            t.text = h_text
            r_text.append(t)
            hyperlink.append(r_text)
            
            r_tab = OxmlElement('w:r')
            tab = OxmlElement('w:tab')
            r_tab.append(tab)
            hyperlink.append(r_tab)
            
            fld_p1 = OxmlElement('w:fldChar')
            fld_p1.set(qn('w:fldCharType'), 'begin')
            r_p1 = OxmlElement('w:r')
            r_p1.append(fld_p1)
            
            instr_p = OxmlElement('w:instrText')
            instr_p.set(qn('xml:space'), 'preserve')
            instr_p.text = f' PAGEREF {bm_name} \\h '
            r_pinstr = OxmlElement('w:r')
            r_pinstr.append(instr_p)
            
            fld_p2 = OxmlElement('w:fldChar')
            fld_p2.set(qn('w:fldCharType'), 'separate')
            r_p2 = OxmlElement('w:r')
            r_p2.append(fld_p2)
            
            r_pnum = OxmlElement('w:r')
            t_pnum = OxmlElement('w:t')
            t_pnum.text = str(max(1, h_level))
            r_pnum.append(t_pnum)
            
            fld_p3 = OxmlElement('w:fldChar')
            fld_p3.set(qn('w:fldCharType'), 'end')
            r_p3 = OxmlElement('w:r')
            r_p3.append(fld_p3)
            
            hyperlink.append(r_p1)
            hyperlink.append(r_pinstr)
            hyperlink.append(r_p2)
            hyperlink.append(r_pnum)
            hyperlink.append(r_p3)
            
            p._p.append(hyperlink)
            
    p_end = doc.add_paragraph()
    p_end.paragraph_format.space_before = Pt(0)
    p_end.paragraph_format.space_after = Pt(4)
    r_end = p_end.add_run()
    fld_end = OxmlElement('w:fldChar')
    fld_end.set(qn('w:fldCharType'), 'end')
    r_end._r.append(fld_end)

def docx_writer(blocks: list, styles: dict, output_file: str, config: dict = None):
    """
    Translates parsed markdown blocks into a Word document and applies CSS styling.
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

    # Pre-scan headings for Table of Contents
    headings_for_toc = []
    toc_seen_scan = False
    for b in blocks:
        if b[0] == 'toc':
            toc_seen_scan = True
            continue
        if b[0] == 'heading' and toc_seen_scan:
            headings_for_toc.append(b)
            
    if not headings_for_toc:
        headings_for_toc = [b for b in blocks if b[0] == 'heading']

    toc_seen = False
    heading_counter = 0

    for block in blocks:
        btype = block[0]
        
        if btype == 'heading':
            level, text = block[1], block[2]
            p = doc.add_heading('', level=level)
            
            if toc_seen:
                bm_name = f"_Toc_{heading_counter}"
                bm_id = str(2000 + heading_counter)
                heading_counter += 1
                
                bm_start = OxmlElement('w:bookmarkStart')
                bm_start.set(qn('w:id'), bm_id)
                bm_start.set(qn('w:name'), bm_name)
                p._p.append(bm_start)
                
                _process_inline(p, text, styles, f'h{level}')
                
                bm_end = OxmlElement('w:bookmarkEnd')
                bm_end.set(qn('w:id'), bm_id)
                p._p.append(bm_end)
            else:
                _process_inline(p, text, styles, f'h{level}')
                
            if f'h{level}' in styles:
                _apply_paragraph_formatting(p, styles[f'h{level}'])
                
        elif btype == 'paragraph':
            text = block[1]
            p = doc.add_paragraph()
            if 'p' in styles:
                _apply_paragraph_formatting(p, styles['p'])
            _process_inline(p, text, styles, 'p')
            
        elif btype == 'callout':
            c_type, title, body_lines = block[1], block[2], block[3]
            _add_callout_box(doc, c_type, title, body_lines, styles)
                
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

        elif btype == 'toc':
            toc_seen = True
            title = block[1]
            _add_table_of_contents(doc, title, headings_for_toc, styles)
            
        elif btype == 'pagebreak':
            doc.add_page_break()
            
        elif btype == 'sectionbreak':
            doc.add_section(WD_SECTION.NEW_PAGE)
            
        elif btype == 'landscape_start':
            new_sec = doc.add_section(WD_SECTION.NEW_PAGE)
            new_sec.orientation = WD_ORIENT.LANDSCAPE
            if new_sec.page_width < new_sec.page_height:
                new_sec.page_width, new_sec.page_height = new_sec.page_height, new_sec.page_width
                
        elif btype == 'landscape_end':
            new_sec = doc.add_section(WD_SECTION.NEW_PAGE)
            new_sec.orientation = WD_ORIENT.PORTRAIT
            if new_sec.page_width > new_sec.page_height:
                new_sec.page_width, new_sec.page_height = new_sec.page_height, new_sec.page_width

    doc.save(output_file)


if __name__ == "__main__":
    # Example Usage:
    styles = style_parser('engine/style.css')
    md_blocks = markdown_parser('## Hello World\nThis is a **bold** test.')
    docx_writer(md_blocks, styles, 'output.docx')
    