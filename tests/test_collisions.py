''' A collection of tests for ensuring the validity of collision logic '''

import sys
import os

currentDirectory = os.path.dirname(os.path.realpath(__file__))
parentDirectory = os.path.dirname(currentDirectory)

sys.path.append(parentDirectory)

import car_details as cde

def close(a,b):
    return (a[0] - b[0])**2 + (a[1] - b[1])**2 <= 0.02

def test_line_intersection_simple():
    # sanity check
    l1 = ((0,-1), (0,1))
    l2 = ((1,0), (-1,0))

    assert(cde.doLinesIntersect(l1,l2) == [0,0])
    assert(cde.doLinesIntersect(l2,l1) == [0,0])

    assert(cde.doLinesIntersect(l1,l1) == False)
    assert(cde.doLinesIntersect(l2,l2) == False)

def test_line_intersection_endpoint():
    # testing line intersections where the intersection occurs at an endpoint
    l1 = ((0,-1), (0,1))
    l2 = ((1,0), (-1,0))
    l3 = ((0,0),(0,1))
    l4 = ((0,1),(1,1))
    l5 = ((0,1),(0,2))

    assert(cde.doLinesIntersect(l1,l3) == False)
    assert(cde.doLinesIntersect(l2,l3) == [0,0])
    assert(cde.doLinesIntersect(l1,l4) == [0,1])
    assert(cde.doLinesIntersect(l1,l5) == [0,1])

def test_line_intersection_random():
    # random lines
    l4 = ((90,85),(47,68))
    l5 = ((50,56),(72,85))
    l6 = ((28,4),(15,2))
    l7 = ((26,63),(34,32))
    l8 = ((57,66),(81,61))

    assert(close(cde.doLinesIntersect(l4,l5), [64.3,74.8]))
    assert(close(cde.doLinesIntersect(l5,l4), [64.3,74.8]))
    assert(cde.doLinesIntersect(l4,l6) == False)
    assert(cde.doLinesIntersect(l6,l4) == False)
    assert(cde.doLinesIntersect(l4,l7) == False)
    assert(cde.doLinesIntersect(l7,l4) == False)
    assert(cde.doLinesIntersect(l4,l8) == False)
    assert(cde.doLinesIntersect(l8,l4) == False)
    assert(cde.doLinesIntersect(l5,l6) == False)
    assert(cde.doLinesIntersect(l6,l5) == False)
    assert(cde.doLinesIntersect(l5,l6) == False)
    assert(cde.doLinesIntersect(l6,l5) == False)
    assert(cde.doLinesIntersect(l5,l7) == False)
    assert(cde.doLinesIntersect(l7,l5) == False)
    assert(close(cde.doLinesIntersect(l5,l8), [57.5,65.9]))
    assert(close(cde.doLinesIntersect(l8,l5), [57.5,65.9]))
    assert(cde.doLinesIntersect(l6,l7) == False)
    assert(cde.doLinesIntersect(l7,l6) == False)
    assert(cde.doLinesIntersect(l6,l8) == False)
    assert(cde.doLinesIntersect(l8,l6) == False)
    assert(cde.doLinesIntersect(l7,l8) == False)
    assert(cde.doLinesIntersect(l8,l7) == False)
