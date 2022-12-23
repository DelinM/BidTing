import dataresource as ds


def get_bidType(data):
    return ds.bid_type_Standard.get(data)


def get_category(data):
    return ds.bid_category_Standard.get(data)


def get_code_category(data):
    return ds.bid_category_numbering.get(data)
