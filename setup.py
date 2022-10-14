import setuptools

exec(open("ticguide/version.py").read())

with open("README.md", "r", encoding="utf-8") as file:
    long_description = file.read()

setuptools.setup(
    name="ticguide",
    version=__version__,
    license="MIT",
    author="Ashley Chontos",
    author_email="ashleychontos@astro.princeton.edu",
    description="quick + painless TESS observing information",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ashleychontos/ticguide",
    project_urls={
        "Source": "https://github.com/ashleychontos/ticguide",
        "Bug Tracker": "https://github.com/ashleychontos/ticguide/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires = [
        'numpy',
        'pandas>=1.0.5',
        'tqdm',
        'bs4',
    ],
    packages=setuptools.find_packages(),
    entry_points={'console_scripts':['ticguide=ticguide.cli:main']},
    python_requires=">=3.6",
)
