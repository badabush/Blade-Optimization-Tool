# https://blog.scottlogic.com/2020/05/18/cubic-spline-in-python-and-alteryx.html

from typing import Tuple, List
import numpy as np
import bisect

def compute_changes(x: List[float]) -> List[float]:
    return [x[i+1] - x[i] for i in range(len(x) - 1)]

def create_tridiagonalmatrix(n: int, h: List[float]) -> Tuple[List[float], List[float], List[float]]:
    A = [h[i] / (h[i] + h[i + 1]) for i in range(n - 2)] + [0]
    B = [2] * n
    C = [0] + [h[i + 1] / (h[i] + h[i + 1]) for i in range(n - 2)]
    return A, B, C

def create_target(n: int, h: List[float], y: List[float]):
    return [0] + [6 * ((y[i + 1] - y[i]) / h[i] - (y[i] - y[i - 1]) / h[i - 1]) / (h[i] + h[i-1]) for i in range(1, n - 1)] + [0]

def solve_tridiagonalsystem(A: List[float], B: List[float], C: List[float], D: List[float]):
    c_p = C + [0]
    d_p = [0] * len(B)
    X = [0] * len(B)

    c_p[0] = C[0] / B[0]
    d_p[0] = D[0] / B[0]
    for i in range(1, len(B)):
        c_p[i] = c_p[i] / (B[i] - c_p[i - 1] * A[i - 1])
        d_p[i] = (D[i] - d_p[i - 1] * A[i - 1]) / (B[i] - c_p[i - 1] * A[i - 1])

    X[-1] = d_p[-1]
    for i in range(len(B) - 2, -1, -1):
        X[i] = d_p[i] - c_p[i] * X[i + 1]

    return X

def compute_spline(xpts: List[float], ypts: List[float]):
    x = .5 * (1 - np.cos(np.linspace(0, np.pi, 500)))  # x-coord generation
    n = len(xpts)
    if n < 3:
        raise ValueError('Too short an array')
    if n != len(ypts):
        raise ValueError('Array lengths are different')

    h = compute_changes(xpts)
    if any(v < 0 for v in h):
        raise ValueError('X must be strictly increasing')

    A, B, C = create_tridiagonalmatrix(n, h)
    D = create_target(n, h, ypts)

    M = solve_tridiagonalsystem(A, B, C, D)

    coefficients = [[(M[i+1]-M[i])*h[i]*h[i]/6, M[i]*h[i]*h[i]/2, (ypts[i+1] - ypts[i] - (M[i+1]+2*M[i])*h[i]*h[i]/6), ypts[i]] for i in range(n-1)]

    def spline(val):
        idx = min(bisect.bisect(xpts, val)-1, n-2)
        z = (val - xpts[idx]) / h[idx]
        C = coefficients[idx]
        return (((C[0] * z) + C[1]) * z + C[2]) * z + C[3]

    xy = np.zeros((np.size(x),2))
    xy[:, 0] = x
    xy[:, 1] = [spline(y) for y in x]

    return xy