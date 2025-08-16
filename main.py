import os
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from functools import partial
import argparse
parser = argparse.ArgumentParser(description="satellites")
parser.add_argument("--tle", type=str, default="sarsat",
                    help="TLE à utiliser [iss, sarsat, all, geo, science]")
parser.add_argument("-f", "--filter", type=str, default="",
                    help="Filtre regex sur le nom des satellites.", nargs='*')
parser.add_argument("-p", "--proj", type=str, default="eqc",
                    help="Projection de la carte [eqc, ortho, moll]" )
parser.add_argument("-t", "--trace", type=str, default="true",
                    help="Affiche la trace des satellites." )
parser.add_argument("-d", "--trace-duration", type=int, default=3600,
                    help="Durée de la trace.")
parser.add_argument("-m", "--max", type=int, default=100,
                    help="Maximum de satellites à afficher.")

from Outils.satellites import Satellites
from Outils.map import Map

tle_link = {"iss" : "https://celestrak.org/NORAD/elements/gp.php?GROUP=stations&FORMAT=tle",
            "sarsat": "https://celestrak.org/NORAD/elements/gp.php?GROUP=sarsat&FORMAT=tle",
            "all": "https://celestrak.org/NORAD/elements/gp.php?GROUP=active&FORMAT=tle",
            "geo": "https://celestrak.org/NORAD/elements/gp.php?GROUP=geo&FORMAT=tle",
            "science": "https://celestrak.org/NORAD/elements/gp.php?GROUP=science&FORMAT=tle"}

def Propag(frame, Sats, m, trace, duree):
    if (frame % 999 == 0) and (trace):
        traces = Sats.propagateWGS(delta=duree, n=360, reset_time=True)
        m.placeSats(satPos=traces, satNames=Sats.satNames, time=Sats.currentTime)
    Sats.computeWGSPos()
    m.animationTrace(satPos=Sats.positionsWGS, satNames=Sats.satNames, time=Sats.currentTime)
    return []


def main():
    args = parser.parse_args()

    trace = args.trace.lower()
    duree = args.trace_duration
    filter = args.filter
    proj = args.proj
    tle = args.tle
    max_sats = args.max

    if trace == "true":
        trace = True
    elif trace == "false":
        trace = False


    if not os.path.exists(f"gp_{tle}.php"):
        Sats = Satellites(tle_link[tle], f"gp_{tle}.php")
    else:
        Sats = Satellites(f"gp_{tle}.php", f"gp_{tle}.php")

    Sats.filterSats(filter, max_sats)

    Sats.computeWGSPos("now")

    m = Map(proj)
    m.figure(time=Sats.currentTime)
    m.placeSats(satPos=Sats.positionsWGS, satNames=Sats.satNames, time=Sats.currentTime)

    ani = FuncAnimation(m.fig, partial(Propag, Sats=Sats, m=m, trace=trace, duree=duree),
                        frames=range(1000), interval=1000, blit=True)
    plt.show()


if __name__ == '__main__':
    main()
