#!/usr/bin/env python3
"""
apply_fulltime.py — Full-time Job Application CLI
"""
import os
import sys
import yaml
import click
from utils.pdf_parser import extract_text_from_pdf
from utils.scraper import scrape_job
from utils.ai import extract_keywords
from document_generator import generate_resume, generate_cover_letter
from utils.pdf import convert as md_to_pdf

CONFIG_PATH = "config-kushal.yaml"

def load_config(path: str) -> dict:
    if not os.path.exists(path):
        print(f"❌ Config not found: {path}")
        sys.exit(1)
    with open(path) as f:
        return yaml.safe_load(f)

@click.command()
@click.option("--url", help="Single job URL (overrides config).")
@click.option("--output", default="output", help="Output directory.")
def main(url, output):
    config = load_config(CONFIG_PATH)
    os.makedirs(output, exist_ok=True)
    
    # ── Resolve URLs ────────────────────────────────────────────────
    if url:
        urls = [url]
    else:
        urls = config.get("job_urls", [])

    if not urls:
        print("❌ No URLs found in config or command line.")
        return

    # ── Load Base Documents (Once) ──────────────────────────────────
    resume_path = config["assets"]["resume"]
    cover_path = config["assets"]["cover_letter"]
    
    # Ensure paths are handled relative to project root or as absolute
    resume_text = extract_text_from_pdf(resume_path)
    print(f"📄 Base documents parsed (Resume: {len(resume_text)} chars)")
    print(resume_text)
    cover_text = extract_text_from_pdf(cover_path)
    print(f"📄 Base documents parsed (Cover Letter: {len(cover_text)} chars)")
    print(cover_text)

    # ── Process Each URL ────────────────────────────────────────────
    for i, job_url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}] Processing: {job_url}")
        try:
            job_text = scrape_job(job_url)
            keywords = extract_keywords(job_text, config)
            
            slug = keywords.get("company_name", "company").lower().replace(" ", "_")
            md_path = os.path.join(output, f"cover_letter_{slug}.md")
            pdf_path = os.path.join(output, f"cover_letter_{slug}.pdf")
            
            # Generate tailored content
            cover_md = generate_cover_letter(cover_text, config, keywords, job_text)
            
            with open(md_path, "w") as f:
                f.write(cover_md)
                
            md_to_pdf(md_path, pdf_path)
            print(f"  ✓ Generated: {pdf_path}")
            
            # Copy to secondary location
            copy_dir = config.get("cover_letter_copy_dir")
            if copy_dir:
                import shutil
                os.makedirs(copy_dir, exist_ok=True)
                dest = os.path.join(copy_dir, os.path.basename(pdf_path))
                shutil.copy2(pdf_path, dest)
                print(f"  ✓ Also copied to: {dest}")
                
        except Exception as e:
            print(f"  ❌ Failed to process {job_url}: {e}")



if __name__ == "__main__":
    main()
