from __future__ import division
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import unittest
import fpentropy as fp
from math import e


class Test(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_filter_resolution_data(self):
        filter_res = fp.filter_resolution_data
        zero_screens = {"0x0x8": 1,
                         "0x800x8": 1,
                         "800x0x16": 1,
                         "100x100x16": 1,
                         "-100x100x16": 1,
                         }
        self.assertEqual({}, filter_res(zero_screens))
        ok_screens = {"640x480x8": 1,
                         "800x600x8": 2,
                         "1900x1200x16": 3}
        self.assertEqual(ok_screens, filter_res(ok_screens))

    def test_tor_button_resize(self):
        r = fp.tor_button_resize
        default_resize_params = fp.ResizeParams()
        self.assertEqual(r("1024x768x32", default_resize_params)[0],
                         "1000x600x24")
        self.assertEqual(r("1600x1200x24",default_resize_params)[0],
                         "1000x1000x24")
        self.assertEqual("1000x600x24", r("1280x800x16",
                        fp.ResizeParams())[0])
        self.assertEqual("800x400x24", r("800x600x24",
                        fp.ResizeParams())[0])
        self.assertEqual("1000x900x24", r("1920x1080x24",
                        fp.ResizeParams())[0])
        self.assertEqual("1000x800x24", r("1920x1080x24",
                        fp.ResizeParams(h_roundto=200))[0])
        self.assertEqual("1000x1400x24", r("1200x1600x24",
                        fp.ResizeParams())[0])
        self.assertEqual("1000x400x24", r("1000x600x24",
                        fp.ResizeParams())[0])

    def test_max_w_capping(self):
        r = fp.tor_button_resize
        resize_params = fp.ResizeParams(max_w=500)
        self.assertEqual(r("1600x1200x24", resize_params)[0],
                         "500x1000x24")

    def test_max_h_capping(self):
        r = fp.tor_button_resize
        resize_params = fp.ResizeParams(max_h=500)
        self.assertEqual(r("1600x1200x24", resize_params)[0],
                         "1000x500x24")

    def test_get_min_entropy_from_counts(self):
        td = {"1024x768x24": 10}
        self.assertEqual(0, fp.get_min_entropy_from_counts(td))
        td = {"1024x768x24": 1, "1600x900x24": 15}
        self.assertEqual(4, fp.get_min_entropy_from_counts(td))
        td = {"1024x768x24": 2, "1600x900x24": 4, "1600x1000x24": 2**21 - 6}
        self.assertEqual(20, fp.get_min_entropy_from_counts(td))
        
    
    def test_get_entropy_from_counts(self):
        td = {"1024x768x24": 10}
        self.assertEqual(0, fp.get_entropy_from_counts(td))
        td = {"1024x768x24": 1, "1600x900x24": 1}
        self.assertEqual(1, fp.get_entropy_from_counts(td))
        td = {"1024x768x24": 1, "1600x900x24": 1,
              "1600x900x8": 1, "1600x900x32": 1}
        self.assertEqual(2, fp.get_entropy_from_counts(td))

    def test_surprisal(self):
        # check the value in bits
        self.assertEqual(fp.surprisal(1), 0)
        self.assertEqual(fp.surprisal(0.5), 1)
        self.assertEqual(fp.surprisal(0.25), 2)
        self.assertEqual(fp.surprisal(0.125), 3)
        # we use assertAlmostEqual to round the values (.7f) before comparison
        # exact comparisons fail due to floating point mismatches
        self.assertAlmostEqual(fp.surprisal(0.1, 10), 1)
        self.assertAlmostEqual(fp.surprisal(0.01, 10), 2)
        self.assertEqual(fp.surprisal(1 / e, e), 1)
        self.assertAlmostEqual(fp.surprisal(1 / (e ** 25), e), 25)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
