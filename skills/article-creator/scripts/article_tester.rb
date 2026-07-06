#!/usr/bin/env ruby

=begin
This script tests a given article directory for compliance with the CarlessianArticle standards.
It checks for:
1. Presence of required files (ARTICLE.md, PLAN.md, TODO.md, SOURCES.md, AI_REASONING.md, HERO_IMAGE_PROMPT.md)
2. Valid YAML frontmatter in ARTICLE.md
3. Checklist format in PLAN.md and TODO.md
4. Division of public/private sections in SOURCES.md
5. Non-leakage of private links into the public ARTICLE.md file
=end

require 'optparse'
require 'yaml'
require 'json'

options = {
  folder: nil,
  semantic: false
}

OptionParser.new do |opts|
  opts.banner = "Usage: article_tester.rb [options]"

  opts.on("-f", "--folder FOLDER", "Article folder path to test (required)") do |v|
    options[:folder] = v
  end

  opts.on("-s", "--semantic", "Run semantic alignment checks using Gemini CLI") do
    options[:semantic] = true
  end
end.parse!

if options[:folder].nil? || options[:folder].empty?
  puts "❌ Error: --folder path is required."
  exit 1
end

folder = File.expand_path(options[:folder])

unless Dir.exist?(folder)
  puts "❌ Error: Folder '#{folder}' does not exist."
  exit 1
end

errors = []
successes = []

# Helper to check file existence
def check_file(folder, filename, errors, successes)
  path = File.join(folder, filename)
  if File.exist?(path)
    successes << "✅ File '#{filename}' exists."
    path
  else
    errors << "❌ Missing required file: '#{filename}'."
    nil
  end
end

puts "🔍 Testing article folder: #{folder}\n\n"

# 1. Check required files
article_path = check_file(folder, "ARTICLE.md", errors, successes)
plan_path = check_file(folder, "PLAN.md", errors, successes)
creation_path = check_file(folder, "01-CREATION.md", errors, successes)
completion_path = check_file(folder, "90-COMPLETION-LIST.md", errors, successes)
signoff_path = check_file(folder, "99-SIGNOFF-TODO.md", errors, successes)
todos_path = check_file(folder, "TODOs.md", errors, successes)
sources_path = check_file(folder, "SOURCES.md", errors, successes)
check_file(folder, "AI_REASONING.md", errors, successes)
check_file(folder, "HUMAN_REASONING.md", errors, successes)
check_file(folder, "HERO_IMAGE_PROMPT.md", errors, successes)
check_file(folder, "50-WORKING-DOC.md", errors, successes)
check_file(folder, "README.md", errors, successes)

# 2. Check ARTICLE.md structure and frontmatter
if article_path
  content = File.read(article_path)
  
  # Ensure it has frontmatter delimiters
  if content =~ /\A---.*?^(---|\.\.\.)/m
    frontmatter_text = $&
    begin
      fm = YAML.safe_load(frontmatter_text)
      successes << "✅ ARTICLE.md frontmatter is valid YAML."
      
      # Validate required keys
      required_keys = %w[Harness Model Title User Host Bug CTA Status Generator Version Platform PublishDate]
      required_keys.each do |key|
        if fm.has_key?(key)
          successes << "✅ Frontmatter key '#{key}' is present."
        else
          errors << "❌ Frontmatter key '#{key}' is missing in ARTICLE.md."
        end
      end
    rescue => e
      errors << "❌ Failed to parse YAML frontmatter in ARTICLE.md: #{e.message}"
    end
  else
    errors << "❌ ARTICLE.md does not start with a valid YAML frontmatter block (delimited by ---)."
  end

  # Check if ## Intent section is present and >= 500 characters
  if content =~ /##\s*Intent\s*\n(.*?)(?=##|\z)/mi
    intent_text = $1.strip
    if intent_text.length < 500
      errors << "❌ ARTICLE.md intent section is too short (#{intent_text.length} chars). It must be at least 500 characters."
    else
      successes << "✅ ARTICLE.md intent section is sufficiently detailed (#{intent_text.length} chars)."
    end
  else
    errors << "❌ ARTICLE.md is missing a '## Intent' section."
  end
end

# 3. Check PLAN.md format
if plan_path
  content = File.read(plan_path)
  if content =~ /- \[[ xX]\]/
    successes << "✅ PLAN.md contains checklists (- [ ] or - [x])."
  else
    errors << "❌ PLAN.md does not appear to contain any checklist items (e.g. '- [ ]' or '- [x]')."
  end
end

# 4. Check 01-CREATION.md format
if creation_path
  content = File.read(creation_path)
  if content =~ /- \[[ xX]\]/
    successes << "✅ 01-CREATION.md contains checklists (- [ ] or - [x])."
  else
    errors << "❌ 01-CREATION.md does not appear to contain any checklist items (e.g. '- [ ]' or '- [x]')."
  end
end

# 5. Check 90-COMPLETION-LIST.md format
if completion_path
  content = File.read(completion_path)
  if content =~ /- \[[ xX]\]/
    successes << "✅ 90-COMPLETION-LIST.md contains checklists (- [ ] or - [x])."
  else
    errors << "❌ 90-COMPLETION-LIST.md does not appear to contain any checklist items (e.g. '- [ ]' or '- [x]')."
  end
