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
            urls_info: List of dicts like:
              - {"url": "https://...", "type": "job"}  — scraped from URL
              - {"description": "...", "url": "", "type": "freelance"}  — description provided directly
            where "type" is either "job" or "freelance".
        """
        # Load templates
        resume_text = self._read_file(self.resume_template_path)
        cover_letter_text = self._read_file(self.cover_letter_template_path)
        proposal_text = self._read_file(self.freelance_proposal_template_path)
        
        for index, item in enumerate(urls_info):
            url = item.get("url", "").strip()
            link_type = item.get("type", "job").lower()
            # Accept either 'job_description' (legacy) or 'description' (freelance shorthand)
            job_text = item.get("job_description") or item.get("description")
            
            if not url and not job_text:
                logging.warning("Skipping item with no URL and no job description.")
                continue
            
            label = url if url else "(description provided directly)"
            logging.info(f"Processing {link_type} for: {label}")
            
            # Scrape only when no description was provided AND a valid URL exists
            if not job_text:
                if not url:
                    logging.warning("No job description and no URL to scrape — skipping.")
                    continue
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
                tailored_proposal_tex = generate_freelance_proposal(
                    proposal_text, self.config, keywords, job_text,
                    relevant_projects_text, resume_text=resume_text
                )
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
                
            logging.info(f"Finished processing {label}. Generated PDFs: {generated_pdfs}\n")

if __name__ == "__main__":
    # Example usage:
    manager = JobApplicationManager()
    sample_urls = [
        {"description": "I’ve integrated a ChatGPT-based solution into my website and am looking for a developer who can refine its implementation, improve efficiency, and enhance the overall user experience." ,"url": "", "type": "freelance"},
        {"description": """We are seeking a full-stack developer with strong expertise in using GenAI models, Java (Spring Boot) and Vue3 to join our eCommerce team. In this role, you will develop and maintain our centralized AI platform, support model service integration, and automate workflows across both frontend and backend systems. Experience with cloud deployment, international collaboration, and fluent English communication is required. Python and React experience are considered a plus.

                            Job Tasks and Responsibilities:
                            • Develop and maintain the AI platform, including various AI workflows, user management, parameter configuration, and feedback interfaces using Java (Spring Boot) for backend and Vue3 for frontend.
                            • Integrate AI models from different vendors (Google, OpenAI, etc) and build related API interfaces for image, text, video and other functionalities.
                            • Automate enterprise eCommerce workflows by integrating the system with other platforms like Salsify and Salesforce Commerce Cloud to push generated content and update records.
                            • Deploy and monitor services using Google Cloud infrastructure (Cloud Run, Cloud Functions, Vertex AI, etc.).
                            • Build task scheduling systems with queue handling, failure retry logic, and progress monitoring.
                            • Collaborate with designers, frontend engineers and marketeers to optimize prompt structures and AI output quality.
                            • Participate in English-speaking team meetings and write technical documentation in English.
                            ________________________________________
                            Qualifications:
                            • Education: Bachelor’s degree or above in Computer Science, Software Engineering, Artificial Intelligence, or related fields.
                            • Experience:
                            o 3+ years of Java development with Spring Boot (must-have)
                            o Strong hands-on experience with Vue3 (must-have)
                            o Experience with AI-related projects and cloud platforms required
                            o Python/React, eCommerce and/or PIM systems experience is a plus
                            ________________________________________
                            Knowledge and Skills:
                            • Backend: Proficient in Java (Spring Boot); Python (FastAPI, Flask) is a plus
                            • Frontend: Strong with Vue3 (must-have); React experience is a plus
                            • Expert in designing RESTful APIs, including authentication, pagination, and documentation
                            • Experience with async task frameworks and message queues (e.g., Celery, Kafka, RabbitMQ)
                            • Strong database knowledge (MongoDB, PostgreSQL) with optimization skills
                            • Hands-on with Google Cloud services (Cloud Run, Vertex AI, Cloud Storage, etc.)
                            • Experience with packaging and calling GenAI models
                            • Proficient in Docker, shell scripting, Git, and CI/CD workflows
                            • Basic image processing skills (Pillow, OpenCV) for format conversion and compatibility handling
                            ________________________________________
                            Language and Communication Skills:
                            • Fluent in English (spoken and written), capable of writing documentation and participating in technical discussions with international teams
                            ________________________________________
                            Personal Attributes:
                            • Proactive, analytical thinker with a strong sense of ownership
                            • Detail-oriented, with solid coding standards and documentation habits
                            • Quick learner who adapts to evolving technologies
                            • Effective communicator and team player in cross-functional environments""" ,"url": "", "type": "freelance"}
    ]
    manager.process_urls(sample_urls)
    pass
