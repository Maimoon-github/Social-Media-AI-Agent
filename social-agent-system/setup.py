from setuptools import setup, find_packages

setup(
    name="social-agent-system",
    version="1.0.0",
    description="Autonomous social media AI agent system",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    install_requires=[
        # Read from requirements.txt
    ],
    entry_points={
        "console_scripts": [
            "social-agent=main:main",
        ],
    },
    python_requires=">=3.11",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.11",
    ],
)