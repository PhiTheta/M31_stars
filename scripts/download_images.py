"""
Script to download images from IRSA corresponding to brick corners in PHAT
"""
import pandas as pd
import ztfquery
from ztfquery import query

def query_string(rcid):
    return "expid in {0} and rcid = {1}".format(tuple(x for x in grouped.get_group(rcid).expid.values), rcid)

def download_metadata(corner_df):
    """
    """
    zquery = query.ZTFQuery()
    dfs = []
    for (ra, dec) in df[['ra', 'dec']].values:
        zquery.load_metadata(radec=[ra, dec], size=0.01)
        dfs.append(zquery.metatable)
    meta = pd.concat(dfs)
    return meta.drop_duplicates(subset=['expid', 'rcid'])

zquery = query.ZTFQuery()
df = pd.read_csv('corners.csv')
print("got data from corners")
meta = download_metadata(df)
utable = meta.drop_duplicates(subset=('expid', 'rcid'))
print('Obtained metadata from ZTF')
utable.to_csv('unique_table.csv', index=False)
rcids = utable.rcid.unique()
print (rcids)
grouped = utable.groupby('rcid')


for rcid in rcids:
    q = query_string(rcid)
    print(q)
    zquery.load_metadata(sql_query=q)
    try:
        zquery.download_data("sciimg.fits", show_progress=True, nprocess=4)
    except:
        print('image download with {} rcid failed'.format(rcid))
