#!/usr/bin/env python3
import unittest
import screen
import os

class TestResolutions(unittest.TestCase):

    def test_ratio(self):
        # check whether a few aspect ratios are printed as expected
        self.assertEqual(str(screen.Resolution(1024, 768)), '1024x768 (4:3)')
        self.assertTrue(str(screen.Resolution(1280, 1024)) in ('1280x1024 (5:4)', '1280x1024 (4:3)'))
        self.assertEqual(str(screen.Resolution(1366, 768)), '1366x768 (16:9)')
        self.assertEqual(str(screen.Resolution(1920, 1080)), '1920x1080 (16:9)')
        self.assertEqual(str(screen.Resolution(1920, 1200)), '1920x1200 (16:10)')
        self.assertEqual(str(screen.Resolution(720, 480)), '720x480 (3:2)')

    def test_xrandr(self):
        internalConnectors = list(screen.commonInternalConnectorNames())
        for file in os.listdir('xrandr-tests'):
            print("##",file)
            with open(os.path.join('xrandr-tests', file)) as file:
                s = screen.ScreenSituation(internalConnectors, xrandrSource = file)
                del(s)

if __name__ == '__main__':
    unittest.main()