end

# 6. Check 99-SIGNOFF-TODO.md format
if signoff_path
  content = File.read(signoff_path)
  if content =~ /- \[[ xX]\]/
    successes << "✅ 99-SIGNOFF-TODO.md contains checklists (- [ ] or - [x])."
  else
    errors << "❌ 99-SIGNOFF-TODO.md does not appear to contain any checklist items (e.g. '- [ ]' or '- [x]')."
  end
end

# 7. Check TODOs.md format
if todos_path
  content = File.read(todos_path)
  if content =~ /- \[[ xX]\]/
    successes << "✅ TODOs.md contains checklists (- [ ] or - [x])."
  else
    errors << "❌ TODOs.md does not appear to contain any checklist items (e.g. '- [ ]' or '- [x]')."
  end
end

# 8. Check SOURCES.md public/private headers and leak check
if sources_path && article_path
  sources_content = File.read(sources_path)
  article_content = File.read(article_path)
  
  if sources_content =~ /##\s*Public/i
    successes << "✅ SOURCES.md contains '## Public' section."
  else
    errors << "❌ SOURCES.md is missing '## Public' section."
  end
  
  if sources_content =~ /##\s*Private/i
    successes << "✅ SOURCES.md contains '## Private' section."
    
    # Parse private links to make sure they aren't in ARTICLE.md
    parts = sources_content.split(/##\s*Private/i)
    if parts.size > 1
      private_section = parts[1]
      # Match standard markdown links and absolute URLs
      private_links = private_section.scan(/https?:\/\/[^\s\)\>\]]+/i)
      
      private_links.each do |link|
        # Clean trailing punctuation from URLs
        clean_link = link.sub(/[\.\,\;\:\?\!]+$/, '')
        if article_content.include?(clean_link)
          errors << "❌ Private link leak: '#{clean_link}' in SOURCES.md is leaked inside ARTICLE.md!"
        end
      end
    end
  else
    errors << "❌ SOURCES.md is missing '## Private' section."
  end
end

# 9. Check that 99-SIGNOFF-TODO.md has reviews section checked if finalized
# (This can be manually filled out by the user or reviewer)

# 10. Semantic Unit Test (if gemini CLI is invoked)
if options[:semantic] && article_path
  ai_path = File.join(folder, "AI_REASONING.md")
  human_path = File.join(folder, "HUMAN_REASONING.md")
  
  if File.exist?(ai_path) && File.exist?(human_path)
    puts "🧠 Running semantic alignment test (comparing ARTICLE.md with AI & Human reasoning)..."
    
    ai_reasoning = File.read(ai_path)
    human_reasoning = File.read(human_path)
    article_draft = File.read(article_path)
    
    prompt = <<~PROMPT
      You are an AI compliance validator checking if an article draft correctly synthesizes and represents the core ideas, sections, and concerns from both the AI reasoning and Human reasoning documents.
      
      --- AI REASONING ---
      #{ai_reasoning}
      
      --- HUMAN REASONING ---
      #{human_reasoning}
      
      --- ARTICLE DRAFT ---
      #{article_draft}
      
      Verify if the ARTICLE DRAFT correctly represents the main themes and outlines from both the AI and Human reasoning documents.
      Respond ONLY with a valid JSON block containing:
      {
        "aligned": true or false,
        "missing_ideas": ["list of any key themes from AI/Human reasoning not present or misrepresented in the article"],
        "explanation": "brief explanation"
      }
    PROMPT
    
    begin
      require 'open3'
      stdout, stderr, status = Open3.capture3("gemini -p \"\" --output-format text", :stdin_data => prompt)
      
      if status.success?
        # Extract JSON block
        json_match = stdout.match(/\{.*\}/m)
        if json_match
          begin
            res = JSON.parse(json_match[0])
            if res["aligned"]
              successes << "✅ Semantic check passed: Article draft is semantically aligned with both AI and Human reasoning. Explanation: #{res["explanation"]}"
            else
              errors << "❌ Semantic check failed: Article is missing key ideas: #{res["missing_ideas"].join(', ')}. Explanation: #{res["explanation"]}"
            end
          rescue => e
            errors << "❌ Failed to parse semantic validation JSON: #{e.message}. Raw output: #{stdout}"
          end
        else
          errors << "❌ No valid JSON block returned by semantic check. Raw output: #{stdout}"
        end
      else
        errors << "❌ Semantic check failed to execute: #{stderr}"
      end
    rescue => e
      errors << "❌ Semantic check failed with exception: #{e.message}"
    end
  else
    errors << "❌ Cannot run semantic check: missing AI_REASONING.md or HUMAN_REASONING.md"
  end
end

# Final report
puts "\n📋 TEST REPORT:"
puts "----------------------------------------"
if errors.empty?
  puts "🎉 All tests passed successfully!"
  exit 0
else
  puts "❌ Some tests failed:\n\n"
  errors.each { |err| puts "  #{err}" }
  exit 1
end
