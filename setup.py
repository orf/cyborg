from setuptools import setup

setup(
    name='cyborg',
    version='0.2',
    packages=['cyborg'],
    url='https://github.com/orf/cyborg',
    license='',
    author='Orf',
    author_email='tom@tomforb.es',
    description='',
    install_requires=[
        "lxml",
        "aiopipes",
        "aiohttp",
        'cssselect'
    ]
)
