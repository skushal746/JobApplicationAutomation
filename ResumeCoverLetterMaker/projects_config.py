"""
src/projects_config.py

Contains a mapping of job roles to relevant projects and tech stacks.
This information is used to enrich cover letters with specific project details.
"""

PROJECTS_BY_ROLE = {
    "Backend Engineer": [
        {
            "name": "NodeExpress API",
            "tech_stack": "Node.js, Express, MongoDB, Redis",
            "description": "A production-ready RESTful API with robust error handling, security middleware, and graceful shutdown.",
            "github_repo": "NodeExpress-API",
            "assets": {
                "architecture": "FreelanceAutomation/PortfolioAssets/node_express_arch.png",
                "setup": "FreelanceAutomation/PortfolioAssets/node_express_setup.png",
                "api_docs": "FreelanceAutomation/PortfolioAssets/node_express_api.png",
                "metrics": "Uptime: 99.9%, Avg Latency: <50ms"
            }
        },
        {
            "name": "Distributed Task Queue",
            "tech_stack": "Python, Celery, RabbitMQ",
            "description": "Asynchronous task processing system capable of handling thousands of background jobs.",
            "github_repo": "distributed-task-queue",
            "assets": {
                "architecture": "FreelanceAutomation/PortfolioAssets/task_queue_arch.png"
            }
        }
    ],

    "Frontend Engineer": [
        {
            "name": "E-commerce Dashboard",
            "tech_stack": "React, TypeScript, TailwindCSS, Chart.js",
            "description": "Real-time analytics dashboard with dynamic visualization of sales data.",
            "github_repo": "ecommerce-dashboard"
        }
    ],
    "Full Stack Engineer": [
        {
            "name": "Job Application Automation",
            "tech_stack": "Python, Ollama, YAML, Markdown",
            "description": f"Automated pipeline for generating tailored resumes and cover letters using local LLMs.",
            "github_repo": "JobApplicationAutomation"
        },
        {
            "name": "Task Management App",
            "tech_stack": "Next.js, PostgreSQL, Prisma, Tailwind",
            "description": "Collaborative project management tool with real-time updates.",
            "github_repo": "task-master"
        }
    ],
    "AI/ML Engineer": [
        {
            "name": "Medical Image Classification",
            "tech_stack": "Python, PyTorch, CNN, OpenCV",
            "description": "Deep learning model for detecting anomalies in X-ray images with 95% accuracy.",
            "github_repo": "medical-imaging-ai"
        }
    ],
    "Java Developer": [
         {
            "name": "Microservices Banking System",
            "tech_stack": "Java, Spring Boot, Spring Cloud, PostgreSQL",
            "description": "Scalable microservices architecture for handling high-volume financial transactions.",
            "github_repo": "banking-microservices",
            "assets": {
                "architecture": "FreelanceAutomation/PortfolioAssets/banking_arch.png"
            }
        }
    ]
}

# Executive Summary details
EXECUTIVE_SUMMARY = {
    "philosophy": "Building decoupled, resilient, and highly observable systems that scale predictably.",
    "experience": "6+ years of US-based professional experience in enterprise software development.",
    "standard": "Committed to clean code, TDD, and automated CI/CD pipelines as a baseline for every project."
}


# Default projects if no specific role matches
DEFAULT_PROJECTS = [
    {
        "name": "Portfolio Website",
        "tech_stack": "HTML, CSS, JavaScript",
        "description": "Personal showcase of projects and professional experience.",
        "github_repo": "portfolio"
    }
]
