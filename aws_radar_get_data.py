# suppress deprecation warnings
import warnings

warnings.simplefilter("ignore", category=DeprecationWarning)
from datetime import datetime, timedelta
import boto3
import botocore
from botocore.client import Config
import matplotlib.pyplot as plt
from metpy.plots import add_timestamp, ctables

def get_data(station, date, starttime, endtime):

    s3 = boto3.resource('s3', config=Config(signature_version=botocore.UNSIGNED,
                                            user_agent_extra='Resource'))
    bucket = s3.Bucket('noaa-nexrad-level2')
    file_prefix = date[4:8] + '/' + date[0:2] + '/' + date[2:4] + '/' + station + '/'
    files = []
    objs = []

    starttime = starttime + "0000"
    endtime = endtime + "5900"

    for obj in bucket.objects.filter(Prefix=file_prefix):
        files.append(obj.key)
        objs.append(obj)

    keys = [list(filter(lambda x: len(x)==6, key.split("_")))[0] for key in files if "MDM" not in key]
    vals = [i for i, key in enumerate(keys) if (int(key) >= int(starttime)) and (int(key) <= int(endtime))]
    lvl2files = [objs[val].get()['Body'] for val in vals]

    return lvl2files
