import numpy as np

from collections.abc import Hashable, Iterable, Mapping
from numpy.typing import NDArray

E = Hashable
N = Hashable

AList = Mapping[N, Mapping[N, Iterable[E]]]

YList = Mapping[E, complex]

PList = Mapping[N, float]
QList = Mapping[N, float]

AngleList = Mapping[N, float]
MagList = Mapping[N, float]

YMat = NDArray[np.complex64]
BMat = NDArray[np.float64]

PVec = NDArray[np.float64]
QVec = NDArray[np.float64]

AngleVec = NDArray[np.float64]
MagVec = NDArray[np.float64]

def make_bmat(a_list: AList, y_list: YList) -> BMat:
    pass

def p(angle_vec: AngleVec, mag_vec: MagVec, y_mat: YMat) -> PVec:
    pass

def q(angle_vec: AngleVec, mag_vec: MagVec, y_mat: YMat) -> QVec:
    pass



