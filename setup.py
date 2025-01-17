import os
import sys
import subprocess
from os import path, makedirs
from io import open

from setuptools import setup, find_packages, Extension
from setuptools.command.build_ext import build_ext

here = path.abspath(path.dirname(__file__))


class CMakeExtension(Extension):
    def __init__(self, name):
        Extension.__init__(self, name, sources=[])


class CMakeBuild(build_ext):

    def run(self):
        for ext in self.extensions:
            self.build_cmake(ext)

    def build_cmake(self, ext):
        if not os.path.isdir(self.build_temp):
            makedirs(self.build_temp)

        extdir = self.get_ext_fullpath(ext.name)

        config = 'Debug' if self.debug else 'Release'
        cmake_args = [
            '-DPYTHON_EXECUTABLE=' + sys.executable,
            '-DCMAKE_LIBRARY_OUTPUT_DIRECTORY=' + os.path.abspath(os.path.split(extdir)[0]),
            '-DCMAKE_BUILD_TYPE=' + config,
        ]

        build_args = ['--config', config, '--', '-j2']

        env = os.environ.copy()
        subprocess.check_call(
            ['cmake', os.path.abspath(os.path.dirname(__file__))] + cmake_args,
            cwd=self.build_temp, env=env)

        if not self.dry_run:
            subprocess.check_call(
                ['cmake', '--build', '.'] + build_args,
                cwd=self.build_temp, env=env)


with open('VERSION', 'r') as fd:
    VERSION = fd.read().rstrip()

setup(
    name='qgis_headless',
    description='QGIS headless rendering library',
    version=VERSION,
    python_requires='>=3.8',
    author='NextGIS',
    author_email='info@nextgis.com',
    license='GPL',
    packages=['qgis_headless', ],
    ext_modules=[CMakeExtension('_qgis_headless')],
    cmdclass=dict(build_ext=CMakeBuild),
    zip_safe=False,
    extras_require={
        'tests': [
            'lxml',
            'pytest',
            'pytest-datadir',
            'pytest-benchmark',
            'requests',
            'pillow',
        ]
    },
    entry_points = {
        'console_scripts': [
            'qgis_headless = qgis_headless.script:main'
        ]
    }
)