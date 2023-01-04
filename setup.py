import io

from setuptools import setup

setup(
    author="Ben Thornton",
    author_email="Ben.Thornton955@cranfield.ac.uk",
    license="MIT",
    name="VCHKPlotter",
    python_requires='>3.5.2',
    version="0.314159",
    description="A tool to plot sections from a .vchk file and saves their contents to disk.",
    long_description=io.open("README.md", encoding="utf-8").read(),
    packages=["VCHKPlotter"],
    install_requires=[
        'termcolor<=2.0.1', 'mne<=0.23.0', 'matplotlib>=3.3.2',
        'seaborn>=0.11.0', 'numpy>=1.17.0rc1', 'pandas>=1.5.0'
    ],
    entry_points={
        'console_scripts': ["VCHKPlotter=VCHKPlotter.__main__:main"]
    },
)
