def FMMSpline(x, y, yp):
    """
    PURPOSE - Compute the cubic spline with endpoint conditions chosen
    by FMM  (from the book by Forsythe,Malcolm & Moler)
    :param x:
    :param y:
    :param yp:
    :return:
    """

    n = x.size
    # x,y,yp must be at least > 3
    assert (n) > 3
    assert (y.size) > 3
    assert (yp.size) > 3

    dx = x[1:-1] - x[0:-2]
    dy = y[1:-1] - y[0:-2]
    delta = dy/dx
    dd = delta[1:-2]-delta[0:-3]
    alpha = -dx(1)
