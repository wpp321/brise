from setuptools import setup, find_packages

setup(
    name="brise",
    version="0.0.1",
    author="WangXueJie",
    author_email="hajiew@163.com",
    description="tornado module solution",
    packages=find_packages(),
    install_requires=[
        "tornado>=6.1",
        "peewee_async",
        "jsonschema",
        "aredis",
        "aiomysql",
        "peewee",
        "click",
        "gmssl"
    ],
    include_package_data=True,
    entry_points={'console_scripts': ['brise=brise.command:cli']}
)
