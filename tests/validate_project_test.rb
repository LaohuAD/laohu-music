# frozen_string_literal: true

require "minitest/autorun"
require "json"
require "open3"

class ValidateProjectTest < Minitest::Test
  ROOT = File.expand_path("..", __dir__)

  def test_portable_interface_includes_event_and_result_contracts
    assert File.file?(File.join(ROOT, "schemas", "work-event.schema.json"))
    assert File.file?(File.join(ROOT, "schemas", "operation-result.schema.json"))
    assert File.file?(File.join(ROOT, "schemas", "audio-run.schema.json"))
  end

  def test_project_validator_accepts_v3_foundation
    stdout, stderr, status = Open3.capture3("ruby", "scripts/validate_project.rb", chdir: ROOT)

    assert status.success?, "validator failed:\n#{stdout}\n#{stderr}"
    assert_includes stdout, "V3 validation passed"
  end

  def test_root_creative_mechanisms_have_single_authority
    creative_core = File.read(File.join(ROOT, "knowledge", "creative-core.md"))
    lyrics_craft = File.read(File.join(ROOT, "knowledge", "lyrics-craft.md"))
    sound_prompt = File.read(File.join(ROOT, "knowledge", "sound-prompt.md"))

    assert_includes creative_core, "语言参与发现主题"
    assert_includes creative_core, "情绪强度不等于作品尺度"
    assert_includes creative_core, "文化材料必须由当前人物重新发声"
    assert_includes creative_core, "外部成熟机制校准"

    assert_includes lyrics_craft, "开场认知缺口"
    assert_includes lyrics_craft, "抽象词的语境缩窄"
    assert_includes lyrics_craft, "呼吸组先于视觉分行"
    assert_includes lyrics_craft, "节奏时间假设"
    assert_includes lyrics_craft, "完美韵、家族韵与同辙"

    assert_includes sound_prompt, "BPM不等于groove"
    assert_includes sound_prompt, "四条声音变化曲线"
    assert_includes sound_prompt, "普通话发声风险"
  end

  def test_external_audio_feedback_contract_supports_repeated_evidence_cycles
    operation_schema = JSON.parse(File.read(File.join(ROOT, "schemas", "operation.schema.json")))
    work_state = JSON.parse(File.read(File.join(ROOT, "schemas", "work-state.schema.json")))
    work_event = JSON.parse(File.read(File.join(ROOT, "schemas", "work-event.schema.json")))
    director_skill = File.read(File.join(ROOT, "skills", "laohu_music", "SKILL.md"))
    sound_skill = File.read(File.join(ROOT, "skills", "laohu_sound", "SKILL.md"))
    prompt_revision_path = File.join(ROOT, "schemas", "prompt-revision.schema.json")
    audio_feedback = operation_schema.fetch("$defs").fetch("audioFeedbackPayload")
    properties = audio_feedback.fetch("properties")

    assert File.file?(prompt_revision_path), "prompt revisions need a stable recoverable contract"
    assert_equal 1, properties.fetch("audio_run_ids").fetch("minItems")
    assert_equal true, properties.fetch("audio_run_ids").fetch("uniqueItems")
    assert_equal %w[user_text_only tool_assisted_audio both], properties.fetch("analysis_mode").fetch("enum")
    assert properties.key?("overall_feeling")
    assert properties.key?("observations")
    assert_includes properties.fetch("observations").fetch("items").fetch("required"), "judgment"

    sound_iteration = work_state.dig("properties", "sound_iteration", "properties")
    assert sound_iteration.key?("current_prompt_revision_id")
    assert sound_iteration.key?("accepted_prompt_revision_id")
    assert sound_iteration.key?("feedback_cycle_count")

    event_types = work_event.dig("properties", "event_type", "enum")
    assert_includes event_types, "prompt_revision_created"
    assert_includes event_types, "external_feedback_incorporated"
    assert_includes event_types, "sound_package_accepted"

    assert_includes operation_schema.dig("properties", "operation", "enum"), "accept_sound_package"
    assert operation_schema.fetch("$defs").key?("acceptSoundPackagePayload")
    assert_includes director_skill, "用户不需要手工提供 ID"
    assert_includes sound_skill, "保留资产"
    assert_includes sound_skill, "expected_observable_changes"
    assert_includes sound_skill, "accept_sound_package"
  end

  def test_prompt_revision_records_lineage_preservation_and_testable_change
    schema = JSON.parse(File.read(File.join(ROOT, "schemas", "prompt-revision.schema.json")))
    required = schema.fetch("required")

    %w[
      prompt_revision_id
      work_id
      parent_prompt_revision_id
      prompt_package_sha256
      source_audio_run_ids
      source_feedback_event_ids
      preserved_assets
      modification_group
      expected_observable_changes
      status
    ].each do |field|
      assert_includes required, field
    end

    modification = schema.dig("properties", "modification_group")
    assert_equal %w[target_fields changes reason], modification.fetch("required")
    assert_equal true, modification.dig("properties", "target_fields", "uniqueItems")
  end

  def test_audio_feedback_can_reopen_locked_lyrics_through_an_explicit_operation
    operation_schema = JSON.parse(File.read(File.join(ROOT, "schemas", "operation.schema.json")))
    work_event = JSON.parse(File.read(File.join(ROOT, "schemas", "work-event.schema.json")))
    director_skill = File.read(File.join(ROOT, "skills", "laohu_music", "SKILL.md"))

    assert_includes operation_schema.dig("properties", "operation", "enum"), "reopen_lyrics"
    payload = operation_schema.dig("$defs", "reopenLyricsPayload")
    assert_equal %w[confirmed reason return_stage], payload.fetch("required")
    assert_equal true, payload.dig("properties", "confirmed", "const")
    assert_includes work_event.dig("properties", "event_type", "enum"), "lyrics_reopened"
    assert_includes director_skill, "reopen_lyrics"
  end

  def test_instrumental_work_can_enter_sound_flow_without_lyrics
    work_state = JSON.parse(File.read(File.join(ROOT, "schemas", "work-state.schema.json")))
    operation_schema = JSON.parse(File.read(File.join(ROOT, "schemas", "operation.schema.json")))
    director_skill = File.read(File.join(ROOT, "skills", "laohu_music", "SKILL.md"))
    sound_skill = File.read(File.join(ROOT, "skills", "laohu_sound", "SKILL.md"))

    assert_equal %w[vocal_song instrumental], work_state.dig("properties", "work_type", "enum")
    assert_equal %w[vocal_song instrumental], operation_schema.dig("$defs", "createWorkPayload", "properties", "work_type", "enum")
    assert_includes director_skill, "纯音乐"
    assert_includes sound_skill, "Instrumental Form"
    assert_includes sound_skill, "instrumental"
  end

  def test_music_fragment_can_be_refined_without_forcing_a_full_package
    work_state = JSON.parse(File.read(File.join(ROOT, "schemas", "work-state.schema.json")))
    operation_schema = JSON.parse(File.read(File.join(ROOT, "schemas", "operation.schema.json")))
    director_skill = File.read(File.join(ROOT, "skills", "laohu_music", "SKILL.md"))
    sound_skill = File.read(File.join(ROOT, "skills", "laohu_sound", "SKILL.md"))

    assert_includes work_state.dig("properties", "active_scope", "properties", "allowed_change", "enum"), "music_fragment"
    assert_includes operation_schema.dig("$defs", "reviseScopePayload", "properties", "level", "enum"), "music_fragment"
    assert_includes director_skill, "音乐片段"
    assert_includes sound_skill, "music_fragment"
    assert_includes sound_skill, "只炼片段"
  end

  def test_music_fragment_schema_constrains_kind_and_representation_pairs
    fragment_schema = JSON.parse(File.read(File.join(ROOT, "schemas", "music-fragment.schema.json")))
    constraints = fragment_schema.fetch("allOf")

    assert_operator constraints.length, :>=, 6
    serialized = JSON.generate(constraints)
    assert_includes serialized, "chord_functions"
    assert_includes serialized, "rhythm_grid"
    assert_includes serialized, "section_map"
    assert_includes serialized, "vocal_action"
  end

  def test_music_fragment_decisions_have_stable_scope_ids
    work_state = JSON.parse(File.read(File.join(ROOT, "schemas", "work-state.schema.json")))
    decision_schema = JSON.parse(File.read(File.join(ROOT, "schemas", "decision.schema.json")))

    assert work_state.dig("properties", "active_scope", "properties").key?("fragment_id")
    assert_includes decision_schema.dig("properties", "scope", "properties", "level", "enum"), "music_fragment"
    assert decision_schema.dig("properties", "scope", "properties").key?("fragment_id")
  end

  def test_quick_draft_can_run_without_faking_user_locks
    director_skill = File.read(File.join(ROOT, "skills", "laohu_music", "SKILL.md"))
    lyrics_skill = File.read(File.join(ROOT, "skills", "laohu_lyrics", "SKILL.md"))

    assert_includes director_skill, "本轮工作假设"
    assert_includes lyrics_skill, "快速完整稿不要求上游已锁定"
    assert_includes lyrics_skill, "不写入 state.locked"
  end

  def test_line_and_section_targets_do_not_require_a_complete_song
    director_skill = File.read(File.join(ROOT, "skills", "laohu_music", "SKILL.md"))
    lyrics_skill = File.read(File.join(ROOT, "skills", "laohu_lyrics", "SKILL.md"))

    assert_includes director_skill, "只炼句"
    assert_includes lyrics_skill, "局部目标不要求完整歌词"
    assert_includes lyrics_skill, "只炼乐段"
    assert_includes lyrics_skill, "不得声称完整歌词成立"
  end
end
