import google.generativeai as genai
import argparse
import os
from dotenv import load_dotenv # Import dotenv

def load_env_file():
    """Loads environment variables from .env file in the script's directory or current working directory."""
    # Try loading .env from script's directory
    script_dir_env = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
    if os.path.exists(script_dir_env):
        load_dotenv(dotenv_path=script_dir_env)
        return True
    # Try loading .env from current working directory
    if load_dotenv(): # python-dotenv's load_dotenv() searches for .env in cwd by default
        return True
    return False

def configure_api():
    """Configures the Gemini API with the API key from environment variables."""
    # Load .env file before accessing environment variables
    load_env_file()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set.")
        exit(1)
    try:
        genai.configure(api_key=api_key)
    except Exception as e:
        print(f"Error configuring Gemini API: {e}")
        exit(1)

def format_file_content(file_path, content):
    """Formats the file content with its name, wrapped in quotes."""
    return f'File: {os.path.basename(file_path)}\n"""\n{content}\n"""'

def is_binary_file(file_path):
    """Determines if a file is binary by reading its first chunk."""
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(1024)
            return b'\0' in chunk  # Binary files typically contain null bytes
    except Exception:
        return True  # If we can't read it, treat as binary to be safe

def get_files_from_paths(file_paths, dir_paths, exclude_exts=None, exclude_names=None, max_bytes=None):
    """
    Collects and formats content from specified files and directories.
    Returns a tuple of formatted content strings and list of included files.
    """
    formatted_contents = []
    included_files = []
    total_bytes = 0
    exclude_exts = [ext.lower() for ext in (exclude_exts or [])]
    exclude_names = exclude_names or []

    def should_exclude(file_path):
        """Check if file should be excluded based on extension or name."""
        file_name = os.path.basename(file_path)
        file_ext = os.path.splitext(file_name)[1].lower()
        return file_ext in exclude_exts or file_name in exclude_names

    def process_file(file_path):
        """Process a single file - check exclusions, binary status, read and format."""
        nonlocal total_bytes
        
        if should_exclude(file_path):
            return
            
        if is_binary_file(file_path):
            print(f"Warning: Skipping binary file: {file_path}")
            return
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            content_size = len(content.encode('utf-8'))
            if max_bytes and (total_bytes + content_size > max_bytes):
                print(f"Warning: Skipping {file_path} as it would exceed the max bytes limit")
                return
                
            total_bytes += content_size
            formatted_contents.append(format_file_content(file_path, content))
            included_files.append(file_path)
        except UnicodeDecodeError:
            print(f"Warning: Skipping file with encoding issues: {file_path}")
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")

    if file_paths:
        for file_path_arg in file_paths:
            if not os.path.isfile(file_path_arg):
                print(f"Warning: File not found or is not a regular file: {file_path_arg}")
                continue
            process_file(file_path_arg)

    if dir_paths:
        for dir_path in dir_paths:
            if not os.path.isdir(dir_path):
                print(f"Warning: Directory not found: {dir_path}")
                continue
            for root, _, files_in_dir in os.walk(dir_path):
                for file_name in files_in_dir:
                    full_file_path = os.path.join(root, file_name)
                    process_file(full_file_path)
    
    return formatted_contents, included_files

def main():
    parser = argparse.ArgumentParser(description="Ask a question to the Gemini API, optionally including file or folder contents.")
    parser.add_argument("question", help="The question to ask the Gemini API.")
    parser.add_argument("-f", "--file", nargs='+', help="One or more files to include in the prompt.", default=[])
    parser.add_argument("-d", "--dir", nargs='+', help="One or more directories to include in the prompt (files will be read recursively).", default=[])
    parser.add_argument("-dr", "--dry-run", action="store_true", help="Print the prompt that would be sent to the AI and exit.")
    parser.add_argument("-o", "--output", help="File path to save the AI's response.")
    parser.add_argument("-ee", "--exclude-ext", nargs='+', help="File extensions to exclude (e.g. .jpg .png .exe).", default=[])
    parser.add_argument("-en", "--exclude-name", nargs='+', help="File names to exclude (e.g. config.json secret.txt).", default=[])
    parser.add_argument("-mb", "--max-bytes", type=int, help="Maximum total bytes to read from all files.", default=None)
    parser.add_argument("-m", "--model", default="gemini-2.0-flash", help="The Gemini model to use (e.g., gemini-2.0-flash). Default: gemini-2.0-flash")

    args = parser.parse_args()

    prompt_parts = [args.question]
    
    file_contents_formatted, included_files = get_files_from_paths(
        args.file, 
        args.dir,
        exclude_exts=args.exclude_ext,
        exclude_names=args.exclude_name,
        max_bytes=args.max_bytes
    )

    if file_contents_formatted:
        prompt_parts.append("\n\n" + "\n\n".join(file_contents_formatted))

    final_prompt = "".join(prompt_parts)

    if args.dry_run:
        print("--- Prompt for AI (Dry Run) ---")
        print(final_prompt)
        print("-------------------------------")
        print(f"\nIncluded Files Summary ({len(included_files)} files):")
        total_bytes = sum(len(open(f, 'r', encoding='utf-8').read().encode('utf-8')) for f in included_files) if included_files else 0
        print(f"Total size: {total_bytes:,} bytes")
        for i, file_path in enumerate(included_files):
            print(f"  {i+1}. {file_path}")
        return

    configure_api()

    try:
        model = genai.GenerativeModel(args.model) # Use the model from arguments
        print(f"Sending request to Gemini API using model {args.model}...")
        response = model.generate_content(final_prompt)
        
        response_text = ""
        if response.parts:
            for part in response.parts:
                response_text += part.text
        elif hasattr(response, 'text'): # Fallback for simpler response structures
             response_text = response.text
        else:
            response_text = "Error: Could not extract text from response."
            # Attempt to print the raw response for debugging if text extraction fails
            print(f"Raw response: {response}")


        if args.output:
            try:
                with open(args.output, 'w', encoding='utf-8') as f:
                    f.write(response_text)
                print(f"Response saved to {args.output}")
            except Exception as e:
                print(f"Error saving response to file {args.output}: {e}")
                print("\nAI Response:\n", response_text) # Print to console if saving fails
        else:
            print("\nAI Response:\n", response_text)

    except Exception as e:
        print(f"An error occurred while interacting with the Gemini API: {e}")

if __name__ == "__main__":
    main()
