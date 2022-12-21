import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="odoo-tools-openapi",
    version="0.1.0",
    author="Loïc Faure-Lacroix <lamerstar@gmail.com>",
    author_email="lamerstar@gmail.com",
    description="Odoo Tools Rest",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://odoo-tools.readthedocs.io",
    project_urls={
        "Source": "https://github.com/llacroix/odoo-tools-rest",
        "Documentation": "https://odoo-tools-rest.readthedocs.io",
    },
    packages=setuptools.find_packages(),
    install_requires=[
        "openapi3",
        "requests",
        "click",
        "jinja2",
    ],
    extras_require={
        "docs": [
            "sphinx",
            "furo",
            "sphinx-argparse",
            "sphinx-click",
            "sphinxcontrib.asciinema",
        ],
        "test": [
            "mock",
            "pytest",
            "pytest-cov"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    entry_points={
        "odootools.command.ext": [
            "gen = odoo_tools_openapi.command:openapi"
        ]
    },
    package_data={
        "odoo_tools_rest": [
            "templates/*.jinja",
        ],
    }
)
