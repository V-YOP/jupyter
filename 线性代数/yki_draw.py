import numpy as np

def vec2(x, y):
    return np.array([x, y], dtype=np.float64)

def vec3(x, y, z):
    return np.array([x, y, z], dtype=np.float64)

def mat2(a, b, c, d):
    """return [ [a b] [c d] ]"""
    return np.array([[a, b], [c, d]], dtype=np.float64)

def mat3(a, b, c, d, e, f, g, h, i):
    """return [ [a b c] [d e f] [g h i] ]"""
    return np.array([[a, b, c], [d, e, f], [g, h, i]], dtype=np.float64)

def mat4(a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p):
    """return [ [a b c d] [e f g h] [i j k l] [m n o p] ]"""
    return np.array([[a, b, c, d], [e, f, g, h], [i, j, k, l], [m, n, o, p]], dtype=np.float64)
