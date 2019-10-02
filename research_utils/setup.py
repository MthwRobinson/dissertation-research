from setuptools import setup, find_packages

reqs = [
    'click',
    'daiquiri',
    'gensim',
    'lifelines',
    'matplotlib',
    'networkx',
    'nltk',
    'numpy',
    'pandas',
    'psycopg2-binary',
    'pyyaml',
    'requests',
    'seaborn',
    'uuid',
]

test_reqs = ['ipython', 'pytest', 'pytest-sugar', 'pytest-cov', 'pylint']

setup(
    name='research_utils',
    description='A utility package to support my dissertation research.',
    author='Matt Robinson',
    author_email='mrobinson23@gwu.edu',
    packages=find_packages(),
    version='0.1.0',
    install_requires=reqs,
    extras_require={
        'test': test_reqs
    },
    entry_points = {
        'console_scripts':'research_utils=research_utils.cli:main'
    }
)
