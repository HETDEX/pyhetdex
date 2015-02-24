"""World coordinate system

"""


def deg2pix(degree, scale=1.698):
    """Convert degrees in pixels, given a pixel scale

    Parameters
    ----------
    degree : float
        angle to convert
    scale : float, optional
        pixel scale

    Returns
    -------
    float
        number of pixels
    """
    return degree * 3600. / scale

