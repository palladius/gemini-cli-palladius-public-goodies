import argparse
import urllib.request
import sys

def fetch_content(url):
    try:
        with urllib.request.urlopen(url) as response:
            return response.read().decode('utf-8')
    except Exception as e:
        print(f"Error fetching {url}: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Fetch ADK context files.")
    parser.add_argument("--type", choices=["summary", "full"], required=True, help="Type of content to fetch.")
    args = parser.parse_args()

    urls = {
        "summary": "https://raw.githubusercontent.com/google/adk-python/main/llms.txt",
        "full": "https://raw.githubusercontent.com/google/adk-python/main/llms-full.txt"
    }

    content = fetch_content(urls[args.type])
    
    # Print the content for the LLM to consume
    print(f"--- START OF ADK {args.type.upper()} CONTENT ---")
    # For 'full', we might want to truncate or just print it all if requested.
    # Given the 1.2MB size, we print it all but warn the agent.
    print(content)
    print(f"--- END OF ADK {args.type.upper()} CONTENT ---")

if __name__ == "__main__":
    main()
