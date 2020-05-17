import numpy as np


def FMMSpline(x, y):
    """
    PURPOSE - Compute the cubic spline with endpoint conditions chosen
    by FMM  (from the book by Forsythe,Malcolm & Moler)
    :param x:
    :param y:
    :return:
    :param yp:
    """

    n = x.size
    # x,y must be at least > 3
    assert (n) > 3
    assert (y.size) > 3

    dx = dy = delta = np.zeros(n - 1)
    dd = np.zeros(n - 2)
    dx = x[1:] - x[0:-1]
    dy = y[1:] - y[0:-1]
    delta = dy / dx
    dd = delta[1:] - delta[0:-1]
    alpha = beta = sigma = np.zeros(n)
    alpha[0] = -dx[0]
    alpha[1:-1] = 2 * (dx[0:-1] + dx[1:])
    for i in range(1, n):
        alpha[i] = alpha[i] - dx[i - 1] * dx[i - 1] / alpha[i - 1]
    alpha[-1] = -dx[-1] - dx[-1] * dx[-1] / alpha[-2]

    beta[0] = dd[1] / (x[3] - x[2]) - dd[0] / (x[1]) - dd[0] / (x[2] - x[0])
    beta[0] = beta[0] * dx[0] * dx[0] / (x[3] - x[0])

    beta[1:-1] = dd[0:n - 2]

    beta[-1] = dd[-1] / (x[-1] - x[-3]) - dd[-1] / (x[-1] - x[-4])
    beta[-1] = -beta[-1] * dx[-1] ** 2 / (x[-1] - x[-4])

    for i in range(1, n):
        beta[i] = beta[i] - dx[i - 1] * beta[i - 1] / alpha[i - 1]

    sigma = beta / alpha
    for i in range(n - 2, 0, -1):  # reverse serial loop
        sigma[i] = (beta[i] - dx[i] * sigma[i + 1]) / alpha[i]  # back substitution

    yp = np.zeros(n)
    yp[0:-1] = delta - dx * (sigma[0:-1] * 2 + sigma[1:])
    yp[-1] = yp[-2] + dx[-1] * 3 * (sigma[-1] + sigma[-2])

    return yp

def SplineZero(x, f, fp, fbar, tol):
    """
    PURPOSE - Find a value of x corresponding to a value of fbar of the cubic
    spline defined by arrays x,f,fp. f is the value of the spline at x and fp
    is the first derivative.
    NOTES - The spline is searched for an interval that crosses the specified
    value. Then Brent's method is used for finding the zero.
    :param x:
    :param f:
    :param fp:
    :param fbar:
    :param tol:
    :return:
    """

    n = x.size
    for k in range(0, n):
        if (abs(f[k]-fbar)<tol):
            xbar = x[k]

    floc = np.zeros(n)
    floc = f-fbar

    for k in range(1,n):
        if (floc[k-1]*floc[k]<0):
            exit()
    a=x[-2]
    fa = floc[-2]
    fpa = fp[-2]