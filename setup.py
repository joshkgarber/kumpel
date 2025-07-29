from setuptools import setup, find_packages

setup(
    name='kumpel',
    version='0.0.1',
    packages=find_packages(),
    description='A terminal-based flashcard program.',
    author='Josh Garber',
    author_email='dev@jkgarber.com',
    entry_points={
        'console_scripts': [
            'kumpel=kumpel.__main__:main'
        ]
    },
    install_requires=[
        'anthropic>=0.50.0',
        'openai>=1.77.0',
        'scipy>=1.15.2',
        'sounddevice>=0.5.1'
    ]
)

