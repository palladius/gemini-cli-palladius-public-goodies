#!/usr/bin/env ruby

=begin
This script automates the creation of a new developer advocate article folder structure.
It parses command-line arguments (title, bug, cta, intent, date, tags) and generates
standardized files (ARTICLE.md, PLAN.md, TODO.md, SOURCES.md, AI_REASONING.md, HERO_IMAGE_PROMPT.md)
based on template files located in the `references/` folder.
=end

require 'optparse'
require 'date'
require 'fileutils'
require 'socket'

GENERATOR_VERSION = '1.2'

# Default values
options = {
  bug: 'b/TODO',
  cta: '',
  intent: 'No intent specified.',
  date: Date.today,
  tags: '',
  platform: 'TBD',
  publish_date: (Date.today + 7).strftime("%Y-%m-%d"),
  dry_run: false,
  articles_dir: '/usr/local/google/home/ricc/git/ricclife-with-gemini-pvt/work/articles'
}

OptionParser.new do |opts|
  opts.banner = "Usage: create_article.rb [options]"

  opts.on("-t", "--title TITLE", "Title of the article (required)") do |v|
    options[:title] = v
  end

  opts.on("-b", "--bug BUG", "Buganizer ID (defaults to b/TODO)") do |v|
    options[:bug] = v
  end

  opts.on("-c", "--cta CTA", "Call to Action URL") do |v|
    options[:cta] = v
  end

  opts.on("-i", "--intent INTENT", "Intent / summary of the article") do |v|
    options[:intent] = v
  end

  opts.on("-d", "--date DATE", "Date in YYYY-MM-DD format (defaults to today)") do |v|
    options[:date] = Date.parse(v) rescue Date.today
  end

  opts.on("-p", "--platform PLATFORM", "Target publishing platform (defaults to TBD)") do |v|
    options[:platform] = v
  end

  opts.on("--publish-date DATE", "Target publication date YYYY-MM-DD (defaults to 7 days from now)") do |v|
    options[:publish_date] = Date.parse(v).strftime("%Y-%m-%d") rescue (Date.today + 7).strftime("%Y-%m-%d")
  end

  opts.on("--tags TAGS", "Comma-separated tags") do |v|
    options[:tags] = v
  end

  opts.on("-n", "--dry-run", "Run in dry-run mode without creating files") do
    options[:dry_run] = true
  end

  opts.on("--articles-dir DIR", "Root articles directory") do |v|
    options[:articles_dir] = v
  end
end.parse!

if options[:title].nil? || options[:title].empty?
  puts "❌ Error: --title is required."
  exit 1
end

# Process bug format
bug_id = options[:bug]
unless bug_id.start_with?("b/")
  if bug_id =~ /^\d+$/
    bug_id = "b/#{bug_id}"
  else
    bug_id = "b/#{bug_id.sub(/^b\/?/, '')}"
  end
end

# Format slug
def slugify(text)
  # Strip tags like [article], convert to lowercase, replace special characters with hyphens
  t = text.gsub(/\[.*?\]/, '')
  t = t.downcase
  t = t.gsub(/[^a-z0-9\s-]/, '')
  t = t.gsub(/[\s-]+/, '-')
  t.sub(/^-/, '').sub(/-$/, '')
end

date_str = options[:date].strftime("%Y%m%d")
title_slug = slugify(options[:title])
folder_name = "#{date_str}-#{title_slug}"
target_dir = File.join(options[:articles_dir], folder_name)

# Validate that the articles root directory exists
articles_root = File.expand_path(options[:articles_dir])
unless Dir.exist?(articles_root)
  puts "❌ Error: Articles root directory '#{articles_root}' does not exist."
  puts "   Please make sure your repository is checked out and the path is correct."
  exit 1
end

# Get user and host
user = ENV['USER'] || ENV['USERNAME'] || 'ricc'
begin
  host = Socket.gethostname
rescue
  host = 'derek.zrh.corp.google.com'
end

puts "📂 Creating article folder structure under: #{target_dir}"

if options[:dry_run]
  puts "⚠️ Dry run active - no directories or files will be created."
  puts "Planned Folder: #{target_dir}"
  exit 0
end

FileUtils.mkdir_p(target_dir)

