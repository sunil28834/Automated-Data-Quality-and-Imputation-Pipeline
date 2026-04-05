from setuptools import setup, find_packages
setup(
    name="data-quality-pipeline",
    version="1.0.0",
    packages=find_packages(),
    install_requires=open("requirements.txt").read().splitlines(),
    entry_points={"console_scripts": ["dqp=run:cli"]},
)
