import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
        name='sf04_sensor',
        version='0.9.5',
        author='Lukas Jaworski',
        author_email='ljaworski88@gmail.com',
        description='A library used to interacted with Sensirion SF04 based sensors.',
        long_description=long_description,
        long_description_content_type='text/markdown',
        url='https://github.com/ljaworski88/sensirion-sf04-python',
        packages=setuptools.find_packages(),
        classifiers=[
            'Programming Language :: Python :: 3',
            'License :: OSI Approved :: GPLv3 License',
            'Operating System :: OS Independant',
            ],
        python_requires='>=3.6',
        )
