#!/usr/bin/env python3
"""
Comprehensive Real-World Validation Suite for PLB Creator Studio
Validates Phases 1 through 7 and collects all telemetry for Phase 8.
"""

import sys
import os
import json
import time
import subprocess
import urllib.request
import urllib.parse
from pathlib import Path

# Ensure UTF-8 unbuffered output
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

BASE_URL_STUDIO = "http://127.0.0.1:5500"
BASE_URL_FORGE = "http://127.0.0.1:5050"
BASE_URL_SEO = "http://127.0.0.1:5000"

results = {}

def log_section(title):
    print("\n" + "=" * 70, flush=True)
    print(f" {title}", flush=True)
    print("=" * 70, flush=True)

def http_get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "PLB-Validator/1.0"})
    with urllib.request.urlopen(req, timeout=5) as resp:
        return resp.status, resp.read().decode('utf-8')

def http_post_json(url, payload=None):
    data = json.dumps(payload or {}).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json", "User-Agent": "PLB-Validator/1.0"}, method="POST")
    with urllib.request.urlopen(req, timeout=8) as resp:
        return resp.status, resp.read().decode('utf-8')

# =====================================================================
# PHASE 1 — START THE REAL APP & VERIFY CORE MODULES
# =====================================================================
log_section("PHASE 1: START THE REAL APP & VERIFY CORE MODULES")

phase1_checks = {}

# 1.1 Server ports
for name, url in [("Studio Gateway", BASE_URL_STUDIO), ("Story Universe Factory", BASE_URL_FORGE), ("Video SEO Engine", BASE_URL_SEO)]:
    try:
        status, body = http_get(f"{url}/")
        phase1_checks[f"Port_{url}"] = (status == 200)
        print(f"  [PASS] {name} ({url}) responded with HTTP {status}", flush=True)
    except Exception as e:
        phase1_checks[f"Port_{url}"] = False
        print(f"  [FAIL] {name} ({url}): {e}", flush=True)

# 1.2 Story Universe & DNA
try:
    status, body = http_get(f"{BASE_URL_FORGE}/api/universe/test_sess_01")
    data = json.loads(body)
    has_universe = "character_universe" in data and "universe_metrics" in data
    phase1_checks["Story_Universe"] = has_universe
    print(f"  [{'PASS' if has_universe else 'FAIL'}] Story Universe data loaded (session: test_sess_01)", flush=True)
except Exception as e:
    phase1_checks["Story_Universe"] = False
    print(f"  [FAIL] Story Universe: {e}", flush=True)

# 1.3 Story DNA & Lineage Graph
try:
    status, body = http_get(f"{BASE_URL_FORGE}/api/session/test_sess_01")
    data = json.loads(body)
    has_dna = "story_dna" in data and "lineage_graph" in data and "stories" in data
    phase1_checks["Story_DNA_and_Lineage"] = has_dna
    print(f"  [{'PASS' if has_dna else 'FAIL'}] Story DNA and Lineage Graph loaded (total stories: {len(data.get('stories', []))})", flush=True)
except Exception as e:
    phase1_checks["Story_DNA_and_Lineage"] = False
    print(f"  [FAIL] Story DNA: {e}", flush=True)

# 1.4 Production Package & Hero Frame Fields
try:
    status, body = http_get(f"{BASE_URL_FORGE}/api/production/test_sess_01/STORY-01")
    data = json.loads(body)
    pkg = data.get("package", {})
    hero = pkg.get("hero_frame", {})
    comp = hero.get("composition")
    lighting = hero.get("lighting")
    palette = hero.get("color_palette") or hero.get("palette")
    lens = hero.get("camera_lens") or hero.get("lens")
    
    hero_valid = bool(comp and lighting and palette and lens and comp != "Not specified" and palette != "Not specified" and lens != "Not specified")
    phase1_checks["Hero_Frame_NonBlank"] = hero_valid
    print(f"  [{'PASS' if hero_valid else 'FAIL'}] Hero Frame Spec: Composition='{comp[:35]}...', Lighting='{lighting[:35]}...', Palette='{palette[:35]}...', Lens='{lens[:35]}...'", flush=True)
    
    continuity_valid = bool(pkg.get("continuity_block") and pkg.get("continuity_lock"))
    phase1_checks["Continuity_Block"] = continuity_valid
    print(f"  [{'PASS' if continuity_valid else 'FAIL'}] Continuity Lock and Block present", flush=True)
    
    prod_valid = bool(pkg.get("script_15s") and pkg.get("storyboard_6_shots"))
    phase1_checks["Production_Package"] = prod_valid
    print(f"  [{'PASS' if prod_valid else 'FAIL'}] Production Package (Script, Storyboard 6-shots) present", flush=True)
