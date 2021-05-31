import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="scraper",
    version="1.0.0",
    author="Gediminas Šimavičius",
    author_email="gediminas.simavicius@gmail.com",
    description="Package for scraping value.today website.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Gedas-LT/value.today-web-scraper",
    install_requires=[
        "beautifulsoup4",
        "fake-useragent",
        "pandas",
        "pytest",
        "requests"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(),
    python_requires=">=3.6",
)