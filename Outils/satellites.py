from skyfield.api import load, wgs84
from skyfield.framelib import itrs
import re
import numpy as np

class Satellites():
    def __init__(self, path: str, tle_filename: str):
        self.satList, self.satNames = self.loadTLE(path, tle_filename)
        self.ts = load.timescale()
        self.currentTime = self.ts.now()
        self.times = []

    @staticmethod
    def loadTLE(path: str, filename: str):
        l = load.tle_file(path, filename=filename, reload=True)
        satNames = [s.name for s in l]
        return l, satNames


    def computeECEFPos(self, time="now"):
        if time == "now":
            time = self.ts.now()
        self.positionsECEF = np.array([s.at(time).frame_xyz(itrs).m for s in self.satList])
        self.currentTime = time


    def computeWGSPos(self, time="now"):
        if time == "now":
            time = self.ts.now()
        self.positionsWGS = np.zeros((np.size(self.satNames), 3))
        for i, s in enumerate(self.satList):
            p = wgs84.subpoint(s.at(time))
            lat, lon, elv = p.latitude, p.longitude, p.elevation
            self.positionsWGS[i] = np.array([lat.degrees, lon.degrees, elv.m])
        self.currentTime = time


    def filterSats(self, filter: list, max_sats: int):
        n = len(self.satNames)

        satNames = []
        satList = []

        for f in filter:
            print(f"Filtering satellites with {f} filter...")
            pattern = re.compile(f'{f}', re.IGNORECASE)

            satNames_temp = [sat for sat in self.satNames if pattern.search(sat)]
            satNames += satNames_temp
            satList += [sat for sat in self.satList if sat.name in satNames_temp]

        self.satNames = satNames[:max_sats]
        self.satList = satList[:max_sats]

        print(f"{len(self.satNames)}/{n} satellites found.")


    def propagateWGS(self, delta: int, n: int, reset_time: bool = False):
        self.times = []
        pos = np.zeros((np.size(self.satNames), 3, 0))
        self.currentTime = self.ts.now()
        for step in range(n):
            self.times.append(self.currentTime)
            self.computeWGSPos(self.currentTime)
            self.currentTime += ((delta/n) / 86400)
            pos = np.concatenate((pos, self.positionsWGS[:, :, np.newaxis]), axis=2)

        if reset_time:
            self.currentTime = self.times[0]

        return pos


    def propagateECEF(self, delta: int, n: int, reset_time: bool = False):
        self.times = []
        pos = np.zeros((np.size(self.satNames), 3, 0))
        self.currentTime = self.ts.now()
        for step in range(n):
            self.times.append(self.currentTime)
            self.computeECEFPos(self.currentTime)
            self.currentTime += ((delta/n) / 86400)
            pos = np.concatenate((pos, self.positionsWGS[:, :, np.newaxis]), axis=2)

        if reset_time:
            self.currentTime = self.times[0]

        return pos
