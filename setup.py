from setuptools import setup, find_packages

setup(
    name="pdw_simulator",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
)