from setuptools import setup

setup(
    name='django_rest_model',
    version='0.1.0',
    packages=['django_rest_model'],
    url='',
    license='MIT ',
    author='MarcoGlauser',
    author_email='',
    description='',
    setup_requires=['pytest-runner',],
    tests_require=['pytest',],
    install_requires=[
        'Django>=1.8',
        'requests>=2.12',
        'djangorestframework>=3.5'
    ],
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Development Status :: 4 - Beta',
    ]
)
