import argparse
import sys
import os
from .core import map_content, process_content

def main():
    parser = argparse.ArgumentParser(description="PyAct CLI - PAMD to Markdown compiler")
    parser.add_argument("input", help="Path to the main .pamd file")
    parser.add_argument("-o", "--output", help="Output file path (default prints to stdout)")
    
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
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
