from pathlib import Path

# Target project folder
project = Path(r"C:\Users\pc\OneDrive\Desktop\password_checker_pro")

folders = [
    "app",
    "database",
    "models",
    "security",
    "ai",
    "services",
    "analytics",
    "reports",
    "utils",
    "components",
    "assets",
    "pages",
    "tests",
    "docs",
    ".github/workflows",
    ".streamlit",
]

files = [
    "app.py",
    "config.py",
    "requirements.txt",
    "pytest.ini",
    ".env.example",
    ".gitignore",
    "Dockerfile",
    "docker-compose.yml",
    "README.md",

    ".streamlit/config.toml",

    "app/__init__.py",

    "database/__init__.py",
    "database/connection.py",
    "database/init_db.py",

    "models/__init__.py",
    "models/models.py",

    "security/__init__.py",
    "security/hashing.py",
    "security/crypto.py",
    "security/validation.py",
    "security/common_passwords.py",

    "ai/__init__.py",
    "ai/analyzer.py",
    "ai/explainer.py",

    "services/__init__.py",
    "services/auth_service.py",
    "services/leak_checker.py",
    "services/password_service.py",
    "services/generator_service.py",
    "services/vault_service.py",
    "services/export_service.py",
    "services/activity_service.py",

    "analytics/__init__.py",
    "analytics/stats.py",

    "reports/__init__.py",
    "reports/report_generator.py",

    "utils/__init__.py",
    "utils/helpers.py",
    "utils/state.py",

    "components/__init__.py",
    "components/ui.py",
    "components/charts.py",
    "components/sidebar.py",

    "assets/style.css",
    "assets/common_passwords.txt",

    "pages/__init__.py",
    "pages/dashboard.py",
    "pages/analyzer.py",
    "pages/leak_checker.py",
    "pages/generator.py",
    "pages/vault.py",
    "pages/history.py",
    "pages/settings.py",
    "pages/admin.py",

    "tests/__init__.py",
    "tests/test_analyzer.py",
    "tests/test_leak_checker.py",
    "tests/test_security.py",
    "tests/test_generators.py",

    "docs/INSTALLATION.md",
    "docs/ARCHITECTURE.md",
    "docs/USER_GUIDE.md",

    ".github/workflows/ci.yml",
]

# Create root folder if it doesn't exist
project.mkdir(parents=True, exist_ok=True)

# Create folders
for folder in folders:
    (project / folder).mkdir(parents=True, exist_ok=True)

# Create files
for file in files:
    path = project / file
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch(exist_ok=True)

print("=" * 60)
print("✅ Project structure created successfully!")
print(f"📂 {project}")
print("=" * 60)