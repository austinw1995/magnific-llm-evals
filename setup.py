from setuptools import setup, find_packages

setup(
    name="magnific-llm-evals",
    version="0.0.2",
    packages=find_packages(),
    install_requires=[
        "openai",
        "anthropic",
        "groq",
        "cerebras_cloud_sdk",
        "google-genai",
        "pydantic",
        "asyncio",
        "typing",
        "dataclasses",
    ],
    author="Austin Wang, Prithvi Balehannina",
    author_email="austinwa@seas.upenn.edu, bprithvi@wharton.upenn.edu",
    description="A package for evaluating LLMs in customer service scenarios",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/austinw1995/magnific-llm-evals",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Testing :: Unit",
    ],
    python_requires=">=3.8",
) 