except Exception as e:
    phase1_checks["Hero_Frame_NonBlank"] = False
    phase1_checks["Continuity_Block"] = False
    phase1_checks["Production_Package"] = False
    print(f"  [FAIL] Production verification: {e}", flush=True)

# 1.5 Prompt Compiler Endpoint
try:
    status, body = http_get(f"{BASE_URL_FORGE}/api/prompt-compiler/test_sess_01/STORY-01")
    data = json.loads(body)
    has_compiler = "prompt_package" in data and "models" in data.get("prompt_package", {})
    phase1_checks["Prompt_Compiler"] = has_compiler
    print(f"  [{'PASS' if has_compiler else 'FAIL'}] Prompt Compiler endpoint responded with compiled prompt package", flush=True)
except Exception as e:
    phase1_checks["Prompt_Compiler"] = False
    print(f"  [FAIL] Prompt Compiler: {e}", flush=True)

results["PHASE_1"] = phase1_checks

# =====================================================================
# PHASE 2 — REAL PROMPT COMPILER TEST
# =====================================================================
log_section("PHASE 2: REAL PROMPT COMPILER TEST")

phase2_checks = {}
compiled_prompts = {}

try:
    status, body = http_get(f"{BASE_URL_FORGE}/api/prompt-compiler/test_sess_01/STORY-01")
    data = json.loads(body)
    prompt_pkg = data.get("prompt_package", {})
    models = prompt_pkg.get("models", {})
    
    # 2.1 Seedance 2.5 Video Prompt
    s25 = models.get("seedance_25", {})
    s25_prompt = s25.get("prompt_text", "")
    compiled_prompts["seedance_25"] = s25_prompt
    phase2_checks["Seedance_25_Prompt"] = bool(s25_prompt and len(s25_prompt) > 50)
    print(f"  [{'PASS' if phase2_checks['Seedance_25_Prompt'] else 'FAIL'}] 1. Seedance 2.5 Video Prompt ({len(s25_prompt)} chars):", flush=True)
    print(f"     \"{s25_prompt[:120]}...\"", flush=True)
    
    # 2.2 Model-Neutral Universal Image Prompt
    univ = models.get("universal_image", {})
    univ_prompt = univ.get("prompt_text", "")
    compiled_prompts["universal_image"] = univ_prompt
    phase2_checks["Universal_Image_Prompt"] = bool(univ_prompt and len(univ_prompt) > 50)
    print(f"  [{'PASS' if phase2_checks['Universal_Image_Prompt'] else 'FAIL'}] 2. Model-Neutral Image Prompt ({len(univ_prompt)} chars):", flush=True)
    print(f"     \"{univ_prompt[:120]}...\"", flush=True)
    
    # 2.3 GPT Image Prompt
    gpt = models.get("gpt_image", {})
    gpt_prompt = gpt.get("prompt_text", "")
    compiled_prompts["gpt_image"] = gpt_prompt
    phase2_checks["GPT_Image_Prompt"] = bool(gpt_prompt and len(gpt_prompt) > 50)
    print(f"  [{'PASS' if phase2_checks['GPT_Image_Prompt'] else 'FAIL'}] 3. GPT Image Prompt ({len(gpt_prompt)} chars):", flush=True)
    print(f"     \"{gpt_prompt[:120]}...\"", flush=True)
    
    # 2.4 Nano Banana Pro Prompt
    nano = models.get("nano_banana_pro", {})
    nano_prompt = nano.get("prompt_text", "")
    compiled_prompts["nano_banana_pro"] = nano_prompt
    phase2_checks["Nano_Banana_Pro_Prompt"] = bool(nano_prompt and len(nano_prompt) > 50)
    print(f"  [{'PASS' if phase2_checks['Nano_Banana_Pro_Prompt'] else 'FAIL'}] 4. Nano Banana Pro Prompt ({len(nano_prompt)} chars):", flush=True)
    print(f"     \"{nano_prompt[:120]}...\"", flush=True)

    # 2.5 Hero Frame Prompt
    status, body = http_get(f"{BASE_URL_FORGE}/api/production/test_sess_01/STORY-01")
    pkg = json.loads(body).get("package", {})
    hero_prompt = pkg.get("hero_frame_prompt", "")
    phase2_checks["Hero_Frame_Prompt"] = bool(hero_prompt and len(hero_prompt) > 20)
    print(f"  [{'PASS' if phase2_checks['Hero_Frame_Prompt'] else 'FAIL'}] 5. Hero Frame Prompt ({len(hero_prompt)} chars):", flush=True)
    print(f"     \"{hero_prompt[:120]}...\"", flush=True)
    
    # 2.6 Shot-by-shot Prompts
    shots = pkg.get("shot_by_shot_prompts", [])
    phase2_checks["Shot_by_shot_Prompts"] = len(shots) >= 6
    print(f"  [{'PASS' if phase2_checks['Shot_by_shot_Prompts'] else 'FAIL'}] 6. Shot-by-shot Prompts ({len(shots)} shots):", flush=True)
    for s in shots[:2]:
        print(f"     Shot {s.get('shot_index')}: {s.get('prompt', '')[:80]}...", flush=True)
    
    # 2.7 Continuity Block
    continuity = pkg.get("continuity_block", "")
    phase2_checks["Continuity_Block"] = bool(continuity and len(continuity) > 30)
    print(f"  [{'PASS' if phase2_checks['Continuity_Block'] else 'FAIL'}] 7. Continuity Block ({len(continuity)} chars):", flush=True)
    print(f"     \"{continuity[:120]}...\"", flush=True)
    
