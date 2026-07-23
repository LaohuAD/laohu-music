#!/usr/bin/env ruby
# frozen_string_literal: true

require "json"
require "yaml"

ROOT = File.expand_path("..", __dir__)

REQUIRED_FILES = %w[
  AGENTS.md
  README.md
  PRD.md
  project.yaml
  schemas/work-state.schema.json
  schemas/decision.schema.json
  schemas/memory-record.schema.json
  schemas/operation.schema.json
  schemas/operation-result.schema.json
  schemas/work-event.schema.json
  schemas/audio-run.schema.json
  schemas/prompt-revision.schema.json
  schemas/music-fragment.schema.json
  skills/laohu_music/SKILL.md
  skills/laohu_lyrics/SKILL.md
  skills/laohu_sound/SKILL.md
  skills/laohu_learning/SKILL.md
  knowledge/creative-core.md
  knowledge/lyrics-craft.md
  knowledge/sound-prompt.md
  memory/profile.yaml
  memory/records.jsonl
  evaluation/skill-tests.md
  docs/v2-root-mechanism-audit.md
].freeze

LEGAL_STAGES = %w[
  briefing proposition_choice hook_development form_choice draft_generation
  section_revision line_revision lyrics_locked sound_choice sound_package_ready
  external_audio_review complete paused
].freeze

def fail!(errors, message)
  errors << message
end

def read_yaml(path, errors)
  YAML.safe_load(File.read(path), permitted_classes: [], aliases: false)
rescue StandardError => e
  fail!(errors, "invalid YAML #{path.delete_prefix(ROOT + "/")}: #{e.message}")
  nil
end

def read_json(path, errors)
  JSON.parse(File.read(path))
rescue StandardError => e
  fail!(errors, "invalid JSON #{path.delete_prefix(ROOT + "/")}: #{e.message}")
  nil
end

errors = []

REQUIRED_FILES.each do |relative|
  path = File.join(ROOT, relative)
  fail!(errors, "missing required file: #{relative}") unless File.file?(path)
end

unless errors.empty?
  warn errors.join("\n")
  exit 1
end

Dir[File.join(ROOT, "schemas", "*.json")].sort.each do |path|
  schema = read_json(path, errors)
  next unless schema

  fail!(errors, "schema missing $schema: #{File.basename(path)}") unless schema["$schema"]
  fail!(errors, "schema missing $id: #{File.basename(path)}") unless schema["$id"]
end

project = read_yaml(File.join(ROOT, "project.yaml"), errors)
profile = read_yaml(File.join(ROOT, "memory", "profile.yaml"), errors)

if project
  fail!(errors, "project schema_version must be 1") unless project["schema_version"] == 1
  entry = project["entry_skill"]
  fail!(errors, "project entry_skill is missing") unless entry.is_a?(String) && File.file?(File.join(ROOT, entry))
  fail!(errors, "product_phase must be local_first") unless project["product_phase"] == "local_first"
end

if profile
  fail!(errors, "profile schema_version must be 1") unless profile["schema_version"] == 1
  fail!(errors, "new profile maturity must be infant") unless profile["maturity"] == "infant"
  if project && profile["owner_id"] != project["default_owner_id"]
    fail!(errors, "profile owner_id must match project default_owner_id")
  end
end

records_path = File.join(ROOT, "memory", "records.jsonl")
record_count = 0
File.foreach(records_path, chomp: true).with_index(1) do |line, index|
  next if line.empty?

  record_count += 1
  begin
    record = JSON.parse(line)
    fail!(errors, "memory record #{index} schema_version must be 1") unless record["schema_version"] == 1
    fail!(errors, "memory record #{index} missing record_id") if record["record_id"].to_s.empty?
    fail!(errors, "memory record #{index} missing record_type") if record["record_type"].to_s.empty?
  rescue JSON::ParserError => e
    fail!(errors, "invalid JSONL memory record #{index}: #{e.message}")
  end
end
fail!(errors, "memory records must include initialization metadata") if record_count.zero?

skill_names = []
Dir[File.join(ROOT, "skills", "*", "SKILL.md")].sort.each do |path|
  content = File.read(path)
  parts = content.split("---", 3)
  if parts.length < 3
    fail!(errors, "skill missing YAML frontmatter: #{path.delete_prefix(ROOT + "/")}")
    next
  end

  frontmatter = YAML.safe_load(parts[1], permitted_classes: [], aliases: false)
  name = frontmatter["name"].to_s
  description = frontmatter["description"].to_s
  fail!(errors, "invalid skill name #{name.inspect}") unless name.match?(/\A[a-zA-Z0-9-]+\z/)
  fail!(errors, "skill description must start with 'Use when': #{name}") unless description.start_with?("Use when")
  fail!(errors, "skill description too long: #{name}") if description.length > 500
  fail!(errors, "duplicate skill name: #{name}") if skill_names.include?(name)
  skill_names << name
end

work_state_schema = read_json(File.join(ROOT, "schemas", "work-state.schema.json"), errors)
if work_state_schema
  stages = work_state_schema.dig("properties", "stage", "enum")
  fail!(errors, "work state stages do not match V3 contract") unless stages == LEGAL_STAGES
end

Dir[File.join(ROOT, "**", "*")].each do |path|
  next unless File.file?(path)
  next if File.basename(path) == ".gitkeep"

  fail!(errors, "unexpected empty file: #{path.delete_prefix(ROOT + "/")}") if File.zero?(path)
end

runtime_files = %w[AGENTS.md project.yaml].map { |relative| File.join(ROOT, relative) } +
  Dir[File.join(ROOT, "skills", "*", "SKILL.md")] +
  Dir[File.join(ROOT, "knowledge", "*.md")]
runtime_files.each do |path|
  content = File.read(path)
  if content.include?("/老胡音乐V2/") || content.include?("\\老胡音乐V2\\")
    fail!(errors, "runtime file contains V2 path dependency: #{path.delete_prefix(ROOT + "/")}")
  end
end

if errors.empty?
  puts "V3 validation passed: #{REQUIRED_FILES.length} authority files, #{skill_names.length} skills, #{record_count} memory records"
  exit 0
end

warn errors.join("\n")
exit 1
