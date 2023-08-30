from setuptools import setup, find_packages


def readme():
    with open('README.md', encoding='utf-8') as f:
        content = f.read()
    return content


def version():
    from oauth2tools import __version__
    return __version__


setup(
    name="oauth2tools",
    version=version(),
    author="Bean-jun",
    author_email="1342104001@qq.com",
    description="oauth2 tools",
    long_description=readme(),
    long_description_content_type='text/markdown',
    license='MIT License',
    packages=find_packages(),
    install_requires=[
        "Flask>=2.3.2",
        "Flask-SQLAlchemy>=3.0.5",
        "requests>=2.31.0",
    ],

    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
)
