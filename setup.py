import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="esap-userprofile-python-client",
    version="0.0.1",
    author="Hugh Dickinson",
    author_email="hugh.dickinson@open.ac.uk",
    description="Python client for ESAP Data Discovery Shoipping Basket",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://git.astron.nl/astron-sdc/esap-userprofile-python-client",
    packages=setuptools.find_packages(),
    install_requires=["pandas", "requests", "panoptes-client"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
