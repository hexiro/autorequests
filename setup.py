from setuptools import setup, find_packages

with open("README.md", encoding="utf8") as readme_file:
    readme = readme_file.read()

with open("./autorequests/__init__.py", encoding="utf8") as __init__:
    # kinda ironic how im parsing a python file in a project that parses js
    # removes leading and trailing __s from var
    # removes escape sequences and ""s from value
    INFO = {var.strip("__"): value.strip("\"").replace("\\", "") for var, value in (
        line.split(" = ") for line in __init__.read().splitlines() if line.startswith("__"))}

setup(
    name="autorequests",
    version=INFO["version"],
    description=INFO["description"],
    long_description=readme,
    long_description_content_type="text/markdown",
    author="Hexiro",
    url="https://github.com/Hexiro/autorequests",
    packages=["autorequests"] + [("autorequests." + x) for x in find_packages(where="autorequests")],
    entry_points={
        "console_scripts": [
            "autorequests = autorequests.__main__:main"
        ]
    },
    python_requires=">=3.6",
    license="MPL2",
    classifiers=[
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python",
        "Topic :: Software Development",
    ],
    keywords=[
        "python",
        "python3",
        "node"
    ],
)
