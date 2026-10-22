import argparse
import sys
import time
import shutil
from pathlib import Path
from .core import map_content, process_content, build_logs, generate_markdown_toc

def _cache_dependencies(root_dir: Path) -> list[Path]:
    dependencies = [
        root_dir / "global.py",
        root_dir / "pamd.conf",
        root_dir / "style.css",
    ]
    helper_dir = Path(__file__).parents[1] / "pamd_helpers"
    if helper_dir.exists():
        dependencies.extend(helper_dir.glob("*.py"))
    return dependencies


def is_cache_valid(build_tree, cache_mtime, root_dir=None, dependencies=None):
    root_dir = Path(root_dir) if root_dir is not None else None
    if dependencies is None and root_dir is not None:
        dependencies = _cache_dependencies(root_dir)
    for dependency in dependencies or []:
        if dependency.exists() and dependency.stat().st_mtime > cache_mtime:
            return False

    file_path = Path(build_tree["source_path"])
    if file_path.exists() and file_path.stat().st_mtime > cache_mtime:
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
    if len(sys.argv) > 1 and sys.argv[1] == "init":
        init_parser = argparse.ArgumentParser(description="PyAct Project Initializer")
        init_parser.add_argument("command", choices=["init"])
        init_parser.add_argument("name", nargs="?", default=".", help="Project folder name (default: current directory)")
        init_parser.add_argument("--template", choices=["default", "engineering", "academic"], default="default", help="Project template to scaffold")
        init_args = init_parser.parse_args()
        from .scaffold import init_project
        init_project(init_args.name, init_args.template)
        return

    parser = argparse.ArgumentParser(description="PyAct CLI - PAMD to Markdown compiler")
    parser.add_argument("input", help="Path to the main .pamd file")
    parser.add_argument("-o", "--output", help="Output file path (default prints to stdout)")
    parser.add_argument("--docx", help="Also generate a DOCX file at this path")
    parser.add_argument("--css", help="Optional CSS file path to style the DOCX")
    parser.add_argument("--conf", help="Optional path to pamd.conf configuration file")
    parser.add_argument("--lint", action="store_true", help="Run the linter on the project to check for unused variables and files")
    parser.add_argument("--no-cache", action="store_true", help="Rebuild the document without reading the cache")
    parser.add_argument("--clear-cache", action="store_true", help="Remove the project cache before compiling")
    
    args = parser.parse_args()
    
    input_path = Path(args.input).resolve()
    directory = input_path.parent
    filename = input_path.name
    
    if filename.endswith(".pamd"):
        filename = filename[:-5]
        
    if args.lint:
        from .linter import run_linter
        if not run_linter(filename, directory):
            sys.exit(1)
        return
        
    try:
        build_tree = map_content(filename, directory)
        
        cache_dir = directory / ".pamd-cache"
        cache_file = cache_dir / f"{filename}.cache.md"
        use_cache = False

        if args.clear_cache and cache_dir.exists():
            shutil.rmtree(cache_dir)
        
        if not args.no_cache and cache_file.exists():
            cache_mtime = cache_file.stat().st_mtime
            if is_cache_valid(
                build_tree,
                cache_mtime,
                directory,
                _cache_dependencies(directory),
            ):
                use_cache = True
                
        if use_cache:
            print("pamd-cache: Using cached markdown...")
            with cache_file.open("r", encoding="utf-8") as f:
                content = f.read()
        else:
            print("pamd-cache: Cache invalid or missing. Rebuilding...")
            build_logs.clear()
            
            total_start = time.perf_counter()
            content = process_content(build_tree)
            total_end = time.perf_counter()
            total_ms = (total_end - total_start) * 1000
            
            # Write cache
            cache_dir.mkdir(parents=True, exist_ok=True)
            with cache_file.open("w", encoding="utf-8") as f:
                f.write(content)
                
            # Write build log
            log_file = cache_dir / "build.log"
            with log_file.open("w", encoding="utf-8") as f:
                f.write("PyAct Build Log\n")
                f.write("================\n\n")
                f.write("File Execution Times:\n")
                for log in build_logs:
                    f.write(f"- {log['file']}: {log['time_ms']:.2f} ms\n")
                f.write(f"\nTotal Build Time: {total_ms:.2f} ms\n")
        
        md_output = generate_markdown_toc(content)
        if args.output:
            with Path(args.output).open("w", encoding="utf-8") as f:
                f.write(md_output)
            print(f"Successfully compiled to {args.output}")
        else:
            if not args.docx:
                print(md_output)
            
        if args.docx:
            from .mdTOword import style_parser, markdown_parser, docx_writer
            styles = {}
            if args.css:
                styles = style_parser(args.css)
            else:
                # Try to look for style.css in the active directory
                local_css = directory / "style.css"
                if local_css.exists():
                    styles = style_parser(local_css)
                else:
                    # Fallback to the default one packaged in pyact
                    default_css = Path(__file__).parent / "style.css"
                    styles = style_parser(default_css)
                    
            # Load pamd.conf configuration
            conf = {}
            conf_path = None
            if args.conf:
                conf_path = Path(args.conf).resolve()
            else:
                local_conf = directory / "pamd.conf"
                cwd_conf = Path.cwd() / "pamd.conf"
                if local_conf.exists():
                    conf_path = local_conf
                elif cwd_conf.exists():
                    conf_path = cwd_conf

            if conf_path and conf_path.exists():
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
