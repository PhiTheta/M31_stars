"""
Script to download ZTF Science Images from IRSA that observe locations as a sequence of ra, dec
"""
import pandas as pd
import ztfquery
from ztfquery import query
import argparse

def _query_string(grouped, rcid, download_few=False):
    """
    Write a sql query for each rcid from the groupby object 
    """
    if download_few:
        tup = tuple(x for x in grouped.get_group(rcid).expid.head(2).values)
    else:
        tup = tuple(x for x in grouped.get_group(rcid).expid.values)
    return "expid in {0} and rcid = {1}".format(tup, rcid)

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
, download_few=download_few        `ZTFQuery`.
    """
    if metadata_file is None:
        zquery = query.ZTFQuery()
        dfs = []
        for (ra, dec) in corner_df[['ra', 'dec']].values:
            zquery.load_metadata(radec=[ra, dec], size=0.01)
            dfs.append(zquery.metatable)
        meta = pd.concat(dfs)
    else:
        meta = pd.read_csv(metadata_file)
    # Note in many cases these duplicates might already be
    # filtered and the drop statement not needed.
    return meta.drop_duplicates(subset=['expid', 'rcid'])

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Download images  from ZTF that overlap the ra, dec coordinates in the input csv file')
    parser.add_argument('--data_download_dir',
                        default=None,
                        help='Absolute path to which the images will be downloaded')
    parser.add_argument('--locations_file', default=None,
                        help='a csv file with columns `ra`, `dec` with locations to be observed')
    parser.add_argument('--metadata_file',
                        default=None,
                        help='if provided, overrides the provided locations file and uses the contents as the metadata for exact data required. Note this should be a unique combination of `expid` and `rcid`, and the metadata table is useful to download using `ZTFQuery`.')
    parser.add_argument('--download_only_2', help='Download only the first couple of images', action='store_true', 
    dest='download_few')
    args = parser.parse_args()
    # Data Download directory
    data_download_dir = args.data_download_dir
    locations = args.locations_file
    download_few = args.download_few
    metadata_file = args.metadata_file

    if data_download_dir is None:
        raise ValueError('data_download_dir must be specified\n')

    # START work
    # if needed to get data from corners do so
    df = None
    print('locations is ', locations)
    if locations is not None:
        df = pd.read_csv(locations)
        print("got data from corners")
    # Actually read off the unique images observing these corners and build the list
    print('read metadata from {}'.format(metadata_file))
    meta = download_metadata(df, metadata_file=metadata_file)
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
        q = _query_string(grouped, rcid, download_few=download_few)
        print(q)
        zquery.load_metadata(sql_query=q)
        try:
            zquery.download_data("sciimg.fits", show_progress=True, nprocess=4,
                                 download_dir=data_download_dir)
        except:
            print('image download with {} rcid failed'.format(rcid))
    print('Done')
