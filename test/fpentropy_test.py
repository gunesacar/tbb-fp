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
        self.assertEqual(("1000x600x24", 1),
                         r("1024x768x32", fp.ResizeParams()))
        self.assertEqual(("1000x1000x24", 1),
                         r("1600x1200x24",
                        fp.ResizeParams()))
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
        self.assertEqual("1000x700x24", r("1200x1600x24",
                        fp.ResizeParams(min_aspect_ratio=1.1))[0])
        self.assertEqual("1000x1400x24", r("1200x1600x24",
                        fp.ResizeParams(min_aspect_ratio=1.2,
                                        min_aspect_ratio_force_h=2000))[0])

        self.assertEqual("1000x600x24", r("1200x1600x24",
                        fp.ResizeParams(min_aspect_ratio=1.2))[0])
        self.assertEqual("1000x600x24", r("1200x1600x24",
                        fp.ResizeParams(min_aspect_ratio=1.1,
                                        h_roundto=200))[0])
        self.assertEqual("1000x400x24", r("1000x600x24",
                        fp.ResizeParams())[0])
        self.assertEqual("1000x400x24", r("1000x600x24",
                        fp.ResizeParams(toolbar_h=200))[0])

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
