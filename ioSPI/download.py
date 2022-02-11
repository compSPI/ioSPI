"""Module to download data from OSF.io."""


class DataDownload:
    """Class to download data from OSF.io.

    Parameters
    ----------
    token : str
        Personal token from OSF.io with access to cryoEM dataset.
    data_node_guid : str, default = "24htr"
        OSF GUID of data node that houses dataset.

    Attributes
    ----------
    headers : dict of type str:str
        Headers containing authorisation token for requests.
    base_url : str
        OSF.io API url base.
    data_node_guid : str
        OSF GUID of data node that houses dataset.

    See Also
    --------
    OSF API documentation : https://developer.osf.io/
    """

    def __init__(self):
        pass
