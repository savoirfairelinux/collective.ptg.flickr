from setuptools import setup, find_packages
import os

version = "0.1"

setup(name='collective.ptg.flickr',
      version=version,
      description="Add on collective.plonetruegallery to aggregate "
                  "from flickr",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Framework :: Plone :: 3.3",
        "Framework :: Plone :: 4.0",
        "Framework :: Plone :: 4.1",
        "Framework :: Plone :: 4.2"
        ],
      keywords='gallery flickr ',
      author='Nathan Van Gheem',
      author_email='vangheem@gmail.com',
      url='http://www.plone.org/products/plone-true-gallery',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.ptg'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'flickrapi',
          'plone.app.z3cform',
          'collective.plonetruegallery'
      ],
      extras_require=dict(
          tests=[
            'flickrapi',
          ],
          flickr=['flickrapi'],
      ),
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """
)
