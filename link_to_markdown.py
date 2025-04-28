import requests
import sys
import argparse
from urllib.parse import quote
import time
import os
from datetime import datetime

def get_jina_markdown(url):
    """
    Fetch the actual markdown representation of a webpage using r.jina.ai
    """
    encoded_url = quote(url, safe='')
    jina_url = f"https://r.jina.ai/{encoded_url}"
    print(f"Converting {url} to markdown...")
    print(f"Fetching content from: {jina_url}")
    
    try:
        # Get the page content from r.jina.ai
        response = requests.get(jina_url)
        response.raise_for_status()
        
        # Extract the markdown content
        # The response is HTML, but r.jina.ai provides the content in a readable format
        content = response.text
        
        # Create a header for the content
        header = f"# Content from [{url}]({url})\n\n"
        
        # Add a reference to the source
        footer = f"\n\n---\n*Source: [Original URL]({url}) | [Jina URL]({jina_url})*\n\n"
        
        return header + content + footer
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching content for {url}: {e}")
        return f"# Error fetching content for [{url}]({url})\n\nError: {e}\n\n---\n"

def save_for_ai(markdown, output_dir="ai_ready"):
    """
    Save markdown content in a format optimized for AI platforms
    """
    # Create the output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Generate a timestamped filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(output_dir, f"ai_content_{timestamp}.md")
    
    # Add AI-friendly formatting
    ai_content = f"""# AI-Ready Content
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Content Summary
This file contains markdown content extracted from web pages for use with AI platforms.

## Main Content

{markdown}

## Notes for AI
- This content was automatically extracted from web pages
- Some formatting may be simplified
- References to the original sources are included
"""
    
    # Write the content to the file
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(ai_content)
    
    print(f"\nAI-ready content saved to: {filename}")
    return filename

def process_urls(urls, output_file=None, ai_format=False):
    """
    Process a list of URLs and generate markdown for each
    """
    all_markdown = ""
    
    for url in urls:
        url = url.strip()
        if not url:
            continue
            
        if not (url.startswith('http://') or url.startswith('https://')):
            url = 'https://' + url
            
        markdown = get_jina_markdown(url)
        all_markdown += markdown
        
        print(f"Added markdown for {url}")
        
        # Add a delay to avoid rate limiting
        time.sleep(1)
    
    if ai_format:
        # Save in AI-ready format
        return save_for_ai(all_markdown)
    elif output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(all_markdown)
        print(f"Markdown saved to {output_file}")
        return output_file
    else:
        print("\n--- MARKDOWN OUTPUT ---\n")
        print(all_markdown)
        return None

def main():
    parser = argparse.ArgumentParser(description="Convert web links to markdown using r.jina.ai")
    parser.add_argument('-f', '--file', help='File containing URLs (one per line)')
    parser.add_argument('-o', '--output', help='Output markdown file (default: print to stdout)')
    parser.add_argument('-a', '--ai', action='store_true', help='Format output for AI platforms')
    parser.add_argument('-d', '--dir', default='ai_ready', help='Output directory for AI-ready content (default: ai_ready)')
    parser.add_argument('urls', nargs='*', help='URLs to convert to markdown')
    
    args = parser.parse_args()
    
    urls = []
    
    # Get URLs from file if specified
    if args.file:
        try:
            with open(args.file, 'r') as f:
                urls.extend([line.strip() for line in f if line.strip()])
        except FileNotFoundError:
            print(f"Error: File {args.file} not found.")
            return 1
    
    # Add URLs from command line arguments
    if args.urls:
        urls.extend(args.urls)
    
    # If no URLs provided, prompt user to enter them
    if not urls:
        print("Enter URLs (one per line, empty line to finish):")
        while True:
            url = input().strip()
            if not url:
                break
            urls.append(url)
    
    if not urls:
        print("No URLs provided. Exiting.")
        return 1
    
    # Process the URLs with appropriate output options
    output_file = None
    if args.ai:
        output_file = process_urls(urls, None, ai_format=True)
    else:
        output_file = process_urls(urls, args.output)
    
    # If file was created, provide helpful information
    if output_file:
        print("\nTo upload to AI:")
        print(f"1. Open the file: {output_file}")
        print("2. Copy the entire content")
        print("3. Paste into the AI platform's input area")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())