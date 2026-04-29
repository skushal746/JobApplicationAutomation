import urllib.request
import json
import ssl

def generate_description_from_readme(repo_full_name, default_branch, fallback_desc, ctx):
    # Fetch README
    readme_content = None
    for filename in ["README.md", "readme.md", "README.MD", "Readme.md"]:
        raw_url = f"https://raw.githubusercontent.com/{repo_full_name}/{default_branch}/{filename}"
        req = urllib.request.Request(raw_url, headers={'User-Agent': 'Mozilla/5.0'})
        try:
            with urllib.request.urlopen(req, context=ctx) as response:
                readme_content = response.read().decode('utf-8', errors='ignore')
                break
        except:
            continue
            
    if not readme_content:
        return fallback_desc
        
    print(f"  -> Found README for {repo_full_name}, summarizing with Ollama...")
    
    # Call Ollama
    ollama_url = "http://localhost:11434/api/generate"
    prompt = f"Based on the following README file content, write a concise 2-3 sentence project description suitable for a resume or cover letter. Do not include any introductory phrases like 'Here is a description', just output the description itself.\n\nREADME content:\n{readme_content[:3000]}"
    
    payload = {
        "model": "llama3.2:latest",
        "prompt": prompt,
        "stream": False
    }
    
    data = json.dumps(payload).encode('utf-8')
    ollama_req = urllib.request.Request(ollama_url, data=data, headers={'Content-Type': 'application/json'})
    
    try:
        with urllib.request.urlopen(ollama_req) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result.get('response', fallback_desc).strip()
    except Exception as e:
        print(f"  [!] Failed to generate description with Ollama for {repo_full_name}: {e}")
        return fallback_desc

def fetch_github_repos():
    # To bypass potential SSL issues locally
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    # GitHub API endpoint to get user repositories
    # per_page=100 gets up to 100 repos, sort=updated sorts by recently updated
    url = "https://api.github.com/users/skushal746/repos?per_page=100&sort=updated"
    
    # GitHub requires a User-Agent header
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    
    try:
        print("Fetching repositories from GitHub API...")
        with urllib.request.urlopen(req, context=ctx) as response:
            data = json.loads(response.read().decode())
            
        output_path = "/Users/kushalsharma/Documents/Projects2026/JobApplicationAutomation/my_github_projects.md"
        
        with open(output_path, "w", encoding='utf-8') as f:
            f.write("# My GitHub Projects\n\n")
            f.write("This file contains an automatically generated list of my GitHub projects, suitable for use in resumes, cover letters, and freelance proposals.\n\n")
            f.write("---\n\n")
            
            project_count = 0
            for repo in data:
                # Typically, you only want to showcase original projects (not forks)
                # If you want to include forks, you can remove this check.
                if repo.get("fork"):
                    continue 
                    
                name = repo.get("name", "N/A").replace("-", " ").title()
                fallback_desc = repo.get("description")
                if not fallback_desc:
                    fallback_desc = "No description provided."
                    
                repo_full_name = repo.get("full_name")
                default_branch = repo.get("default_branch", "main")
                
                print(f"Processing: {name}")
                desc = generate_description_from_readme(repo_full_name, default_branch, fallback_desc, ctx)
                
                # Get the primary language
                language = repo.get("language")
                
                # Get tags/topics if any
                topics = repo.get("topics", [])
                
                # Combine them for "Technologies used"
                techs = []
                if language:
                    techs.append(language)
                if topics:
                    techs.extend([t.replace("-", " ").title() for t in topics])
                    
                # Use a set to remove potential duplicates (ignoring case)
                unique_techs = []
                seen = set()
                for tech in techs:
                    if tech.lower() not in seen:
                        seen.add(tech.lower())
                        unique_techs.append(tech)
                        
                tech_str = ", ".join(unique_techs) if unique_techs else "Not specified"
                html_url = repo.get("html_url", "")
                
                f.write(f"## [{name}]({html_url})\n")
                f.write(f"- **Technologies:** {tech_str}\n")
                f.write(f"- **Description:** {desc}\n\n")
                
                project_count += 1
                
        print(f"Successfully processed {project_count} original projects and saved to {output_path}")
        
    except Exception as e:
        print("Error fetching or processing data:", e)

if __name__ == "__main__":
    fetch_github_repos()
