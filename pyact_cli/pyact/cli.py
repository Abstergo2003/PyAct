import argparse
import sys
import os
from .core import map_content, process_content

def main():
    parser = argparse.ArgumentParser(description="PyAct CLI - PAMD to Markdown compiler")
    parser.add_argument("input", help="Path to the main .pamd file")
    parser.add_argument("-o", "--output", help="Output file path (default prints to stdout)")
    parser.add_argument("--docx", help="Also generate a DOCX file at this path")
    parser.add_argument("--css", help="Optional CSS file path to style the DOCX")
    
    args = parser.parse_args()
    
    input_path = os.path.abspath(args.input)
    directory = os.path.dirname(input_path)
    filename = os.path.basename(input_path)
    
    if filename.endswith(".pamd"):
        filename = filename[:-5]
        
    try:
        build_tree = map_content(filename, directory)
        content = process_content(build_tree)
        
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Successfully compiled to {args.output}")
        else:
            print(content)
            
        if args.docx:
            from .mdTOword import style_parser, markdown_parser, docx_writer
            styles = {}
            if args.css:
                styles = style_parser(args.css)
            else:
                # Try to look for style.css in the active directory
                local_css = os.path.join(directory, "style.css")
                if os.path.exists(local_css):
                    styles = style_parser(local_css)
                else:
                    # Fallback to the default one packaged in pyact
                    default_css = os.path.join(os.path.dirname(__file__), "style.css")
                    styles = style_parser(default_css)
                    
            blocks = markdown_parser(content)
            docx_writer(blocks, styles, args.docx)
            print(f"Successfully compiled DOCX to {args.docx}")
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
