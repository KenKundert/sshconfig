from setuptools import setup

with open('README.rst') as f:
    readme = f.read()

setup(
    name='sshconfig'
  , version='1.0.0'
  , description='generate ssh config file'
  , author="Ken Kundert"
  , author_email='ken@designers-guide.com'
  , url='http://nurdletech.com/linux-utilities/sshconfig'
  , download_url='https://github.com/kenkundert/sshconfig/tarball/master'
  , scripts=['gensshconfig']
  , py_modules=['sshconfig', 'config', 'hosts', 'core']
  , license='GPLv3+'
  , install_requires=['docopt']
  , platforms=['linux']
  , classifiers=[
        'Development Status :: 3 - Alpha'
      , 'Environment :: Console'
      , 'Intended Audience :: End Users/Desktop'
      , 'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)'
      , 'Natural Language :: English'
      , 'Operating System :: POSIX :: Linux'
      , 'Programming Language :: Python :: 3.5'
      , 'Programming Language :: Python :: 3.4'
      , 'Programming Language :: Python :: 3.3'
      , 'Programming Language :: Python :: 2.7'
      , 'Topic :: Utilities'
    ],
)