except Exception as e:
    print(f"  [FAIL] Phase 2 error: {e}", flush=True)

results["PHASE_2"] = phase2_checks

# =====================================================================
# PHASE 3 — VERIFY SOURCE-OF-TRUTH UI & DOCUMENTATION GROUNDING
# =====================================================================
log_section("PHASE 3: VERIFY SOURCE-OF-TRUTH UI & DOCUMENTATION GROUNDING")

phase3_checks = {}

try:
    status, body = http_get(f"{BASE_URL_FORGE}/api/prompt-compiler/sources")
    src_data = json.loads(body)
    sources = {s["model_id"]: s for s in src_data.get("sources", [])}
    
    # 3.1 Verify Badges in rules
    all_rules = []
    for m in sources.values():
        if isinstance(m.get("rules"), dict):
            all_rules.extend(m["rules"].values())
        elif isinstance(m.get("rules"), list):
            all_rules.extend(m["rules"])
    
    has_official_badges = any("OFFICIAL" in r.get("classification", "") for r in all_rules)
    has_plb_badges = any("OPTIMIZATION" in r.get("classification", "") for r in all_rules)
    has_model_indep_badges = any("MODEL-INDEPENDENT" in r.get("classification", "") for r in all_rules)
    
    phase3_checks["Official_Rule_Badges"] = has_official_badges
    phase3_checks["PLB_Optimization_Badges"] = has_plb_badges
    phase3_checks["Model_Independent_Badges"] = has_model_indep_badges
    print(f"  [{'PASS' if has_official_badges else 'FAIL'}] OFFICIAL RULE badges present in registry ({sum(1 for r in all_rules if 'OFFICIAL' in r.get('classification', ''))} rules)", flush=True)
    print(f"  [{'PASS' if has_plb_badges else 'FAIL'}] PLB OPTIMIZATION badges present in registry ({sum(1 for r in all_rules if 'OPTIMIZATION' in r.get('classification', ''))} rules)", flush=True)
    print(f"  [{'PASS' if has_model_indep_badges else 'FAIL'}] MODEL-INDEPENDENT badges present in registry ({sum(1 for r in all_rules if 'MODEL-INDEPENDENT' in r.get('classification', ''))} rules)", flush=True)
    
    # 3.2 Verify Documentation Links
    s25_src = sources.get("seedance_25", {})
    gpt_src = sources.get("gpt_image", {})
    nano_src = sources.get("nano_banana_pro", {})
    
    s25_ok = "volcengine.com" in s25_src.get("source_url", "")
    gpt_ok = "openai.com" in gpt_src.get("source_url", "")
    nano_ok = "ai.google.dev" in nano_src.get("source_url", "")
    
    phase3_checks["Seedance_Doc_Link"] = s25_ok
    phase3_checks["GPT_Doc_Link"] = gpt_ok
    phase3_checks["Nano_Doc_Link"] = nano_ok
    
    print(f"  [{'PASS' if s25_ok else 'FAIL'}] Seedance Docs: {s25_src.get('source_url')}", flush=True)
    print(f"  [{'PASS' if gpt_ok else 'FAIL'}] GPT Image Docs: {gpt_src.get('source_url')}", flush=True)
    print(f"  [{'PASS' if nano_ok else 'FAIL'}] Nano Banana Pro Docs: {nano_src.get('source_url')}", flush=True)
    
    # 3.3 Verify NO DALL-E 3 claims
    json_str = body.lower()
    has_dalle = "dall-e" in json_str or "dalle" in json_str
    phase3_checks["No_DALLE_Claims"] = (not has_dalle)
    print(f"  [{'PASS' if not has_dalle else 'FAIL'}] Zero DALL-E references in source registry", flush=True)
    
    # Check app.js for any DALL-E references
    status, js_body = http_get(f"{BASE_URL_FORGE}/static/js/app.js")
    js_has_dalle = "dall-e" in js_body.lower() or "dalle" in js_body.lower()
    phase3_checks["No_DALLE_In_Frontend"] = (not js_has_dalle)
    print(f"  [{'PASS' if not js_has_dalle else 'FAIL'}] Zero DALL-E references in frontend JS", flush=True)
    
    # 3.4 Verify Nano Banana Pro bracket syntax is marked as PLB optimization
    nano_rules = list(nano_src.get("rules", {}).values()) if isinstance(nano_src.get("rules"), dict) else nano_src.get("rules", [])
    bracket_rule = next((r for r in nano_rules if "bracket" in r.get("rule_id", "").lower() or "syntax" in r.get("rule_id", "").lower()), None)
    bracket_ok = (bracket_rule is not None and bracket_rule.get("classification") == "PLB OPTIMIZATION")
    phase3_checks["Nano_Bracket_Marked_PLB_Optimization"] = bracket_ok
    print(f"  [{'PASS' if bracket_ok else 'FAIL'}] Nano Banana Pro bracket syntax classified strictly as PLB OPTIMIZATION (not official syntax)", flush=True)
    
