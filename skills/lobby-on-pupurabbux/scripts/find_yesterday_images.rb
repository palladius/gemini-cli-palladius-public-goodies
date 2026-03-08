#!/usr/bin/env ruby
# (💛) find_yesterday_images.rb
# This script finds images from yesterday in OpenClaw inbound and nano_banana folders.
# It uses Riccardo's preferred style: Colorful and emoji-friendly.

require 'date'

# Configuration
INBOUND_DIR = "/home/riccardo/.openclaw/media/inbound"
PIXAR_DIR = "/home/riccardo/.openclaw/workspace/nano_banana"
MAPPING_FILE = "/home/riccardo/.openclaw/workspace/banana_mapping.csv"

# Time setup
target_date = (Date.today - 1).strftime("%Y-%m-%d")
next_day = Date.today.strftime("%Y-%m-%d")

puts "🔍 Looking for images from yesterday (#{target_date})..."

# Check if directories exist
unless Dir.exists?(INBOUND_DIR) && Dir.exists?(PIXAR_DIR)
  puts "❌ OpenClaw directories not found. Are you on the right host?"
  exit 1
end

# Find images using the shell find command
cmd = "find #{INBOUND_DIR} #{PIXAR_DIR} -newermt \"#{target_date}\" ! -newermt \"#{next_day}\" \\( -name \"*.jpg\" -o -name \"*.png\" -o -name \"*.jpeg\" -o -name \"*.webp\" \\) -printf \"%T+ %p\\n\" | sort"

output = `#{cmd}`

if output.empty?
  puts "📭 No images found for #{target_date}."
else
  puts "✨ Found the following images from yesterday:"
  output.each_line do |line|
    time, path = line.split(' ')
    # Make it beautiful with emojis
    icon = path.include?("nano_banana") ? "🍌 (Pixarized)" : "📥 (Inbound)"
    puts "  #{icon} [#{time[11..18]}] #{File.basename(path)}"
  end
end

puts "\n💡 Pro-tip: Check `#{MAPPING_FILE}` for manual correlation if needed!"
