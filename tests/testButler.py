#!/usr/bin/env python

#
# LSST Data Management System
# Copyright 2012 LSST Corporation.
#
# This product includes software developed by the
# LSST Project (http://www.lsst.org/).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the LSST License Statement and
# the GNU General Public License along with this program.  If not,
# see <http://www.lsstcorp.org/LegalNotices/>.
#

import os
import sys

import unittest
import lsst.utils.tests as utilsTests
import lsst.daf.persistence as dafPersist
import lsst.afw.cameraGeom as cameraGeom
import lsst.afw.cameraGeom.utils as cameraGeomUtils

try:
    type(display)
except NameError:
    display = False

frame = 0

class GetRawTestCase(unittest.TestCase):
    """Testing butler raw image retrieval"""

    def setUp(self):
        datadir = self.getTestDataDir()
        if datadir:
            self.butler = dafPersist.Butler(root=os.path.join(datadir, "DATA"),
                                            calibRoot=os.path.join(datadir, "CALIB"))
            self.size = (2112, 4644)
            self.dataId = {'visit': 1038843}
            self.filter = "i2"
            self.runTests = True
        else:
            self.runTests = False

    def tearDown(self):
        if self.runTests:
            del self.butler

    def assertExposure(self, exp, ccd, checkFilter=True):
        print "dataId: ", self.dataId
        print "ccd: ", ccd
        print "width: ", exp.getWidth()
        print "height: ", exp.getHeight()
        print "detector name: ", exp.getDetector().getName()
        print "filter name: ", exp.getFilter().getFilterProperty().getName()

        self.assertEqual(exp.getWidth(), self.size[0])
        self.assertEqual(exp.getHeight(), self.size[1])
        self.assertEqual(exp.getDetector().getName(), "ccd%02d" % ccd)
        if checkFilter:
            self.assertEqual(exp.getFilter().getFilterProperty().getName(), self.filter)

        if display and ccd % 18 == 0:
            global frame
            frame += 1
            ccd = cameraGeom.cast_Ccd(exp.getDetector())
            for amp in ccd:
                amp = cameraGeom.cast_Amp(amp)
                print ccd.getId(), amp.getId(), amp.getDataSec().toString(), \
                      amp.getBiasSec().toString(), amp.getElectronicParams().getGain()
            cameraGeomUtils.showCcd(ccd, ccdImage=exp, frame=frame)

    def getTestDataDir(self):
        datadir = os.getenv("TESTDATA_CFHT_DIR")
        if datadir:
            return datadir
        else:
            print >> sys.stderr, "Skipping test as testdata_cfht is not setup"

    def testRaw(self):
        """Test retrieval of raw image"""
        if not self.runTests:
            return
        if display:
            global frame
            frame += 1
            cameraGeomUtils.showCamera(self.butler.mapper.camera, frame=frame)

        for ccd in range(36):
            raw = self.butler.get("raw", self.dataId, ccd=ccd, immediate=True)

            self.assertExposure(raw, ccd)

    def getDetrend(self, detrend):
        """Test retrieval of detrend image"""
        if not self.runTests:
            return
        for ccd in range(36):
            flat = self.butler.get(detrend, self.dataId, ccd=ccd)

            self.assertExposure(flat, ccd, checkFilter=False)

    def testFlat(self):
        if not self.runTests:
            return
        self.getDetrend("flat")

    def testBias(self):
        if not self.runTests:
            return
        self.getDetrend("bias")

    def testFringe(self):
        if not self.runTests:
            return
        self.getDetrend("fringe")

    def testPackageName(self):
        self.assertEqual(self.butler.mapper.packageName, "obs_cfht")

#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

def suite():
    """Returns a suite containing all the test cases in this module."""

    utilsTests.init()

    suites = []
    suites += unittest.makeSuite(GetRawTestCase)
    suites += unittest.makeSuite(utilsTests.MemoryTestCase)
    return unittest.TestSuite(suites)

def run(shouldExit = False):
    """Run the tests"""
    utilsTests.run(suite(), shouldExit)

if __name__ == "__main__":
    if "--display" in sys.argv:
        display = True
    run(True)
