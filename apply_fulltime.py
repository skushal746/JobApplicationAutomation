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
@click.option("--url", help="Job URL")
@click.option("--output", default="output", help="Output dir")
def main(url, output):
    config = load_config(CONFIG_PATH)
    os.makedirs(output, exist_ok=True)
    
    # Logic similar to original main.py for full-time URLs
    # Simplified for the demonstration of the new structure
    if url:
        print(f"🚀 Applying for: {url}")
        job_text = scrape_job(url)
        keywords = extract_keywords(job_text, config)
        
        # Load assets
        resume_path = config["assets"]["resume"]
        cover_path = config["assets"]["cover_letter"]
        resume_text = extract_text_from_pdf(resume_path)
        cover_text = extract_text_from_pdf(cover_path)
        
        # Generate
        cover_md = generate_cover_letter(cover_text, config, keywords, job_text)
        
        slug = keywords.get("company_name", "company").lower().replace(" ", "_")
        md_path = os.path.join(output, f"cover_letter_{slug}.md")
        pdf_path = os.path.join(output, f"cover_letter_{slug}.pdf")
        
        with open(md_path, "w") as f:
            f.write(cover_md)
            
        md_to_pdf(md_path, pdf_path)
        print(f"✅ Full-time application generated: {pdf_path}")
        
        # Copy to secondary location
        copy_dir = config.get("cover_letter_copy_dir")
        if copy_dir:
            import shutil
            os.makedirs(copy_dir, exist_ok=True)
            dest = os.path.join(copy_dir, os.path.basename(pdf_path))
            shutil.copy2(pdf_path, dest)
            print(f"✅ Also copied to: {dest}")


if __name__ == "__main__":
    main()
