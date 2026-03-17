"""
portfolio_generator.py

Generates a multi-page portfolio/proposal document for freelance gigs.
"""

import os
from projects_config import PROJECTS_BY_ROLE, DEFAULT_PROJECTS, EXECUTIVE_SUMMARY


def generate_portfolio(config: dict, keywords: dict) -> str:
    """
    Generate a tailored portfolio Markdown string.
    """
    personal = config["personal"]
    job_title = keywords.get("job_title") or "Enterprise Software Solutions"
    github_user = personal.get("github", "")
    github_base = "github.com/" + github_user.split("github.com/")[-1].strip("/") if github_user else ""

    # 1. Match Projects
    matched_role = None
    for role in PROJECTS_BY_ROLE.keys():
        if role.lower() in job_title.lower() or job_title.lower() in role.lower():
            matched_role = role
            break
    
    if matched_role:
        curated_list = PROJECTS_BY_ROLE[matched_role]
    else:
        curated_list = DEFAULT_PROJECTS

    # Limit to 3 projects as requested
    selected_projects = curated_list[:3]

    # 2. Build Page 1: Executive Summary
    lines = []
    lines.append(f"# {personal['name']}")
    lines.append(f"{personal.get('email', '')} | {personal.get('phone', '')} | {personal.get('linkedin', '')} | {github_base}")
    lines.append("\n---\n")
    lines.append("## EXECUTIVE SUMMARY\n")
    lines.append(f"**Core Philosophy:** {EXECUTIVE_SUMMARY['philosophy']}\n")
    lines.append(f"**Experience:** {EXECUTIVE_SUMMARY['experience']} (Prominent US Experience Highlighted)\n")
    lines.append(f"**Professional Standards:** {EXECUTIVE_SUMMARY['standard']}\n")
    lines.append("\nI specialize in delivering robust, production-ready software for global clients, ensuring high communication standards and technical excellence.\n")
    lines.append("\n---page---\n")

    # 3. Build Project Pages
    for i, p in enumerate(selected_projects):
        lines.append(f"## PROJECT SPOTLIGHT: {p['name']}")
        lines.append(f"**Goal:** {p['description']}")
        lines.append(f"**Tech Stack:** {p['tech_stack']}")
        
        repo_link = f"https://{github_base}/{p['github_repo']}" if github_base and p.get('github_repo') else "#"
        lines.append(f"**Code:** [GitHub Repository]({repo_link})\n")

        assets = p.get("assets", {})
        
        # Architecture Diagram
        arch_img = assets.get("architecture")
        if arch_img:
            lines.append(f"### System Architecture")
            lines.append(f"![Architecture Diagram for {p['name']}]({arch_img})")
        
        # Other assets
        if assets.get("metrics"):
             lines.append(f"**Performance Metrics:** {assets['metrics']}\n")
        
        setup_img = assets.get("setup")
        if setup_img:
            lines.append(f"### Local Setup & Environment")
            lines.append(f"![Localhost Setup for {p['name']}]({setup_img})")

        api_img = assets.get("api_docs")
        if api_img:
            lines.append(f"### API Documentation")
            lines.append(f"![API Docs for {p['name']}]({api_img})")

        if i < len(selected_projects) - 1:
            lines.append("\n---page---\n")

    return "\n".join(lines)
