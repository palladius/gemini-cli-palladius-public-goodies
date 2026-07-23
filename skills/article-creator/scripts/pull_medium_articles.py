#!/usr/bin/env python3
import os
import sys
import re
import urllib.request
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
import html

class MediumHTMLToMarkdown(HTMLParser):
    def __init__(self):
        super().__init__()
        self.markdown = []
        self.list_stack = [] # Stack of ('ul' or 'ol', item_count)
        self.current_href = None
        self.in_code = False
        self.in_blockquote = False
        self.in_pre = False
        self.in_figcaption = False
        self.img_src = None
        self.img_alt = None

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == 'p':
            if self.in_blockquote:
                self.markdown.append('\n> ')
            else:
                self.markdown.append('\n\n')
        elif tag in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
            level = int(tag[1])
            self.markdown.append('\n\n' + '#' * level + ' ')
        elif tag in ('strong', 'b'):
            self.markdown.append('**')
        elif tag in ('em', 'i'):
            self.markdown.append('*')
        elif tag == 'a':
            self.current_href = attrs_dict.get('href', '')
            self.markdown.append('[')
        elif tag == 'blockquote':
            self.in_blockquote = True
            self.markdown.append('\n\n> ')
        elif tag == 'pre':
            self.in_pre = True
            self.markdown.append('\n\n```')
            cls = attrs_dict.get('class', '')
            lang = ''
            if 'lang-' in cls:
                lang = cls.split('lang-')[-1].split()[0]
            elif 'language-' in cls:
                lang = cls.split('language-')[-1].split()[0]
            self.markdown.append(lang + '\n')
        elif tag == 'code':
            self.in_code = True
            if not self.in_pre:
                self.markdown.append('`')
        elif tag == 'ul':
            self.list_stack.append(('ul', 0))
            self.markdown.append('\n')
        elif tag == 'ol':
            self.list_stack.append(('ol', 0))
            self.markdown.append('\n')
        elif tag == 'li':
            if self.list_stack:
                list_type, count = self.list_stack[-1]
                indent = '  ' * (len(self.list_stack) - 1)
                if list_type == 'ol':
                    count += 1
                    self.list_stack[-1] = (list_type, count)
                    self.markdown.append(f'\n{indent}{count}. ')
                else:
                    self.markdown.append(f'\n{indent}- ')
            else:
                self.markdown.append('\n- ')
        elif tag == 'img':
            self.img_src = attrs_dict.get('src', '')
            self.img_alt = attrs_dict.get('alt', 'image')
            if not self.in_figcaption:
                self.markdown.append(f'\n\n![{self.img_alt}]({self.img_src})')
        elif tag == 'figcaption':
            self.in_figcaption = True
            self.markdown.append('\n*')
        elif tag == 'hr':
            self.markdown.append('\n\n---\n\n')
        elif tag == 'br':
            self.markdown.append('\n')

    def handle_endtag(self, tag):
        if tag == 'p':
            pass
        elif tag in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
            self.markdown.append('\n\n')
        elif tag in ('strong', 'b'):
            self.markdown.append('**')
        elif tag in ('em', 'i'):
            self.markdown.append('*')
        elif tag == 'a':
            href = self.current_href or ''
            self.markdown.append(f']({href})')
            self.current_href = None
        elif tag == 'blockquote':
            self.in_blockquote = False
            self.markdown.append('\n\n')
        elif tag == 'pre':
            self.in_pre = False
            self.markdown.append('\n```\n\n')
        elif tag == 'code':
            self.in_code = False
            if not self.in_pre:
                self.markdown.append('`')
        elif tag in ('ul', 'ol'):
            if self.list_stack:
                self.list_stack.pop()
            self.markdown.append('\n')
        elif tag == 'figcaption':
            self.in_figcaption = False
            self.markdown.append('*\n')
        elif tag == 'figure':
            self.markdown.append('\n')

    def handle_data(self, data):
        if self.in_figcaption:
            self.markdown.append(data.strip())
        else:
            self.markdown.append(data)

    def get_markdown(self):
        content = ''.join(self.markdown)
        content = re.sub(r'\n{3,}', '\n\n', content)
        return content.strip()

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'[\s-]+', '-', text)
    return text.strip('-')

