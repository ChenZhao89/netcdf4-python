import unittest
import os
import tempfile

import numpy as np
from numpy import ma
from numpy.testing import assert_array_almost_equal
from netCDF4 import Dataset

# Test automatic conversion of masked arrays (set_auto_array_type())

class SetAutoArrayTypeTestBase(unittest.TestCase):

    """Base object for tests checking the functionality of set_auto_array_type()"""

    def setUp(self):

        self.testfile = tempfile.NamedTemporaryFile(suffix='.nc', delete=False).name

        self.v = np.array([4, 3, 2, 1], dtype="i2")
        self.w = np.ma.array([-1, -2, -3, -4], mask=[False, True, False, False], dtype="i2")
                  
        f = Dataset(self.testfile, 'w')
        _ = f.createDimension('x', None)
        v = f.createVariable('v', "i2", 'x')
        w = f.createVariable('w', "i2", 'x')

        v[...] = self.v
        w[...] = self.w

        f.close()
        
    def tearDown(self):

        os.remove(self.testfile)


class SetAutoArrayTypeFalse(SetAutoArrayTypeTestBase):

    def test_auto_array_type(self):
        
        """Testing auto-conversion of masked arrays with no missing values to regular arrays."""
        f = Dataset(self.testfile)

        f.variables["v"].set_auto_array_type(False) # The default anyway...

        v = f.variables['v'][:]

        self.assertTrue(isinstance(v, np.ndarray))
        self.assertTrue(isinstance(v, ma.core.MaskedArray))
        assert_array_almost_equal(v, self.v)

        w = f.variables['w'][:]

        self.assertTrue(isinstance(w, np.ndarray))
        self.assertTrue(isinstance(w, ma.core.MaskedArray))
        assert_array_almost_equal(w, self.w)
        
        f.close()

class SetAutoArrayTypeTrue(SetAutoArrayTypeTestBase):

    def test_auto_array_type(self):
        
        """Testing auto-conversion of masked arrays with no missing values to regular arrays."""
        f = Dataset(self.testfile)

        f.variables["v"].set_auto_array_type(True)
        v = f.variables['v'][:]

        self.assertTrue(isinstance(v, np.ndarray))
        self.assertFalse(isinstance(v, ma.core.MaskedArray))
        assert_array_almost_equal(v, self.v)

        w = f.variables['w'][:]

        self.assertTrue(isinstance(w, np.ndarray))
        self.assertTrue(isinstance(w, ma.core.MaskedArray))
        assert_array_almost_equal(w, self.w)

        f.close()

class GlobalSetAutoArrayTypeTest(unittest.TestCase):

    def setUp(self):

        self.testfile = tempfile.NamedTemporaryFile(suffix='.nc', delete=False).name

        f = Dataset(self.testfile, 'w')

        grp1 = f.createGroup('Group1')
        grp2 = f.createGroup('Group2')
        f.createGroup('Group3')         # empty group

        f.createVariable('var0', "i2", ())
        grp1.createVariable('var1', 'f8', ())
        grp2.createVariable('var2', 'f4', ())

        f.close()

    def tearDown(self):

        os.remove(self.testfile)

    def runTest(self):

        # Note: The default behaviour is to always return masked
        #       arrays, which is already tested elsewhere.

        f = Dataset(self.testfile, "r")

        # Without auto array typing

        f.set_auto_array_type(False)

        v0 = f.variables['var0']
        v1 = f.groups['Group1'].variables['var1']
        v2 = f.groups['Group2'].variables['var2']

        self.assertFalse(v0.array_type)
        self.assertFalse(v1.array_type)
        self.assertFalse(v2.array_type)

        # With auto array typing

        f.set_auto_array_type(True)

        self.assertTrue(v0.array_type)
        self.assertTrue(v1.array_type)
        self.assertTrue(v2.array_type)

        f.close()


if __name__ == '__main__':
    unittest.main()
