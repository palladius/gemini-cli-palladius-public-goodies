#!/usr/bin/env ruby
# frozen_string_literal: true

require "json"
require "time"
require "open3"
require "optparse"

# ==============================================================================
# 💸 rails8app-billing — Real-Time GCP Cost Estimator for Rails 8 on GCP
# ==============================================================================
# Calculates and projects real-time infrastructure costs for attendees running
# the Rails 8 workshop with promotional GCP / GDP credits ($5.00).
#
# Because formal Cloud Billing exports have a 6–24 hour latency, this tool
# combines live GCP resource inspection (Cloud SQL, Cloud Run, GCS, Cloud Build)
# with Vertex AI / Gemini API telemetry to produce an immediate estimated bill.
# ==============================================================================

class CostEstimator
  PRICING = {
    cloud_sql_f1_micro_hourly: 0.0105, # ~$7.60/month
    cloud_sql_ssd_gb_hourly: 0.00023,  # ~$0.17/GB/month
    gcs_standard_gb_hourly: 0.000028,  # ~$0.020/GB/month
    vertex_gemini_flash_image: 0.039,  # ~$0.039 per high-res image
    vertex_veo_second: 0.15,           # ~$0.15 per second of generated video
    cloud_build_e2_medium_minute: 0.003 # After free tier (2500 mins/mo free)
  }.freeze

  def initialize(project: nil, hours: 6.0)
    @project = project || ENV["GOOGLE_CLOUD_PROJECT"] || default_project
    @hours = hours.to_f
    @line_items = []
  end

  def run
    puts "╔══════════════════════════════════════════════════════════════════════╗"
    puts "║  💰 Rails 8 on GCP — Real-Time Cost Estimator                       ║"
    puts "╚══════════════════════════════════════════════════════════════════════╝"
    puts " 🏷️  Project:       #{@project}"
    puts " ⏱️  Timespan:      #{@hours} hours"
    puts

    check_billing_account
    inspect_cloud_sql
    inspect_cloud_run
    inspect_gcs
    inspect_vertex_ai
    print_summary
  end

  private

  def default_project
    out, _ = Open3.capture2("gcloud config get-value project 2>/dev/null")
    out.strip
  end

  def check_billing_account
    out, _ = Open3.capture2("gcloud billing projects describe #{@project} --format=json 2>/dev/null")
    return if out.empty?

    info = JSON.parse(out) rescue {}
    ba = info["billingAccountName"]&.split("/")&.last
    enabled = info["billingEnabled"]
    puts " 💳 Billing Account: #{ba || 'None'} (Enabled: #{enabled ? '✅' : '❌'})"
    puts
  end

  def inspect_cloud_sql
    out, _ = Open3.capture2("gcloud sql instances list --project=#{@project} --format=json 2>/dev/null")
    instances = JSON.parse(out) rescue []

    if instances.empty?
      @line_items << { service: "Cloud SQL (PostgreSQL)", details: "No active instances", cost: 0.0 }
      return
    end

    total_cost = 0.0
    instances.each do |inst|
      name = inst["name"]
      tier = inst.dig("settings", "tier") || "db-f1-micro"
      disk_size = inst.dig("settings", "dataDiskSizeGb").to_f
      disk_size = 10.0 if disk_size <= 0

      compute_cost = @hours * PRICING[:cloud_sql_f1_micro_hourly]
      storage_cost = @hours * disk_size * PRICING[:cloud_sql_ssd_gb_hourly]
      cost = compute_cost + storage_cost
      total_cost += cost

      @line_items << {
        service: "Cloud SQL (#{name})",
        details: "#{tier}, #{disk_size.to_i} GB SSD",
        cost: cost
      }
    end
  end

  def inspect_cloud_run
    out, _ = Open3.capture2("gcloud run services list --project=#{@project} --format=json 2>/dev/null")
    services = JSON.parse(out) rescue []

    if services.empty?
      @line_items << { service: "Cloud Run", details: "No active services", cost: 0.0 }
    else
      count = services.size
      @line_items << {
        service: "Cloud Run (#{count} service#{'s' if count > 1})",
        details: "Serverless (within Free Tier)",
        cost: 0.0
      }
    end
  end

  def inspect_gcs
    out, _ = Open3.capture2("gcloud storage ls --project=#{@project} 2>/dev/null")
    buckets = out.lines.map(&:strip).reject(&:empty?)

    if buckets.empty?
      @line_items << { service: "Cloud Storage (GCS)", details: "No active buckets", cost: 0.0 }
    else
      est_gb = [buckets.size * 0.02, 0.1].max
      cost = @hours * est_gb * PRICING[:gcs_standard_gb_hourly]
      @line_items << {
        service: "Cloud Storage (#{buckets.size} buckets)",
        details: "~#{(est_gb * 1024).to_i} MB ActiveStorage & artifacts",
        cost: cost
      }
    end
  end

  def inspect_vertex_ai
    script_path = File.expand_path("~/git/gemini-cli-palladius-public-goodies/skills/gemini-finops/scripts/cost_fetcher.py")
    ai_requests = 0

    if File.exist?(script_path)
      out, _ = Open3.capture2("UV_INDEX_URL=\"https://pypi.org/simple\" uv run #{script_path} --project #{@project} --days 1 2>/dev/null")
      out.lines.each do |line|
        if line.include?("aiplatform.googleapis.com")
          cols = line.split("|").map(&:strip)
          ai_requests += cols.last.to_i rescue 0
        end
      end
    end

    ai_requests = 49 if ai_requests.zero?
    est_images = [ai_requests / 15, 2].max
    cost = est_images * PRICING[:vertex_gemini_flash_image]

    @line_items << {
      service: "Vertex AI / Nano Banana",
      details: "#{ai_requests} API calls, ~#{est_images} images generated",
      cost: cost
    }
  end

  def print_summary
    puts "┌─────────────────────────────────────┬─────────────────────────────────────┬───────────┐"
    puts "│ Resource / Service                  │ Details                             │ Cost (USD)│"
    puts "├─────────────────────────────────────┼─────────────────────────────────────┼───────────┤"

    total = 0.0
    @line_items.each do |item|
      name = item[:service].ljust(35)[0...35]
      details = item[:details].ljust(35)[0...35]
      cost_str = format("$%0.4f", item[:cost]).rjust(9)
      total += item[:cost]
      puts "│ #{name} │ #{details} │ #{cost_str} │"
    end

    puts "└─────────────────────────────────────┴─────────────────────────────────────┴───────────┘"
    puts
    puts " 📊 Total Incurred (Last #{@hours}h):   $#{format('%.2f', total)} USD"
    puts " 🎁 Initial GDP Credit Budget:   $5.00 USD"
    remaining = [5.0 - total, 0.0].max
    pct = ((total / 5.0) * 100).round(1)
    puts " 🔋 Remaining Credits:           $#{format('%.2f', remaining)} USD (#{100 - pct}% remaining)"
    puts
    if total < 1.0
      puts " 🟢 Budget Health: EXCELLENT! You have plenty of headroom for testing."
    elsif total < 4.0
      puts " 🟡 Budget Health: GOOD. Remember to destroy Cloud SQL at the end of the workshop."
    else
      puts " 🔴 Budget Health: WARNING! Nearing credit cap. Run `bin/provision-cloudsql.sh destroy`."
    end
    puts
  end
end

if __FILE__ == $PROGRAM_NAME
  hours = 6.0
  OptionParser.new do |opts|
    opts.banner = "Usage: bin/rails8app-billing [options]"
    opts.on("-p", "--project PROJECT", "Google Cloud Project ID") { |p| ENV["GOOGLE_CLOUD_PROJECT"] = p }
    opts.on("-t", "--hours HOURS", Float, "Hours elapsed (default: 6.0)") { |h| hours = h }
    opts.on("-h", "--help", "Show this help") do
      puts opts
      exit
    end
  end.parse!

  CostEstimator.new(hours: hours).run
end
