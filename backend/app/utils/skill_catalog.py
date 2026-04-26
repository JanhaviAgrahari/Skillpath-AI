from app.schemas.common import SkillCategory


SKILL_DEFINITIONS: dict[str, dict[str, object]] = {
    "python": {
        "canonical_name": "Python",
        "category": SkillCategory.TECHNICAL,
        "aliases": ["python", "py"],
        "adjacent": ["FastAPI", "Django", "Flask"],
    },
    "fastapi": {
        "canonical_name": "FastAPI",
        "category": SkillCategory.FRAMEWORK,
        "aliases": ["fastapi"],
        "adjacent": ["Python", "REST APIs"],
    },
    "sql": {
        "canonical_name": "SQL",
        "category": SkillCategory.DATABASE,
        "aliases": ["sql"],
        "adjacent": ["PostgreSQL", "MySQL", "Database Design"],
    },
    "postgresql": {
        "canonical_name": "PostgreSQL",
        "category": SkillCategory.DATABASE,
        "aliases": ["postgresql", "postgres"],
        "adjacent": ["SQL", "Database Design"],
    },
    "mysql": {
        "canonical_name": "MySQL",
        "category": SkillCategory.DATABASE,
        "aliases": ["mysql"],
        "adjacent": ["SQL", "PostgreSQL"],
    },
    "docker": {
        "canonical_name": "Docker",
        "category": SkillCategory.TOOL,
        "aliases": ["docker", "docker compose", "containerization"],
        "adjacent": ["Kubernetes", "CI/CD"],
    },
    "kubernetes": {
        "canonical_name": "Kubernetes",
        "category": SkillCategory.CLOUD,
        "aliases": ["kubernetes", "k8s"],
        "adjacent": ["Docker", "Cloud Deployment"],
    },
    "aws": {
        "canonical_name": "AWS",
        "category": SkillCategory.CLOUD,
        "aliases": ["aws", "amazon web services"],
        "adjacent": ["Cloud Deployment", "Docker"],
    },
    "rest apis": {
        "canonical_name": "REST APIs",
        "category": SkillCategory.TECHNICAL,
        "aliases": ["rest api", "rest apis", "api development", "apis"],
        "adjacent": ["FastAPI", "Backend Development"],
    },
    "backend development": {
        "canonical_name": "Backend Development",
        "category": SkillCategory.DOMAIN,
        "aliases": ["backend development", "backend engineering"],
        "adjacent": ["REST APIs", "Database Design"],
    },
    "database design": {
        "canonical_name": "Database Design",
        "category": SkillCategory.DOMAIN,
        "aliases": ["database design", "schema design", "data modeling"],
        "adjacent": ["SQL", "PostgreSQL"],
    },
    "git": {
        "canonical_name": "Git",
        "category": SkillCategory.TOOL,
        "aliases": ["git", "github", "gitlab"],
        "adjacent": ["CI/CD"],
    },
    "ci/cd": {
        "canonical_name": "CI/CD",
        "category": SkillCategory.TOOL,
        "aliases": ["ci/cd", "cicd", "continuous integration", "continuous deployment"],
        "adjacent": ["Docker", "Git"],
    },
    "javascript": {
        "canonical_name": "JavaScript",
        "category": SkillCategory.TECHNICAL,
        "aliases": ["javascript", "js"],
        "adjacent": ["TypeScript", "Node.js"],
    },
    "typescript": {
        "canonical_name": "TypeScript",
        "category": SkillCategory.TECHNICAL,
        "aliases": ["typescript", "ts"],
        "adjacent": ["JavaScript", "Node.js"],
    },
    "node.js": {
        "canonical_name": "Node.js",
        "category": SkillCategory.FRAMEWORK,
        "aliases": ["node.js", "nodejs", "node js"],
        "adjacent": ["JavaScript", "TypeScript"],
    },
}
