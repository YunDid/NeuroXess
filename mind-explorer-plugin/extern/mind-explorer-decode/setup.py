import os.path

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

packages=find_packages(".", exclude=("test"))

# packages = []


print(packages)


setup(
        name='decoder',     # 包名字
        version='0.0.3',   # 包版本
        description='This is a me_decoder of the setup',   # 简单描述
        author='',  # 作者
        author_email='',  # 作者邮箱
        install_requires=install_requires,
        url='',      # 包的主页
        packages= packages,
        # package_dir={"": "."},
)