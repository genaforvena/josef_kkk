from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="josef_kkk",
    version="0.1.0",
    author="Fake",
    author_email="",
    description="An AI-powered assistant for handling calls with German bureaucracy",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/genaforvena/josef_kkk",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.7",
    install_requires=[
        "SpeechRecognition>=3.8.1",
        "pyttsx3>=2.90",
        "anthropic>=0.3.6",
    ],
    entry_points={
        "console_scripts": [
            "josef_kkk=josef_kkk.main:main",
        ],
    },
)
