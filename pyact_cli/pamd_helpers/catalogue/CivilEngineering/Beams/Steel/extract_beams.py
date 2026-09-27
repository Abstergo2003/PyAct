from bs4 import BeautifulSoup
import json
import glob
import os
from collections import defaultdict

print("Starting Dlubal HTML Beam Catalog Extractor...")

html_files = glob.glob("*.html")

for file_path in html_files:
    print(f"\nParsing '{file_path}'... (This may take 30-60 seconds due to file size)")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')
        
    # Store raw extracted series before disambiguation
    raw_series_list = []
    series_name_counts = defaultdict(int)
    
    # 1. Find all series wrappers
    for wrapper in soup.find_all('div', class_='tables__wrapper-row'):
        img_details = wrapper.find('div', class_='header__image-details')
        if not img_details:
            continue
            
        title_tag = img_details.find(['h3', 'h2'], class_='title')
        if not title_tag:
            continue
            
        base_series_name = title_tag.text.strip()
        
        # Extract metadata (manufacturer/standard) for potential disambiguation
        lis = img_details.find_all('li')
        li_texts = [li.text.strip() for li in lis if li.text.strip() and li.text.strip() != "--"]
        series_suffix = f" ({', '.join(li_texts)})" if li_texts else ""
        
        # Extract column headers for this specific series table
        headers = []
        thead = wrapper.find('thead')
        if thead:
            # The last row of the header usually contains the actual variable names (h[mm], A[cm2], etc)
            header_trs = thead.find_all('tr')
            if header_trs:
                last_header_tr = header_trs[-1]
                for th in last_header_tr.find_all('th'):
                    text = th.text.strip()
                    
                    # Convert Greek letters to Latin equivalents (e.g., Iω -> Iw, α -> alpha)
                    greek_to_latin = {
                        'α': 'alpha', 'β': 'beta', 'γ': 'gamma', 'δ': 'delta', 'ε': 'eps',
                        'ζ': 'zeta', 'η': 'eta', 'θ': 'theta', 'ι': 'iota', 'κ': 'kappa',
                        'λ': 'lambda', 'μ': 'mu', 'ν': 'nu', 'ξ': 'xi', 'ο': 'o',
                        'π': 'pi', 'ρ': 'rho', 'σ': 'sigma', 'τ': 'tau', 'υ': 'upsilon',
                        'φ': 'phi', 'χ': 'chi', 'ψ': 'psi', 'ω': 'w',
                        'Α': 'Alpha', 'Β': 'Beta', 'Γ': 'Gamma', 'Δ': 'Delta', 'Ε': 'Eps',
                        'Ζ': 'Zeta', 'Η': 'Eta', 'Θ': 'Theta', 'Ι': 'Iota', 'Κ': 'Kappa',
                        'Λ': 'Lambda', 'Μ': 'Mu', 'Ν': 'Nu', 'Ξ': 'Xi', 'Ο': 'O',
                        'Π': 'Pi', 'Ρ': 'Rho', 'Σ': 'Sigma', 'Τ': 'Tau', 'Υ': 'Upsilon',
                        'Φ': 'Phi', 'Χ': 'Chi', 'Ψ': 'Psi', 'Ω': 'W'
                    }
                    for greek, latin in greek_to_latin.items():
                        text = text.replace(greek, latin)
                        
                    # Skip empty headers or the 'Section' header (since Section name is handled separately)
                    # Also skip the select all checkbox header
                    if text and text.lower() not in ["section", "select all"]:
                        headers.append(text)
        
        # Extract beams for this series
        beams_in_series = {}
        for tr in wrapper.find_all('tr'):
            name_tag = tr.find('div', class_='series-name')
            if not name_tag:
                continue
                
            beam_name = name_tag.text.strip()
            cells = tr.find_all('td', class_='tsl-cell')
            
            if not cells or len(cells) < len(headers):
                continue
                
            data = {}
            for i, cell in enumerate(cells):
                if i < len(headers):
                    val_text = cell.text.strip()
                    try:
                        # Try to parse as float
                        data[headers[i]] = float(val_text)
                    except ValueError:
                        # Fallback to string if it's 'N/A' or similar
                        data[headers[i]] = val_text
                        
            beams_in_series[beam_name] = data
                
        if beams_in_series:
            raw_series_list.append({
                "base_name": base_series_name,
                "suffix": series_suffix,
                "beams": beams_in_series
            })
            series_name_counts[base_series_name] += 1
            
    # 2. Build the final structured and optionally disambiguated catalog
    catalog = {}
    total_beams = 0
    
    for series in raw_series_list:
        # Only append suffix if there is a collision in the base series name
        if series_name_counts[series["base_name"]] > 1 and series["suffix"]:
            final_series_name = series["base_name"] + series["suffix"]
        else:
            final_series_name = series["base_name"]
            
        catalog[final_series_name] = series["beams"]
        total_beams += len(series["beams"])

    # 3. Save to JSON
    output_filename = file_path.replace('.html', '.json')
    with open(output_filename, 'w', encoding='utf-8') as out_f:
        json.dump(catalog, out_f, indent=4)
        
    print(f"✅ Extracted {total_beams} beams across {len(catalog)} series to '{output_filename}'!")

print("\nAll files processed!")
