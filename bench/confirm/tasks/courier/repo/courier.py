"""The courier's parcel tracking: the scans the drivers' handsets send."""


def scans_for(scans, parcel):
    """The (parcel, status, when) scans for one parcel, oldest first."""
    found = []
    for item in scans:
        if item[0] == parcel:
            found.append(item)
    return sorted(found, key=lambda scan: scan[2])
