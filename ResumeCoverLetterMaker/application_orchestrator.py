"""
application_orchestrator.py

Orchestrates the job application generation process based on URLs.
"""

import os
import yaml
import logging
from typing import List, Dict

from document_generator import (
    generate_resume,
    generate_cover_letter,
    generate_freelance_proposal,
    select_relevant_projects
)
from utils.scraper import scrape_job
from utils.latex import compile_tex_to_pdf
from utils.ai import extract_keywords

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


class JobApplicationManager:
    def __init__(self, config_path: str = "config-kushal.yaml", output_dir: str = "output"):
        """
        Initialize the manager with configuration.
        """
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        
        try:
            with open(config_path, "r") as f:
                self.config = yaml.safe_load(f)
        except Exception as e:
            logging.error(f"Failed to load config {config_path}: {e}")
            self.config = {"personal": {"name": "Kushal Sharma"}, "use_local": True}
            
        # Define paths to templates
        self.assets_dir = os.path.join(os.path.dirname(__file__), "assets")
        self.resume_template_path = os.path.join(self.assets_dir, "KushalSharma_Resume.tex")
        self.cover_letter_template_path = os.path.join(self.assets_dir, "Vanilla_Cover_Letter.tex")
        self.freelance_proposal_template_path = os.path.join(self.assets_dir, "Vanilla_Freelance_Proposal.tex")
        
    def _read_file(self, path: str) -> str:
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            logging.error(f"Failed to read file {path}: {e}")
            return ""

    def process_urls(self, urls_info: List[Dict[str, str]]):
        """
        Process a list of URLs and generate corresponding documents.
        
        Args:
            urls_info: List of dicts like [{"url": "https://...", "type": "job"}]
                       where "type" is either "job" or "freelance".
        """
        # Load templates
        resume_text = self._read_file(self.resume_template_path)
        cover_letter_text = self._read_file(self.cover_letter_template_path)
        proposal_text = self._read_file(self.freelance_proposal_template_path)
        
        for index, item in enumerate(urls_info):
            url = item.get("url", "Manual Entry")
            link_type = item.get("type", "job").lower()
            job_text = item.get("job_description")
            
            if not url and not job_text:
                logging.warning("Skipping item with no URL and no job description.")
                continue
                
            logging.info(f"Processing {link_type} for: {url}")
            
            # Scrape only if job_text is not manually provided
            if not job_text:
                try:
                    job_text = scrape_job(url)
                except Exception as e:
                    logging.error(f"Failed to scrape {url}: {e}")
                    continue
                
            # Extract keywords using Ollama/Gemini via ai.py
            logging.info("Extracting keywords from job description...")
            keywords = extract_keywords(job_text, self.config)
            
            # Identify relevant projects using the LLM
            logging.info("Selecting relevant projects from GitHub portfolio...")
            relevant_projects_text = select_relevant_projects(keywords, job_text, self.config)
            
            generated_pdfs = []
            
            if link_type == "job":
                # Generate Resume
                logging.info("Generating tailored Resume (LaTeX)...")
                tailored_resume_tex = generate_resume(resume_text, self.config, keywords, relevant_projects_text)
                resume_tex_path = os.path.join(self.output_dir, f"Resume_job_{index+1}.tex")
                with open(resume_tex_path, "w", encoding="utf-8") as f:
                    f.write(tailored_resume_tex)
                
                # Generate Cover Letter
                logging.info("Generating tailored Cover Letter (LaTeX)...")
                tailored_cl_tex = generate_cover_letter(cover_letter_text, self.config, keywords, job_text, relevant_projects_text)
                cl_tex_path = os.path.join(self.output_dir, f"CoverLetter_job_{index+1}.tex")
                with open(cl_tex_path, "w", encoding="utf-8") as f:
                    f.write(tailored_cl_tex)
                    
                # Compile to PDF
                logging.info("Compiling LaTeX to PDF...")
                try:
                    resume_pdf = compile_tex_to_pdf(resume_tex_path, self.output_dir)
                    cl_pdf = compile_tex_to_pdf(cl_tex_path, self.output_dir)
                    generated_pdfs.extend([resume_pdf, cl_pdf])
                except Exception as e:
                    logging.error(f"Compilation failed: {e}")
                    
            elif link_type == "freelance":
                # Generate Freelance Proposal
                logging.info("Generating tailored Freelance Proposal (LaTeX)...")
                tailored_proposal_tex = generate_freelance_proposal(proposal_text, self.config, keywords, job_text, relevant_projects_text)
                proposal_tex_path = os.path.join(self.output_dir, f"Proposal_freelance_{index+1}.tex")
                with open(proposal_tex_path, "w", encoding="utf-8") as f:
                    f.write(tailored_proposal_tex)
                    
                # Compile to PDF
                logging.info("Compiling LaTeX to PDF...")
                try:
                    proposal_pdf = compile_tex_to_pdf(proposal_tex_path, self.output_dir)
                    generated_pdfs.append(proposal_pdf)
                except Exception as e:
                    logging.error(f"Compilation failed: {e}")
            else:
                logging.warning(f"Unknown link type '{link_type}', skipping.")
                
            logging.info(f"Finished processing {url}. Generated PDFs: {generated_pdfs}\n")

if __name__ == "__main__":
    # Example usage:
    manager = JobApplicationManager()
    sample_urls = [
        # Example URLs
        # {"url": "https://example.com/job1", "type": "job"},
        # {"url": "https://example.com/freelance1", "type": "freelance"}
        {"url": "https://www.upwork.com/jobs/~022049184413304168405", "type": "freelance", "job_description": """ 
            We are seeking a senior back-end engineer with expertise in AI engineering to develop a production-ready Agent As a Model and SaaS platform. The platform will serve the healthcare and education industries, requiring domain-specific knowledge. The ideal candidate will have experience in designing scalable architectures and integrating AI models into cloud-based systems. Strong problem-solving skills and the ability to work in a fast-paced environment are essential.
        """},
        {"url": "https://www.upwork.com/jobs/Node-developer-Full-stack-developer_~022049125295108733081", "type": "freelance", "job_description": """ 
            Summary
            We are looking for a skilled Node.js Developer to join our team and help build scalable, high-performance web products. This role requires strong experience in backend development with Node.js, along with solid frontend capabilities using React.
            You will work on modern web application development, contributing to both backend architecture and frontend implementation as part of a full-stack development process.


            Key Responsibilities:

            Experience in SaaS platform development
            Develop and maintain backend services using Node.js
            Build responsive and dynamic user interfaces with React, HTML, and CSS
            Write clean and scalable code using JavaScript and TypeScript
            Design and integrate API endpoints and third-party services
            Collaborate on full-cycle web application development
            Support and extend existing systems, including components built with Python

            Requirements:

            Strong experience with Node.js and backend architecture
            Solid knowledge of React, HTML and CSS
            Proficiency in JavaScript and TypeScript
            Experience with API design and integrations
            Understanding of full-stack development principles
            Familiarity with Python is a plus


            Nice to Have:

            Experience working on complex web applications
            Ability to take ownership of features end-to-end
            Strong problem-solving and communication skills
            Project Type: Ongoing / Long-term
            Level: Mid to Senior
            We’re looking for someone who can think beyond code — someone who understands how to build reliable, scalable, and user-focused products.
            👉 Send your experience, portfolio, and a short intro.
        """},
    ]
    manager.process_urls(sample_urls)
    pass
