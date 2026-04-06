from setuptools import setup, find_packages

setup(
    name="mazegen",
    version="1.0.0",
    description="A 42 project: Terminal-based maze generator and solver",
    author="dporhomo, amanukho",
    packages=find_packages(include=['mazegen', 'mazegen.*']),
    install_requires=[
        "pydantic>=2.0.0"
    ],
    entry_points={
        'console_scripts': [
            'a_maze_ing=a_maze_ing:main',
        ],
    }
)
