from setuptools import setup
import versioneer

setup(
    name='demerio',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description='demerio gui module',
    packages=['demerio_gui', 'demerio_sync', 'demerio_daemon', 'demerio_split','demerio_mapping', 'demerio_utils'],
    include_package_data=True,
    long_description=open('README.md').read().strip(),
    author='demerio',
    author_email='victor.sabatier@gmail.com',
    zip_safe=False,
    test_suite='nose.collector',
    )
