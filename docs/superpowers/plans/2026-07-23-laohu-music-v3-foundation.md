# Laohu Music V3 Foundation Implementation Plan

> **Historical record:** This completed plan records how the foundation was built. It is not a runtime instruction. Current operation follows `AGENTS.md`; in particular, V3 does not start subagents by default.

**Goal:** Build a local-first, directory-driven AI music co-creation project whose work state, human decisions, personal memory, root-cause learning, lyric workflow, instrumental entry, and sound-prompt workflow can later be adapted to a website without rewriting the creative core.

**Architecture:** The project separates universal knowledge, procedural skills, per-user memory, and per-work state. A thin director routes one explicit state transition at a time; one lyric skill develops proposition, invariant chorus lines, form, draft, section, and line refinement; one sound skill serves both vocal songs and instrumental works, then revises prompt packages through repeated external-audio feedback cycles; one learning skill converts accepted feedback into scoped preference evidence or validated root-cause learning. JSON Schema files define interface-stable records for future adapters.

**Tech Stack:** Markdown, YAML, JSON Schema, JSONL, Ruby standard library validation.

---

### Task 1: Product Contract and Directory Authority

**Files:**
- Create: `PRD.md`
- Create: `AGENTS.md`
- Create: `README.md`
- Create: `project.yaml`

- [x] **Step 1:** Write the V3 PRD with goals, non-goals, first principles, user workflow, stage machine, data model, learning model, V2 migration policy, performance budget, future website boundary, and acceptance criteria.
- [x] **Step 2:** Write a detailed but non-duplicative `AGENTS.md` defining directory authority, state recovery, request routing, human decision protocol, root-cause evolution, file discipline, stage transitions, cross-agent handoff, and delivery checks.
- [x] **Step 3:** Write `README.md` as the human entry point and `project.yaml` as the machine entry point.
- [x] **Step 4:** Confirm that each concept has one authority and that project operation does not depend on chat history.

### Task 2: Interface-Stable Data Contracts

**Files:**
- Create: `schemas/work-state.schema.json`
- Create: `schemas/decision.schema.json`
- Create: `schemas/memory-record.schema.json`
- Create: `schemas/operation.schema.json`
- Create: `memory/profile.yaml`
- Create: `memory/records.jsonl`

- [x] **Step 1:** Define the work state schema with stage, lock, artifact, active scope, open-decision, next-action, and schema-version fields.
- [x] **Step 2:** Define decision packages and submitted choices without storing hidden reasoning.
- [x] **Step 3:** Define separate memory record variants for preference evidence, root-cause learning, and external-result evidence.
- [x] **Step 4:** Define local and future-web operations such as `create_work`, `get_work_state`, `get_next_decision`, `submit_choice`, `generate_draft`, `revise_scope`, `lock_lyrics`, `select_sound_direction`, `generate_sound_package`, and `submit_audio_feedback`.
- [x] **Step 5:** Initialize an infant profile and a valid metadata record without inventing user preferences.

### Task 3: Distill Strategic Creative Knowledge from V2

**Files:**
- Create: `knowledge/creative-core.md`
- Create: `knowledge/lyrics-craft.md`
- Create: `knowledge/sound-prompt.md`

- [x] **Step 1:** Migrate only upstream principles that change creative decisions: human reception, unresolved contradiction, character knowledge, selective perception, the integrated three realms, listener participation, and private-to-public recognition.
- [x] **Step 2:** Migrate lyric craft that is required for a high-potential draft: language discovery, observation distance, invariant chorus core, section functions, natural Chinese, poetic transformation, rhyme and singability, whole-song coherence, and replacement-loss tests.
- [x] **Step 3:** Migrate sound-prompt principles: prompt as generation hypothesis, one memory center, vocal identity, lyrics alignment, positive Style Prompt, exact Controlled Lyrics, and external-audio feedback as the truth source.
- [x] **Step 4:** Exclude V2 lifecycle bureaucracy, large candidate pools, near-duplicate prohibitions, one-incident word bans, exhaustive matrices, and rules that only describe a surface symptom.

### Task 4: Create Four Focused Skills

**Files:**
- Create: `evaluation/skill-tests.md`
- Create: `skills/laohu_music/SKILL.md`
- Create: `skills/laohu_lyrics/SKILL.md`
- Create: `skills/laohu_sound/SKILL.md`
- Create: `skills/laohu_learning/SKILL.md`

- [x] **Step 1:** Record RED evidence from V2 failures for routing latency, lyric over-compliance, text-only sound speculation, and rule bloat.
- [x] **Step 2:** Write the thin director skill with stage restoration, decision gating, and no creative-rule duplication.
- [x] **Step 3:** Write the lyric skill with explicit modes and full-context scoped editing; review every line but surface only evidence-backed choices.
- [x] **Step 4:** Write the sound skill with macro direction choice, one prompt-package generation, and targeted updates from real external audio feedback.
- [x] **Step 5:** Write the learning skill with symptom-to-root-cause tracing, preference/rule separation, validation states, boundaries, counterexamples, and promotion control.
- [x] **Step 6:** Add pressure scenarios proving that skills do not recreate multi-agent pools, write unapproved preferences, isolate sections from whole-song context, or treat expected sound as heard audio.
- [x] **Step 7:** Add a pure-instrumental branch using `work_type`, `Style Prompt + Instrumental Form`, and the same external-audio feedback loop without requiring lyrics or a vocalist.

### Task 5: Add Portable Validation

**Files:**
- Create: `tests/validate_project_test.rb`
- Create: `scripts/validate_project.rb`
- Create: `works/.gitkeep`

- [x] **Step 1:** Write a failing test that requires all authority files, valid JSON/YAML, skill frontmatter, schema versions, legal stages, and cross-file entry paths.
- [x] **Step 2:** Run `ruby tests/validate_project_test.rb` and confirm failure because the validator is absent.
- [x] **Step 3:** Implement the minimal standard-library validator.
- [x] **Step 4:** Run `ruby tests/validate_project_test.rb` and `ruby scripts/validate_project.rb`; expect all checks to pass.
- [x] **Step 5:** Run placeholder, duplicate-authority, empty-file, and directory checks.

### Task 6: Final Architecture Review

**Files:**
- Verify all files created above.

- [x] **Step 1:** Confirm no V2 production files were modified and V3 does not depend on V2 paths at runtime.
- [x] **Step 2:** Confirm another agent can restore a work from `project.yaml` and `works/<id>/state.yaml` without chat history.
- [x] **Step 3:** Confirm universal knowledge, personal memory, and work-specific decisions cannot overwrite each other implicitly.
- [x] **Step 4:** Confirm the default lyric flow has human decisions at proposition, invariant chorus line, form, section repair, line repair, and sound direction, while avoiding full-candidate pools.
- [x] **Step 5:** Report created files, validation results, deliberate V2 exclusions, and remaining productization work.
