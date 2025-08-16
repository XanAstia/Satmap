import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import numpy as np
import matplotlib
from cartopy.feature.nightshade import Nightshade
matplotlib.use('Qt5Agg')


class Map():
    def __init__(self, projection):
        PROJECTIONS = {
            "eqc": ccrs.PlateCarree,
            "ortho": lambda: ccrs.Orthographic(central_longitude=0, central_latitude=0),
            "moll": ccrs.Mollweide
        }
        self.proj = PROJECTIONS[projection]()


    def figure(self, time):
        # Création de la figure
        self.fig = plt.figure(figsize=(12, 7))
        self.ax = plt.axes(projection=self.proj)

        # Fond de carte
        self.ax.stock_img()
        #self.ax.background_img(resolution="full")
        # self.ax.coastlines()
        self.ax.gridlines(draw_labels=True)
        self.ax.add_feature(Nightshade(time.utc_datetime(), alpha=0.2))

        self.ax.set_title(f"Positions satellites at {time.utc_datetime().strftime('%Y-%m-%d %H:%M:%S')}")
        self.points = None
        self.labels = None
        self.traces = None


    def placeSats(self, satPos, satNames, time):
        if self.points:
            for sat in satNames:
                self.points[sat].remove()
        else:
            self.points = {}

        if self.labels:
            for sat in satNames:
                self.labels[sat].remove()
        else:
            self.labels = {}

        if self.traces:
            for sat in satNames:
                for t in self.traces[sat]:
                    t.remove()
        else:
            self.traces = {}

        self.fig.canvas.draw_idle()

        # Placement des satellites
        for pos, sat in zip(satPos, satNames):
            if np.size(pos[1]) == 1:

                self.points[sat] = self.ax.plot(pos[1], pos[0], 'ro', transform=ccrs.PlateCarree())[0]  # Points
                self.labels[sat] = self.ax.text( pos[1] + 2, pos[0] + 2, sat, color='white', transform=self.proj)
            else:

                self.points[sat] = self.ax.plot(pos[1][0], pos[0][0], 'ro', transform=ccrs.PlateCarree())[0]  # Points
                self.labels[sat] = self.ax.text(pos[1][0] + 2, pos[0][0] + 2, sat, color='white', transform=self.proj)

                self.traces[sat] = []
                diff = np.abs(np.diff(pos[1]))
                split_indices = np.where(diff > 180)[0] + 1
                start = 0
                for idx in split_indices:
                    self.traces[sat].append(
                        self.ax.plot(pos[1][start:idx], pos[0][start:idx], 'r', alpha=0.2, transform=ccrs.PlateCarree())[0])
                    start = idx
                self.traces[sat].append(
                    self.ax.plot(pos[1][start:], pos[0][start:], 'r', alpha=0.2, transform=ccrs.PlateCarree())[0])
        self.ax.set_title(f"Positions satellites at {time.utc_datetime().strftime('%Y-%m-%d %H:%M:%S')}")
        self.fig.canvas.draw_idle()


    def animationTrace(self, satPos, satNames, time):
        for pos, sat in zip(satPos, satNames):
            if not plt.fignum_exists(self.fig.number):
                exit()
            if self.points[sat]:
                self.points[sat].set_data([pos[1]], [pos[0]])  # Points
            if self.labels[sat]:
                self.labels[sat].set_position([pos[1] + 2, pos[0] + 2])

            self.ax.set_title(f"Positions satellites at {time.utc_datetime().strftime('%Y-%m-%d %H:%M:%S')}")