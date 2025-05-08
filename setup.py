from setuptools import setup, find_packages

with open('README.md') as readme_file:
    README = readme_file.read()


setup_args = dict(
    name='BVCscrap',
    version='0.0.2',
    description='Python library to scrape financial data from Casablanca Stock Exchange(Bourse des Valeurs de Casablanca)',
    long_description_content_type="text/markdown",
    long_description=README,
    license='MIT',
    packages=find_packages(include=["BVCscrap", "BVCscrap.*"]),
    author='ANDAM Amine and edithor BOUAYAD Rayane',
    author_email='bouayadr39@gmail.com',
    keywords=["Web scrapping","financial data"],
    url='https://github.com/AmineAndam04/BVCscrap',

)

install_requires = ['requests','BeautifulSoup','pandas','json','datetime',"lxml"]

