from setuptools import setup, find_packages

setup(
    name='nginx-generator',
    version='0.1.1',
    description='Generate nginx configs interactivly',
    url='http://github.com/Oliwerix/nginx-generator',
    author='Oliver Wagner',
    author_email='oliwerix@oliwerix.com',
    license='AGPLv3.0',
    include_package_data=True,
    package_data={'nginx-generator':['snippets/*']},
    install_requires=['validators','click'],
    packages=find_packages(),
    entry_points=dict(
        console_scripts=['nginx-generator=nginx_generator.app:main']
    )
)

