"""
src/github_parser.py

Fetches and parses repositories from a GitHub profile.
"""

import requests
import logging

def get_github_repos(username: str) -> list:
    """
    Fetch all public repositories for a given GitHub username.
    
    Args:
        username: GitHub username (e.g., 'skushal746')
        
    Returns:
        List of dicts: [{'name': '...', 'url': '...', 'description': '...'}]
    """
    if not username:
        return []
        
    # Handle cases where full URL is provided
    if "github.com/" in username:
        username = username.split("github.com/")[-1].strip("/")

    url = f"https://api.github.com/users/{username}/repos?sort=updated&per_page=100"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        repos = response.json()
        
        parsed_repos = []
        for repo in repos:
            if not repo.get('fork'): # Only include original repos
                parsed_repos.append({
                    "name": repo.get("name"),
                    "url": repo.get("html_url"),
                    "description": repo.get("description") or "",
                    "stars": repo.get("stargazers_count", 0),
                    "language": repo.get("language", "")
                })
        
        return parsed_repos
    except Exception as e:
        logging.error(f"Failed to fetch GitHub repos for {username}: {e}")
        return []

def format_repos_for_llm(repos: list, limit: int = 15) -> str:
    """Format the list of repos into a string for LLM context."""
    if not repos:
        return "No public GitHub repositories found."
        
    lines = []
    # Sort by stars and then by name
    sorted_repos = sorted(repos, key=lambda x: x['stars'], reverse=True)
    
    for repo in sorted_repos[:limit]:
        desc = f" - {repo['description']}" if repo['description'] else ""
        lang = f" [{repo['language']}]" if repo['language'] else ""
        lines.append(f"- {repo['name']}{lang}: {repo['url']}{desc}")
        
    return "\n".join(lines)
