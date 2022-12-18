import dataresource as ds


def get_bidType(data):
    return ds.bid_type_Standard.get(data)
