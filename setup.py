from setuptools import setup

with open("README", 'r') as f:
    long_description = f.read()
install_reqs = parse_requirements('requirements.txt', session='hack')

setup(
    name='New Albums',
    version='1.0',
    description='Creates a Spotify playlist from new albums',
    long_description=long_description,
    author='Rivers Cuomo',
    author_email='riverscuomo@users.noreply.github.com',
    url="https://riverscuomo.com/home",
    packages=['new-albums'],  #same as name
    install_requires=install_reqs, #external packages as dependencies
    scripts=[]
)
