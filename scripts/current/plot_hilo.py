""" Plot the High + Low Temperatures"""

import sys
import datetime
from pyiem.plot import MapPlot
from pyiem.util import get_dbconn


def main():
    """Go Main Go"""
    now = datetime.datetime.now() - datetime.timedelta(days=int(sys.argv[1]))
    pgconn = get_dbconn('iem', user='nobody')
    icursor = pgconn.cursor()

    # Compute normal from the climate database
    sql = """
    SELECT
      s.id as station, max_tmpf, min_tmpf,
      ST_x(s.geom) as lon, ST_y(s.geom) as lat
    FROM
      summary_%s c, stations s
    WHERE
      c.iemid = s.iemid and
      s.network IN ('AWOS', 'IA_ASOS') and
      day = '%s'
      and max_tmpf > -50
    """ % (now.year, now.strftime("%Y-%m-%d"))

    data = []
    icursor.execute(sql)
    for row in icursor:
        data.append(dict(lat=row[4], lon=row[3], tmpf=row[1], dwpf=row[2],
                    id=row[0]))

    mp = MapPlot(title="Iowa High & Low Air Temperature", axisbg='white',
                 subtitle=now.strftime("%d %b %Y"))
    mp.plot_station(data)
    mp.drawcounties()
    if sys.argv[1] == "0":
        pqstr = "plot c 000000000000 summary/asos_hilo.png bogus png"
    else:
        pqstr = "plot a %s0000 bogus hilow.gif png" % (
            now.strftime("%Y%m%d"), )
    mp.postprocess(view=False, pqstr=pqstr)
    mp.close()


if __name__ == '__main__':
    main()
