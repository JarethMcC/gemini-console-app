# Gemini CLI Assistant

This command-line tool allows you to interact with Google's Gemini AI API, easily including file and directory contents in your prompts. 
Another use case of this tool is to use it predominantly for the dryrun functionality. This allows you to preview the prompt that will be sent to the Gemini API without actually sending it, this can be copied and pasted into any LLM.

## Features

- Ask questions to Gemini API directly from your terminal
- Include content from individual files in your prompt
- Include all files from directories (with recursive traversal)
- Preview your prompt with dry-run mode before sending
- Save AI responses to a file
- Exclude files by extension or name
- Limit total bytes to avoid exceeding API limits
- Skip binary files automatically
- Supports API key via `.env` file, environment variable.
- Customizable model selection.
- Display token usage for prompt and response.

## Prerequisites

- Python 3.6+
- A Gemini API key (get one from [Google AI Studio](https://aistudio.google.com/))

## Installation

1. Clone or download this repository
2. Install the required dependencies:
   ```
   pip install google-generativeai python-dotenv
   ```
3. Set up your Gemini API key using one of these methods:

   ### Method 1: `.env` File (Recommended)
   Create a file named `.env` in the same directory as the `gemini_cli.py` script, or in your current working directory when running the script. Add your API key to it:
   ```
   GEMINI_API_KEY="your_api_key_here"
   ```

   ### Method 2: Environment Variable
   Set an environment variable named `GEMINI_API_KEY`.
   **Windows:**
   ```
   set GEMINI_API_KEY=your_api_key_here
   ```
   
   **PowerShell:**
   ```
   $env:GEMINI_API_KEY="your_api_key_here"
   ```
   
   **Linux/macOS:**
   ```
   export GEMINI_API_KEY=your_api_key_here
   ```

## Usage

```
python gemini_cli.py "your question here" [options]
```

### Options

- `-f, --file [FILE_PATH...]`: Include content from specific file(s)
- `-d, --dir [DIR_PATH...]`: Include content from all files in directory/directories
- `-dr, --dry-run`: Preview the prompt without sending to API
- `-o, --output FILE_PATH`: Save the response to a specified file
- `-ee, --exclude-ext [EXT...]`: Exclude files with these extensions (e.g. .jpg .exe)
- `-en, --exclude-name [NAME...]`: Exclude files with these names (e.g. config.json)
- `-mb, --max-bytes BYTES`: Maximum total bytes to read from files
- `-m, --model MODEL_NAME`: Specify the Gemini model to use (default: `gemini-2.0-flash`). Check Google AI documentation for available models.
- `-tu, --token-usage`: Print the token usage for the request and response.

### Examples

**Simple question:**
```
python gemini_cli.py "What is quantum computing?"
```

**Include a specific file:**
```
python gemini_cli.py "Explain this code:" -f main.py
```

**Include multiple files:**
```
python gemini_cli.py "Compare these implementations:" -f app1.py -f app2.py
```

**Include all files from a directory:**
```
python gemini_cli.py "Review this project:" -d ./src/
```

**Preview what will be sent:**
```
python gemini_cli.py "Debug this code:" -f buggy_script.py --dry-run
```

**Save the response to a file:**
```
python gemini_cli.py "Write a unit test for this code:" -f my_function.py -o test_my_function.py
```

**Combine file and directory inputs:**
```
python gemini_cli.py "Explain the relationship between these components:" -f architecture.md -d ./src/components/
```

**Exclude specific file types:**
```
python gemini_cli.py "Analyze this codebase:" -d ./project/ --exclude-ext .jpg .png .pdf
```

**Limit total bytes read:**
```
python gemini_cli.py "Summarize this project:" -d ./src/ --max-bytes 50000
```

**Using a specific model:**
```
python gemini_cli.py "Translate this to French:" -f document.txt --model gemini-pro
```
(Note: Replace `gemini-pro` with a model name confirmed to be available for your API key and version.)

**Check token usage:**
```
python gemini_cli.py "Summarize this document:" -f report.txt --token-usage
```

## File Formatting

When files are included in your prompt, they are formatted as:

```
File: filename.ext
"""
file contents here
"""
```

This helps the AI understand the context and structure of your files.

## Error Handling

- The script will notify you if files or directories aren't found
- Binary files and files that cannot be read as text will be skipped with a warning
- If the API key is not set or invalid, you'll receive an appropriate error message
- If you encounter model not found errors (like a 404 error), try a different model name with the `--model` argument. Refer to the Google AI documentation or use the `genai.list_models()` function in a separate Python script to see available models for your API key. Example to list models:

## Tips

- For complex prompts, use `--dry-run` first to verify the prompt looks as expected
- When requesting code generation, use the `-o` flag to save the output directly to a file
- For large directories, use `--max-bytes` to limit the total content size
- Use `--exclude-ext` to skip binary or irrelevant file types like images or compiled files
- Using a `.env` file is a convenient way to manage your API key without setting system-wide environment variables.
- Use `--token-usage` to understand the cost and limits of your API calls. Token counts are also displayed in dry-run mode if this flag is active.
