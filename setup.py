from setuptools import setup, find_packages

def parse_requirements(filename):
    with open(filename, encoding="utf-8") as f:
        return [
            line.strip()
            for line in f
            if line.strip() and not line.startswith("#")
        ]

setup(
    name="speedupy",
    version="0.1.0",
    description="SpeeduPy: sistema de cache para experimentos científicos",
    author="Clayton Escouper das Chagas",
    author_email="escouper@ime.eb.br",
    packages=find_packages(),
    include_package_data=True,  # Inclui arquivos como __init__.py, se não estiver usando MANIFEST
    install_requires=parse_requirements("requirements.txt"),
    python_requires=">=3.12",
)

