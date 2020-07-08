import os
import setuptools

# REAME Correction
filepath = os.path.dirname(os.path.abspath(__file__))

with open(f"{filepath}/README.MD", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Youtube Wrapper Unofficial",
    version="0.0.1",
    author="Pedro Havay",
    author_email="pedrohavay@protonmail.com",
    description="Youtube Wrapper (Unofficial) made with Python and Selenium.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pedrohavay/youtube-wrapper-unofficial",
    packages=setuptools.find_packages(),
    install_requires=[
        "selenium==3.141.0",
        "lxml==4.5.0",
        "beautifulsoup4==4.8.2",
        "requests==2.21.0"
    ]
)
