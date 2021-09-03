import tempfile

# suppress deprecation warnings
import warnings

warnings.simplefilter("ignore", category=DeprecationWarning)
import nexradaws
from boto.s3.connection import S3Connection
from datetime import datetime, timedelta
from siphon.radarserver import RadarServer


def get_data(station, date, starttime, endtime):
    (lon, lat) = station[0]
    rs = RadarServer(
        "http://tds-nexrad.scigw.unidata.ucar.edu/thredds/radarServer/nexrad/level2/S3/"
    )
    query = rs.query()
    year = date[4:8]
    month = date[0:2]
    day = date[2:4]
    st = datetime(
        int(year), int(month), int(day), int(starttime), 0
    )  # Our specified time
    et = datetime(
        int(year), int(month), int(day), int(endtime), 59
    )  # Our specified time
    query.lonlat_point(lon, lat).time_range(st, et)

    cat = rs.get_catalog(query)
    return cat.datasets
