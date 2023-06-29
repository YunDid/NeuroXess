import os.path
import subprocess

from setuptools import setup, find_packages

# or
# from distutils.core import setup

basedir = os.path.dirname(__file__)
requirements = os.path.join(basedir, "requirements.txt")


with open(requirements, "r") as f:
    install_requires=[_.strip() for _ in f.readlines()]

# install_requires=[
#     'requests',
#     'flask>=1.0'
#     'setuptools==38.2.4',
#     'django>=1.11, !=1.11.1, <=2',
#     'requests[security, socks]>=2.18.4',
# ]

packages=find_packages(".", exclude=("tests/*"))

packages = []



version = subprocess.call("git rev-parse --short=8 HEAD")
print(version)

setup(
        name='me_worker',     # 包名字
        version=f'0.0.2-{version}',   # 包版本
        description='This is a test of the setup',   # 简单描述
        author='xl',  # 作者
        author_email='',  # 作者邮箱
        install_requires=install_requires,
        url='',      # 包的主页
        packages= find_packages() +find_packages(where="me_worker/errors"),
        # package_dir={"": "."},
)