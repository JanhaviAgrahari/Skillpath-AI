from app.schemas.common import ResourceType
from app.schemas.learning_plan import LearningResource


RESOURCE_CATALOG: dict[str, list[LearningResource]] = {
    "Docker": [
        LearningResource(
            title="Docker Get Started",
            resource_type=ResourceType.DOCUMENTATION,
            url="https://docs.docker.com/get-started/",
            provider="Docker",
            estimated_minutes=90,
            notes="Best first pass for containers, images, and basic workflows.",
        ),
        LearningResource(
            title="Docker for the Absolute Beginner",
            resource_type=ResourceType.COURSE,
            url="https://kodekloud.com/courses/docker-for-the-absolute-beginner/",
            provider="KodeKloud",
            estimated_minutes=180,
            notes="Good practical walkthrough for container basics and compose-style thinking.",
        ),
    ],
    "PostgreSQL": [
        LearningResource(
            title="PostgreSQL Tutorial",
            resource_type=ResourceType.DOCUMENTATION,
            url="https://www.postgresql.org/docs/current/tutorial.html",
            provider="PostgreSQL",
            estimated_minutes=120,
            notes="Use this to build strong grounding in queries, tables, and transactions.",
        ),
        LearningResource(
            title="Exploring Explain",
            resource_type=ResourceType.ARTICLE,
            url="https://www.postgresql.org/docs/current/using-explain.html",
            provider="PostgreSQL",
            estimated_minutes=60,
            notes="Important for query planning and performance troubleshooting.",
        ),
    ],
    "SQL": [
        LearningResource(
            title="SQLBolt",
            resource_type=ResourceType.COURSE,
            url="https://sqlbolt.com/",
            provider="SQLBolt",
            estimated_minutes=180,
            notes="Fast interactive refresher for joins, filters, and data retrieval patterns.",
        ),
        LearningResource(
            title="Use The Index, Luke!",
            resource_type=ResourceType.ARTICLE,
            url="https://use-the-index-luke.com/",
            provider="Use The Index, Luke!",
            estimated_minutes=120,
            notes="Great for query optimization and index intuition.",
        ),
    ],
    "FastAPI": [
        LearningResource(
            title="FastAPI Tutorial",
            resource_type=ResourceType.DOCUMENTATION,
            url="https://fastapi.tiangolo.com/tutorial/",
            provider="FastAPI",
            estimated_minutes=180,
            notes="Work through request validation, routing, and dependency injection.",
        ),
        LearningResource(
            title="FastAPI Best Practices",
            resource_type=ResourceType.ARTICLE,
            url="https://github.com/zhanymkanov/fastapi-best-practices",
            provider="GitHub",
            estimated_minutes=90,
            notes="Useful once the fundamentals are clear and you want cleaner structure.",
        ),
    ],
    "Python": [
        LearningResource(
            title="Real Python Learning Paths",
            resource_type=ResourceType.COURSE,
            url="https://realpython.com/learning-paths/",
            provider="Real Python",
            estimated_minutes=180,
            notes="Practical coverage with strong backend-friendly examples.",
        ),
        LearningResource(
            title="Python Docs Tutorial",
            resource_type=ResourceType.DOCUMENTATION,
            url="https://docs.python.org/3/tutorial/",
            provider="Python",
            estimated_minutes=120,
            notes="Helpful for building precise language foundations.",
        ),
    ],
    "REST APIs": [
        LearningResource(
            title="Microsoft REST API Guidelines",
            resource_type=ResourceType.DOCUMENTATION,
            url="https://github.com/microsoft/api-guidelines",
            provider="Microsoft",
            estimated_minutes=90,
            notes="Great reference for API design, consistency, and client-friendly behavior.",
        ),
        LearningResource(
            title="HTTP Status Codes",
            resource_type=ResourceType.DOCUMENTATION,
            url="https://developer.mozilla.org/en-US/docs/Web/HTTP/Status",
            provider="MDN",
            estimated_minutes=45,
            notes="Useful for clear API semantics and interview explanations.",
        ),
    ],
    "CI/CD": [
        LearningResource(
            title="GitHub Actions Documentation",
            resource_type=ResourceType.DOCUMENTATION,
            url="https://docs.github.com/en/actions",
            provider="GitHub",
            estimated_minutes=120,
            notes="Practical path to build automated test and deploy pipelines quickly.",
        ),
        LearningResource(
            title="CI/CD Concepts",
            resource_type=ResourceType.ARTICLE,
            url="https://www.redhat.com/en/topics/devops/what-is-ci-cd",
            provider="Red Hat",
            estimated_minutes=40,
            notes="Good conceptual primer before implementing workflows.",
        ),
    ],
    "Kubernetes": [
        LearningResource(
            title="Kubernetes Basics",
            resource_type=ResourceType.DOCUMENTATION,
            url="https://kubernetes.io/docs/tutorials/kubernetes-basics/",
            provider="Kubernetes",
            estimated_minutes=180,
            notes="Strong first path for deployments, pods, and services.",
        )
    ],
    "Database Design": [
        LearningResource(
            title="Database Design Basics",
            resource_type=ResourceType.ARTICLE,
            url="https://www.lucidchart.com/pages/database-diagram/database-design",
            provider="Lucidchart",
            estimated_minutes=60,
            notes="Good conceptual grounding for schemas and relationships.",
        )
    ],
    "Backend Development": [
        LearningResource(
            title="Backend Developer Roadmap",
            resource_type=ResourceType.ARTICLE,
            url="https://roadmap.sh/backend",
            provider="roadmap.sh",
            estimated_minutes=75,
            notes="Useful overview to connect topics into a coherent journey.",
        )
    ],
}
