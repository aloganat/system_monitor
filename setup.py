from setuptools import setup

setup(name='system_monitor',
      version='0.1',
      author='Arthy Loganathan',
      author_email='aloganat@gmail.com',
      description=('Tool for monitoring system and draws chart with system monitor data'),
      url='https://github.com/aloganat/system_monitor',
      classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Quality Assurance',
        ],
      packages=['system_monitor'],
      entry_points={
        'console_scripts': [
            'system_monitor = system_monitor.system_monitor:main',
            ]
                    },
      install_requires=['pip', 'xlrd', 'xlwt', 'xlutils']
)
