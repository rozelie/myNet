import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="myNet-rozelie",
    version="0.0.1",
    author="Ryan Ozelie",
    author_email="rozelie@iwu.edu",
    description="Combine functionalities of networking probes through custom and/or existing implementations to capture and view networking information and topologies within the LAN and beyond.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rozelie/myNet/README.md",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Linux",
    ],
)