def clean_xml_string(xml_str):
    # Some RSS feeds might have metadata or frontmatter at the beginning
    idx = xml_str.find('<?xml')
    if idx != -1:
        return xml_str[idx:]
    return xml_str

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Pull articles from Medium RSS XML feed and save them as Markdowns")
    parser.add_argument("rss_file", nargs="?", help="Path to local RSS XML file. If not provided, will try fetching online or using standard path.")
    parser.add_argument("--dest-dir", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'references', 'personal-styie', 'riccardo-carlesso'), help="Destination directory for markdown files.")
    args = parser.parse_args()

    os.makedirs(args.dest_dir, exist_ok=True)

    xml_content = None
    if args.rss_file:
        print(f"📖 Reading RSS feed from local file: {args.rss_file}")
        with open(args.rss_file, 'r', encoding='utf-8') as f:
            xml_content = f.read()
    else:
        # Try fetching online first
        url = "https://medium.com/feed/@palladiusbonton"
        print(f"🌐 Fetching RSS feed from: {url}")
        try:
            req = urllib.request.Request(
                url, 
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
            )
            with urllib.request.urlopen(req) as response:
                xml_content = response.read().decode('utf-8')
            print("✅ Successfully fetched RSS feed online.")
        except Exception as e:
            print(f"⚠️ Failed to fetch feed online: {e}")
            # No fallback — removed hardcoded path
            fallback_path = None
            if fallback_path and os.path.exists(fallback_path):
                print(f"📖 Reading RSS feed from fallback file: {fallback_path}")
                with open(fallback_path, 'r', encoding='utf-8') as f:
                    xml_content = f.read()
            else:
                print("❌ No RSS feed content source available.")
                sys.exit(1)

    xml_content = clean_xml_string(xml_content)

    namespaces = {
        'content': 'http://purl.org/rss/1.0/modules/content/',
        'dc': 'http://purl.org/dc/elements/1.1/'
    }

    try:
        root = ET.fromstring(xml_content)
    except Exception as e:
        print(f"❌ Failed to parse XML: {e}")
        sys.exit(1)

    items = root.findall('.//item')
    print(f"📚 Found {len(items)} articles in feed.")

    for item in items:
        title = item.find('title').text
        link = item.find('link').text
        pub_date = item.find('pubDate').text
        creator = item.find('{http://purl.org/dc/elements/1.1/}creator')
        creator_text = creator.text if creator is not None else "Riccardo Carlesso"
        
        categories = [cat.text for cat in item.findall('category')]
        
        encoded_content_el = item.find('{http://purl.org/rss/1.0/modules/content/}encoded')
        if encoded_content_el is None or not encoded_content_el.text:
            print(f"⚠️ Skipping '{title}' (no encoded content)")
            continue

        html_content = encoded_content_el.text
        
        # Convert HTML to Markdown
        parser = MediumHTMLToMarkdown()
        parser.feed(html_content)
        markdown_body = parser.get_markdown()

        # Build final markdown structure
        filename = f"{slugify(title)}.md"
        dest_path = os.path.join(args.dest_dir, filename)

        frontmatter = [
            "---",
            f"title: \"{title.replace('\"', '\\\"')}\"",
            f"author: {creator_text}",
            f"pubDate: {pub_date}",
            f"link: {link}",
            f"tags: {', '.join(categories)}",
            "---",
            "",
            f"# {title}",
            "",
            f"*Originally published at [Medium]({link}) by {creator_text} on {pub_date}.*",
            "",
            markdown_body
        ]
        
        markdown_content = "\n".join(frontmatter)

        with open(dest_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        print(f"💾 Saved: {filename} -> {dest_path}")

    print("🎉 Done! All articles successfully pulled and saved as markdowns.")

if __name__ == "__main__":
    main()
