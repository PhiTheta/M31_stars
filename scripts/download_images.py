"""
Script to download images from IRSA corresponding to brick corners in PHAT
"""
import pandas as pd
import ztfquery
from ztfquery import query

def query_string(rcid):
    return "expid in {0} and rcid == {1}".format(tuple(x for x in grouped.get_group(rcid).expid.values), rcid)

#def download_metadata(corner_df):
#    """
#    """
#    dfs = []
#    for (ra, dec) in df[['ra', 'dec']]:
#        zquery.load_metadata(radec=[ra, dec], size=0.01)
#        dfs.append(zquery.metatable)
#    meta = pd.concat(dfs)
#    return meta.drop_duplicates(subset=['expid', 'rcid'])

df = pd.read_csv('corners.csv')
meta = download_metadata(df)
utable = meta.drop_duplicates(subset=('expid', 'rcid'))
rcids = utable.rcid.unique()
grouped = utable.groupby('rcid')
zquery = query.ZTFQuery()


for rcid in rcids:
    q = query_string(rcid)
    zquery.load_metadata(sql_query=q)
    zquery.download_data("sciimg.fits", show_progress=True)
