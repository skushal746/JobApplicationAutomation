#!/usr/bin/env python3
"""
apply_freelance.py — Freelance Portfolio/Proposal Generator
"""
import os
import sys
import yaml
import click
from utils.ai import extract_keywords
from portfolio_generator import generate_portfolio
from utils.pdf import convert as md_to_pdf

CONFIG_PATH = "config-kushal.yaml"

def load_config(path: str) -> dict:
    if not os.path.exists(path):
        print(f"❌ Config not found: {path}")
        sys.exit(1)
    with open(path) as f:
        return yaml.safe_load(f)

@click.command()
@click.option("--desc", help="Freelance project description")
@click.option("--output", default="output", help="Output dir")
def main(desc, output):
    config = load_config(CONFIG_PATH)
    os.makedirs(output, exist_ok=True)
    
    print("🚀 Generating Portfolio Proposal...")
    # Use provide desc or pick first from config
    job_text = desc if desc else config["job_descriptions"][0]["description"]
    keywords = extract_keywords(job_text, config)
    
    portfolio_md = generate_portfolio(config, keywords)
    
    md_path = os.path.join(output, "portfolio_proposal.md")
    pdf_path = os.path.join(output, "portfolio_proposal.pdf")
    
    with open(md_path, "w") as f:
        f.write(portfolio_md)
    
    md_to_pdf(md_path, pdf_path)
    print(f"✅ Portfolio generated: {pdf_path}")

if __name__ == "__main__":
    main()