# Define script root and templates directory
script_dir = File.expand_path(File.dirname(__FILE__))
templates_dir = File.expand_path(File.join(script_dir, "..", "references", "templates"))

# Load and format templates
def load_template(templates_dir, filename)
  path = File.join(templates_dir, filename)
  return "" unless File.exist?(path)
  File.read(path)
end

# 1. ARTICLE.md
article_tpl = load_template(templates_dir, "ARTICLE.md")
if article_tpl != ""
  article_content = article_tpl
    .gsub("{title}", options[:title])
    .gsub("{user}", user)
    .gsub("{host}", host)
    .gsub("{bug}", bug_id)
    .gsub("{tags}", options[:tags])
    .gsub("{cta}", options[:cta])
    .gsub("{intent}", options[:intent])
    .gsub("{generator}", File.basename(__FILE__))
    .gsub("{version}", GENERATOR_VERSION)
    .gsub("{platform}", options[:platform])
    .gsub("{publish_date}", options[:publish_date])
  
  File.write(File.join(target_dir, "ARTICLE.md"), article_content)
  puts "📝 Created: ARTICLE.md"
end

# 2. PLAN.md
plan_tpl = load_template(templates_dir, "PLAN.md")
if plan_tpl != ""
  File.write(File.join(target_dir, "PLAN.md"), plan_tpl)
  puts "📝 Created: PLAN.md"
end

# 3. 01-CREATION.md
creation_tpl = load_template(templates_dir, "01-CREATION.md")
if creation_tpl != ""
  File.write(File.join(target_dir, "01-CREATION.md"), creation_tpl)
  puts "📝 Created: 01-CREATION.md"
end

# 4. 90-COMPLETION-LIST.md
completion_tpl = load_template(templates_dir, "90-COMPLETION-LIST.md")
if completion_tpl != ""
  File.write(File.join(target_dir, "90-COMPLETION-LIST.md"), completion_tpl)
  puts "📝 Created: 90-COMPLETION-LIST.md"
end

# 5. 99-SIGNOFF-TODO.md
signoff_tpl = load_template(templates_dir, "99-SIGNOFF-TODO.md")
if signoff_tpl != ""
  File.write(File.join(target_dir, "99-SIGNOFF-TODO.md"), signoff_tpl)
  puts "📝 Created: 99-SIGNOFF-TODO.md"
end

# 6. TODOs.md
todos_tpl = load_template(templates_dir, "TODOs.md")
if todos_tpl != ""
  File.write(File.join(target_dir, "TODOs.md"), todos_tpl)
  puts "📝 Created: TODOs.md"
end

# 7. SOURCES.md
sources_tpl = load_template(templates_dir, "SOURCES.md")
if sources_tpl != ""
  File.write(File.join(target_dir, "SOURCES.md"), sources_tpl)
  puts "📝 Created: SOURCES.md"
end

# 8. 50-WORKING-DOC.md
working_doc_tpl = load_template(templates_dir, "50-WORKING-DOC.md")
if working_doc_tpl != ""
  working_doc_content = working_doc_tpl
    .gsub("{intent}", options[:intent])
    .gsub("{date}", options[:date].strftime("%Y-%m-%d"))
  
  File.write(File.join(target_dir, "50-WORKING-DOC.md"), working_doc_content)
  puts "📝 Created: 50-WORKING-DOC.md"
end

# 9. README.md
readme_tpl = load_template(templates_dir, "README.md")
if readme_tpl != ""
  File.write(File.join(target_dir, "README.md"), readme_tpl)
  puts "📝 Created: README.md"
end

# 10. Empty and additional files
File.write(File.join(target_dir, "AI_REASONING.md"), "# AI Reasoning\n\n- Put drafts, outline notes, and research findings here.\n")
puts "📝 Created: AI_REASONING.md"

File.write(File.join(target_dir, "HUMAN_REASONING.md"), "# Human Reasoning\n\n- Put human drafts, outline notes, and research findings here.\n")
puts "📝 Created: HUMAN_REASONING.md"

File.write(File.join(target_dir, "HERO_IMAGE_PROMPT.md"), "# Hero Image Prompt\n\nProvide the visual description for the image generation tool here.\n")
puts "📝 Created: HERO_IMAGE_PROMPT.md"

puts "\n🎉 Success! Article folder initialized successfully."
puts "👉 Folder: #{target_dir}"
