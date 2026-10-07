import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from scripts.video_seo_reverse_engineer import run_full_analysis

p = Path("C:/Users/Admin/Desktop/google-project/temp_uploads/378c9d_Rabbits & Horseradish_TJX_no_watermark.mp4")
out_md = Path("C:/Users/Admin/Desktop/google-project/temp_uploads/RABBITS-REPORT.md")
res = run_full_analysis(p, output_report_path=out_md)

seo = res["reconstructed_seo"]
print("==================================================================")
print(" 🐰 RABBITS & HORSERADISH RECONSTRUCTED SEO VERIFICATION")
print("==================================================================")
print(f"Primary Topic:       {seo['primary_topic']}")
print(f"Primary Keyword:     {seo['primary_keyword']}")
print(f"Secondary Keywords:  {seo['secondary_keywords']}")
print(f"Long-Tail Keywords:  {seo['long_tail_keywords'][:2]}")
print(f"SEO Titles (first 3):")
for t in seo["seo_titles"][:3]:
    print(f"  - {t}")
print(f"Retention Titles:")
for t in seo["retention_titles"]:
    print(f"  - {t}")
print(f"TikTok Caption:      {seo['platforms']['tiktok']['caption']}")
print(f"Instagram Caption:   {seo['platforms']['instagram_reels']['caption'][:100]}...")
print(f"YouTube Shorts:      {seo['platforms']['youtube_shorts']['title']}")
print(f"Pinned Comment:      {seo['pinned_comment']}")

print("\n--- MASTER EVIDENCE TABLE ---")
for row in res["evidence_table"]:
    print(f"[{row['domain']}]")
    print(f"   Original:      {row['original']}")
    print(f"   Reconstructed: {row['reconstructed']}")
    print(f"   Confidence:    {row['confidence']}")
    print(f"   Unknowns:      {row['unknowns']}")

# Assertions to guarantee strict adherence to user rules:
assert "378c9d" not in seo["primary_keyword"], "Hash 378c9d found in primary keyword!"
assert "tjx" not in seo["primary_keyword"].lower(), "TJX found in primary keyword!"
assert "watermark" not in seo["primary_keyword"].lower(), "Watermark found in primary keyword!"
assert seo["primary_keyword"] == "rabbits eating horseradish", f"Unexpected primary keyword: {seo['primary_keyword']}"
assert res["original_metadata"]["title"] == "[NOT PRESENT IN SOURCE]", "Invented original title!"
assert res["original_metadata"]["caption_main"] == "[NOT PRESENT IN SOURCE]", "Invented original caption!"

print("\n🎉 ALL STRICT SEO QUALITY ASSERTIONS PASSED WITH 100% ACCURACY!")
