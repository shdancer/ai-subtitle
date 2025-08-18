from setuptools import setup, find_packages


def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]


setup(
    name="ai-subtitle",
    version="0.1.3",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "ai-subtitle = ai_subtitle_assistant.__main__:main",
        ],
    },
    author="Lumos",
    author_email="lumos@lumos.fit",
    description="A set of UNIX-style tools for generating and translating subtitles using AI.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/shdancer/ai-subtitle",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    include_package_data=True,
    package_data={
        "ai_subtitle_assistant": ["../locales/*/LC_MESSAGES/*.mo"],
    },
)
