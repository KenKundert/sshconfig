from setuptools import setup
from textwrap import dedent

longDescription=dedent('''
    Generates SSH configuration file based on what network is currently being 
    used.
''')

setup(
    name='sshconfig'
  , version='1.0'
  , description='generate ssh config'
  , long_description=longDescription
  , author="Ken Kundert"
  , author_email='ken@designers-guide.com'
  , scripts=['gensshconfig']
  , py_modules=['sshconfig', 'config', 'hosts', 'core']
  , use_2to3=True
)
