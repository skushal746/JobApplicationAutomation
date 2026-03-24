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
@click.option("--output", default="output", help="Output directory.")
def main(output):
    config = load_config(CONFIG_PATH)
    os.makedirs(output, exist_ok=True)
    
    # ── Resolve URLs ────────────────────────────────────────────────
    urls = config.get("job_urls", [])

    if not urls:
        print("❌ No URLs found in config.")
        return

    # ── Load Base Documents (Once) ──────────────────────────────────
    resume_path = config["assets"]["resume"]
    cover_path = config["assets"]["cover_letter"]
    
    # Read resume as text directly (if .md) or extract from PDF
    if resume_path.endswith('.md'):
        with open(resume_path, 'r') as f:
            resume_text = f.read()
    else:
        resume_text = extract_text_from_pdf(resume_path)
    
    # Read cover letter as text directly (if .md) or extract from PDF
    if cover_path.endswith('.md'):
        with open(cover_path, 'r') as f:
            cover_text = f.read()
    else:
        cover_text = extract_text_from_pdf(cover_path)

    print(f"📄 Base documents loaded (Resume: {len(resume_text)} chars, Cover Letter: {len(cover_text)} chars)")

    # ── Process Each URL ────────────────────────────────────────────
    for i, job_url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}] Processing: {job_url}")
        try:
            job_text = scrape_job(job_url)
            keywords = extract_keywords(job_text, config)
            
            # 1. Generate Cover Letter
            slug = keywords.get("company_name", "company").lower().replace(" ", "_")
            cl_md_path = os.path.join(output, f"cover_letter_{slug}.md")
            cl_pdf_path = os.path.join(output, f"cover_letter_{slug}.pdf")
            
            cover_md = generate_cover_letter(cover_text, config, keywords, job_text)
            with open(cl_md_path, "w") as f:
                f.write(cover_md)
            md_to_pdf(cl_md_path, cl_pdf_path)
            print(f"  ✓ Generated Cover Letter: {cl_pdf_path}")
            
            # 2. Generate Resume (if enabled)
            if config.get("generate_resume", False):
                res_md_path = os.path.join(output, f"resume_{slug}.md")
                res_pdf_path = os.path.join(output, f"resume_{slug}.pdf")
                
                if config.get("tailor_resume", False):
                    print(f"  ⏳ Tailoring resume for {slug}...")
                    resume_md = generate_resume(resume_text, config, keywords)
                else:
                    resume_md = resume_text
                
                with open(res_md_path, "w") as f:
                    f.write(resume_md)
                md_to_pdf(res_md_path, res_pdf_path)
                print(f"  ✓ Generated Resume: {res_pdf_path}")

            # 3. Copy to secondary location
            copy_dir = config.get("cover_letter_copy_dir")
            if copy_dir:
                import shutil
                os.makedirs(copy_dir, exist_ok=True)
                # Copy cover letter
                shutil.copy2(cl_pdf_path, os.path.join(copy_dir, os.path.basename(cl_pdf_path)))
                # Copy resume (if generated)
                if config.get("generate_resume", False):
                    shutil.copy2(res_pdf_path, os.path.join(copy_dir, os.path.basename(res_pdf_path)))
                print(f"  ✓ Files copied to: {copy_dir}")
                
        except Exception as e:
            print(f"  ❌ Failed to process {job_url}: {e}")



if __name__ == "__main__":
    main()
