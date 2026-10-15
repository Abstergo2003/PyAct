import argparse
import sys
import os
import time
from .core import map_content, process_content, build_logs

def is_cache_valid(build_tree, cache_mtime, root_dir=None):
    if root_dir is not None:
        global_file = os.path.join(root_dir, "global.py")
        if os.path.exists(global_file) and os.path.getmtime(global_file) > cache_mtime:
            return False

    file_path = os.path.join(build_tree.get("path", ""), build_tree.get("name", "") + ".pamd")
    if os.path.exists(file_path) and os.path.getmtime(file_path) > cache_mtime:
        return False
    for t in build_tree.get("templates", []):
        if not is_cache_valid(t, cache_mtime):
            return False
    return True

def main():
    """
    Main entry point for the PyAct Command Line Interface.
    
    Why it is needed:
    This acts as the bridge between the terminal and the PyAct compilation engine. 
    It parses command-line arguments, triggers the document mapping/compilation process, 
    and handles file I/O for outputting the compiled Markdown and DOCX files.
    
    Inputs (via sys.argv):
        input (str): Positional argument for the target `.pamd` file path.
        --output (str): Optional path to save the generated `.md` file.
        --docx (str): Optional path to save the generated `.docx` file.
        --css (str): Optional path to a `.css` file for styling the DOCX output.
        --lint (bool): Run the linter to check for unused files and variables.
        
    Outputs:
        Writes the generated `.md` and `.docx` files to the filesystem and prints 
        status messages to stdout/stderr.
    """
    parser = argparse.ArgumentParser(description="PyAct CLI - PAMD to Markdown compiler")
    parser.add_argument("input", help="Path to the main .pamd file")
    parser.add_argument("-o", "--output", help="Output file path (default prints to stdout)")
    parser.add_argument("--docx", help="Also generate a DOCX file at this path")
    parser.add_argument("--css", help="Optional CSS file path to style the DOCX")
    parser.add_argument("--conf", help="Optional path to pamd.conf configuration file")
    parser.add_argument("--lint", action="store_true", help="Run the linter on the project to check for unused variables and files")
    
    args = parser.parse_args()
    
    input_path = os.path.abspath(args.input)
    directory = os.path.dirname(input_path)
    filename = os.path.basename(input_path)
    
    if filename.endswith(".pamd"):
        filename = filename[:-5]
        
    if args.lint:
        from .linter import run_linter
        run_linter(filename, directory)
        return
        
    try:
        build_tree = map_content(filename, directory)
        
        cache_dir = os.path.join(directory, ".pamd-cache")
        cache_file = os.path.join(cache_dir, f"{filename}.cache.md")
        use_cache = False
        
        if os.path.exists(cache_file):
            cache_mtime = os.path.getmtime(cache_file)
            if is_cache_valid(build_tree, cache_mtime, directory):
                use_cache = True
                
        if use_cache:
            print("pamd-cache: Using cached markdown...")
            with open(cache_file, "r", encoding="utf-8") as f:
                content = f.read()
        else:
            print("pamd-cache: Cache invalid or missing. Rebuilding...")
            build_logs.clear()
            
            total_start = time.perf_counter()
            content = process_content(build_tree)
            total_end = time.perf_counter()
            total_ms = (total_end - total_start) * 1000
            
            # Write cache
            if not os.path.exists(cache_dir):
                os.makedirs(cache_dir)
            with open(cache_file, "w", encoding="utf-8") as f:
                f.write(content)
                
            # Write build log
            log_file = os.path.join(cache_dir, "build.log")
            with open(log_file, "w", encoding="utf-8") as f:
                f.write("PyAct Build Log\n")
                f.write("================\n\n")
                f.write("File Execution Times:\n")
                for log in build_logs:
                    f.write(f"- {log['file']}: {log['time_ms']:.2f} ms\n")
                f.write(f"\nTotal Build Time: {total_ms:.2f} ms\n")
        
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Successfully compiled to {args.output}")
        else:
            if not args.docx:
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
                    
            # Load pamd.conf configuration
            conf = {}
            conf_path = None
            if args.conf:
                conf_path = os.path.abspath(args.conf)
            else:
                local_conf = os.path.join(directory, "pamd.conf")
                cwd_conf = os.path.join(os.getcwd(), "pamd.conf")
                if os.path.exists(local_conf):
                    conf_path = local_conf
                elif os.path.exists(cwd_conf):
                    conf_path = cwd_conf

            if conf_path and os.path.exists(conf_path):
                from .conf_parser import conf_parser
                conf = conf_parser(conf_path)
                    
            blocks = markdown_parser(content)
            docx_writer(blocks, styles, args.docx, config=conf)
            print(f"Successfully compiled DOCX to {args.docx}")
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
