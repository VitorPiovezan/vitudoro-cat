from setuptools import setup, find_packages

setup(
    name="vitudoro-cat",
    version="1.0.0",
    description="Pet virtual com pomodoro para Linux",
    author="Vitor Piovezan",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "vitudoro_cat": ["assets/kitten/*.png"],
    },
    entry_points={
        "console_scripts": [
            "vitudoro-cat=vitudoro_cat.main:main",
        ],
    },
    python_requires=">=3.8",
    install_requires=[
        "PyGObject>=3.36",
    ],
)