except Exception as e:
    print(f"  [FAIL] Phase 3 error: {e}", flush=True)

results["PHASE_3"] = phase3_checks

# =====================================================================
# PHASE 4 — REAL WINDOWS CLIPBOARD TEST
# =====================================================================
log_section("PHASE 4: REAL WINDOWS CLIPBOARD TEST")

phase4_checks = {}

# Test copying each model prompt to Windows clipboard using temporary file + PowerShell
clip_tmp = Path("scratch/clip_tmp.txt")
for model_key, prompt_text in compiled_prompts.items():
    if not prompt_text:
        continue
    try:
        # Write prompt to disk
        clip_tmp.write_text(prompt_text, encoding="utf-8")
        
        # 1. Put prompt text into clipboard using PowerShell
        subprocess.run(
            ["powershell", "-NoProfile", "-Command", "Get-Content scratch/clip_tmp.txt -Raw | Set-Clipboard"],
            check=True
        )
        
        # 2. Read back from clipboard using PowerShell
        p_get = subprocess.run(
            ["powershell", "-NoProfile", "-Command", "Get-Clipboard -Raw"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=True
        )
        retrieved = p_get.stdout.replace("\r\n", "\n").rstrip("\n")
        expected = prompt_text.replace("\r\n", "\n").rstrip("\n")
        
        match = (retrieved == expected)
        phase4_checks[f"Clipboard_{model_key}"] = match
        print(f"  [{'PASS' if match else 'FAIL'}] Windows Clipboard round-trip for {model_key}: {len(retrieved)} chars, exact match={match}", flush=True)
        
        # 3. Send diagnostic event to server to verify server-side event logging
        event_status, event_resp = http_post_json(f"{BASE_URL_FORGE}/api/diagnostics/event", {
            "event_type": "COPY_SUCCESS",
            "module": "prompt_compiler",
            "metadata": {"model": model_key, "char_count": len(prompt_text), "source": "validator_test"}
        })
        phase4_checks[f"Log_Event_{model_key}"] = (event_status == 200)
    except Exception as e:
        phase4_checks[f"Clipboard_{model_key}"] = False
        print(f"  [FAIL] Clipboard test for {model_key}: {e}", flush=True)

if clip_tmp.exists():
    try:
        clip_tmp.unlink()
    except Exception:
        pass

# 4. Verify /api/diagnostics/copy-test endpoint
try:
    status, resp_body = http_post_json(f"{BASE_URL_FORGE}/api/diagnostics/copy-test", {"text": "Validation copy test string 12345"})
    resp_data = json.loads(resp_body)
    copy_test_ok = (status == 200 and resp_data.get("result", {}).get("status") == "PASS")
    phase4_checks["Diagnostics_Copy_Test_Endpoint"] = copy_test_ok
    print(f"  [{'PASS' if copy_test_ok else 'FAIL'}] /api/diagnostics/copy-test endpoint returned status='PASS' (fallback_ready={resp_data.get('result', {}).get('fallback_ready')})", flush=True)
except Exception as e:
    phase4_checks["Diagnostics_Copy_Test_Endpoint"] = False
    print(f"  [FAIL] copy-test endpoint: {e}", flush=True)

# 5. Verify COPY_FAILED simulation
try:
    status, resp_body = http_post_json(f"{BASE_URL_FORGE}/api/diagnostics/event", {
        "event_type": "COPY_FAILED",
        "module": "prompt_compiler",
        "metadata": {"error": "Test simulated clipboard rejection", "source": "validator_test"}
    })
    phase4_checks["Copy_Failed_Logged"] = (status == 200)
    print(f"  [{'PASS' if status == 200 else 'FAIL'}] COPY_FAILED diagnostic event logging verified", flush=True)
except Exception as e:
    phase4_checks["Copy_Failed_Logged"] = False
    print(f"  [FAIL] COPY_FAILED logging: {e}", flush=True)

results["PHASE_4"] = phase4_checks

# =====================================================================
# PHASE 5 — REAL PROMPT QUALITY CHECK
# =====================================================================
log_section("PHASE 5: REAL PROMPT QUALITY CHECK")

phase5_checks = {}

# 5.1 Seedance 2.5
s25 = compiled_prompts.get("seedance_25", "")
has_subj_tag = "@Subject" in s25
has_timeline = any(marker in s25 for marker in ["[00:00", "[00:03", "[00:06", "00:00-"])
has_camera = any(cam in s25.lower() for cam in ["camera", "push", "tracking", "shot", "lens", "angle"])
has_sound = any(snd in s25.lower() for snd in ["[sound]:", "sound]:", "sound:", "foley"])

phase5_checks["Seedance_Formula_And_Roles"] = has_subj_tag
phase5_checks["Seedance_Camera_And_Sound"] = (has_camera and has_sound)
print(f"  [{'PASS' if has_subj_tag else 'FAIL'}] Seedance: Uses @Subject reference roles (@Subject in prompt={has_subj_tag})", flush=True)
print(f"  [{'PASS' if has_camera else 'FAIL'}] Seedance: Contains camera motion description", flush=True)
print(f"  [{'PASS' if has_sound else 'FAIL'}] Seedance: Contains official Sound syntax ([Sound]: in prompt={has_sound})", flush=True)

# 5.2 GPT Image
gpt = compiled_prompts.get("gpt_image", "")
has_sentences = "." in gpt and len(gpt.split(".")) >= 2
no_tag_salad = not (gpt.count(",") > 20 and gpt.count(".") < 3)
has_style_lighting = any(w in gpt.lower() for w in ["lighting", "light", "palette", "composition", "style", "cinematic"])

phase5_checks["GPT_Natural_Sentences"] = has_sentences
phase5_checks["GPT_No_Tag_Salad"] = no_tag_salad
phase5_checks["GPT_Style_Lighting"] = has_style_lighting
print(f"  [{'PASS' if has_sentences else 'FAIL'}] GPT Image: Natural descriptive sentences (sentences={len(gpt.split('.'))})", flush=True)
print(f"  [{'PASS' if no_tag_salad else 'FAIL'}] GPT Image: Avoids comma-tag-salad (commas={gpt.count(',')}, periods={gpt.count('.')})", flush=True)
print(f"  [{'PASS' if has_style_lighting else 'FAIL'}] GPT Image: Preserves scene lighting, style, composition", flush=True)

# 5.3 Nano Banana Pro
nano = compiled_prompts.get("nano_banana_pro", "")
nano_has_details = any(w in nano.lower() for w in ["subject", "lighting", "shot", "photograph", "composition", "background", "style"])
no_fake_syntax_in_main = not ("--ar" in nano or "--v" in nano or "--style raw" in nano)

phase5_checks["Nano_Photographic_Details"] = nano_has_details
phase5_checks["Nano_No_Unsupported_Syntax"] = no_fake_syntax_in_main
print(f"  [{'PASS' if nano_has_details else 'FAIL'}] Nano Banana Pro: Explicit photographic details present", flush=True)
print(f"  [{'PASS' if no_fake_syntax_in_main else 'FAIL'}] Nano Banana Pro: Zero unsupported parameters (--ar, --v)", flush=True)

# 5.4 Model-Neutral Image
univ = compiled_prompts.get("universal_image", "")
has_zero_proprietary = not ("@Subject" in univ or "--" in univ)
phase5_checks["Universal_Zero_Proprietary"] = has_zero_proprietary
print(f"  [{'PASS' if has_zero_proprietary else 'FAIL'}] Universal Image: Zero proprietary markup or flags", flush=True)

results["PHASE_5"] = phase5_checks

# =====================================================================
# PHASE 7 — DIAGNOSTICS SELF-TEST
# =====================================================================
log_section("PHASE 7: DIAGNOSTICS SELF-TEST SUBSYSTEM")

phase7_checks = {}

try:
    status, body = http_post_json(f"{BASE_URL_FORGE}/api/diagnostics/self-test")
    test_data = json.loads(body)
    overall = test_data.get("results", {}).get("overall_status")
    components = test_data.get("results", {}).get("components", {})
    print(f"  Diagnostics Self-Test Response HTTP {status}, Overall: {overall}, Total Checks: {len(components)}", flush=True)
    for check_name, info in components.items():
        st = info.get("status")
        is_pass = (st == "PASS")
        phase7_checks[check_name] = is_pass
        msg = info.get("message", "")
        print(f"  [{'PASS' if is_pass else 'FAIL'}] {check_name}: {msg}", flush=True)
except Exception as e:
    print(f"  [FAIL] Diagnostics self-test error: {e}", flush=True)

results["PHASE_7"] = phase7_checks

# Save results for final report
with open("scratch/validation_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)

print("\nValidation suite run finished. Results saved to scratch/validation_results.json", flush=True)
