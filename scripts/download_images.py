"""
Script to download images from IRSA corresponding to brick corners in PHAT
"""
import pandas as pd
import ztfquery
from ztfquery import query

def _query_string(grouped, rcid):
    """
    Write a sql query for each rcid from the groupby object 
    """
    return "expid in {0} and rcid = {1}".format(tuple(x for x in grouped.get_group(rcid).expid.values), rcid)

def download_metadata(corner_df, metadata_file=None):
    """
    Download ZTF metadata corresponding to a set of points in a dataframe. If the metadata
    are already downloaded read from the metadata_file instead

    Parameters
    ----------
    corner_df : `pd.DataFrame`
        a pandas dataframe with columns ra, dec in degrees
    metadata_file : string
        absolute path to a csv file with the columns `expid` and `rcid`
        specifying the unique set of images to download.

    Returns
    -------
    unique_table: `pd.DataFrame`
        a dataframe of unique images with their entire metadata as downloaded using
        `ZTFQuery`.
    """
    if metadata_file is not None:
        zquery = query.ZTFQuery()
        dfs = []
        for (ra, dec) in df[['ra', 'dec']].values:
            zquery.load_metadata(radec=[ra, dec], size=0.01)
            dfs.append(zquery.metatable)
        meta = pd.concat(dfs)
    else:
        meta = pd.read_csv(metadata_file)
    # Note in many cases these duplicates might already be
    # filtered and the drop statement not needed.
    return meta.drop_duplicates(subset=['expid', 'rcid'])

if __name__ == '__main__':

    # Data Download directory
    data_download_dir = '/nfs/brahe/ZTF/ZTF_sci_images'
    # read in the corners of PHAT bricks
    df = pd.read_csv('corners.csv')
    print("got data from corners")
    # Actually read off the unique images observing these corners and build the list
    meta = download_metadata(df, metadata_file='unique_table.csv')
    utable = meta.drop_duplicates(subset=('expid', 'rcid'))
    print('Obtained metadata from ZTF')
    # record the list of unique observations
    utable.to_csv('unique_table.csv', index=False)
    # Unique combinations of ccd and channels used
    rcids = utable.rcid.unique()
    print (rcids)
    # Download images for each ccd and channel for a sequence of expids.
    grouped = utable.groupby('rcid')
    zquery = query.ZTFQuery()
    for rcid in rcids:
        q = _query_string(grouped, rcid)
        print(q)
        zquery.load_metadata(sql_query=q)
        try:
            zquery.download_data("sciimg.fits", show_progress=True, nprocess=4,
                                 download_dir=data_download_dir)
        except:
            print('image download with {} rcid failed'.format(rcid))
    print('Done')
