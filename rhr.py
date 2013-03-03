# BSD license, Andrzej Zaborowski
import math

def signbit(x):
    if x > 0:
        return 1
    if x < 0:
        return -1

def isleft(a, b, c):
    return (c[1] - b[1]) * (b[0] - a[0]) - (c[0] - b[0]) * (b[1] - a[1])

def getangle(a, b, c):
    alat = float(a[0])
    alon = float(a[1])
    blat = float(b[0])
    blon = float(b[1])
    clat = float(c[0])
    clon = float(c[1])
    ablen = math.hypot(blat - alat, blon - alon)
    bclen = math.hypot(clat - blat, clon - blon)
    # Vector cross product (?)
    cross = (blat - alat) * (clon - blon) - (blon - alon) * (clat - blat)
    # Vector dot product (?)
    dot = (blat - alat) * (clat - blat) + (blon - alon) * (clon - blon)

    try:
        sine = cross / (ablen * bclen)
        cosine = dot / (ablen * bclen)
        return math.degrees(signbit(sine) * math.acos(cosine))
    except:
        return 0.0

epsilon = 0.001

def is_rhr(poly):
    num = len(poly)
    if num < 3:
        raise Exception('2-node shape')

    angle = 0.0
    for i in range(0, num):
        a = (i + 0)
        b = (i + 1) % num
        c = (i + 2) % num
        # No projection needed
        angle += getangle(poly[a], poly[b], poly[c])
    angle = -angle

    if angle > -360.0 - epsilon and angle < -360.0 + epsilon: # CCW
        return False
    elif angle > 360.0 - epsilon and angle < 360.0 + epsilon: # CW
        return True
    else:
        raise Exception('likely an illegal shape')
