from dataclasses import dataclass
import numpy as np

"""
h1           /
 \    h2    /
  \  /  \  /
   l1    l2

"""
@dataclass
class W:
    h1: np.float64
    h1_index: int
    h2: np.float64
    h2_index: int
    l1: np.float64
    l1_index: int
    l2: np.float64
    l2_index: int


"""
     h1      h2
    /  \    /  \
   /    \  /    \
  /      l2      \
l1                \
"""
@dataclass
class M:
    h1: np.float64
    h1_index: int
    h2: np.float64
    h2_index: int
    l1: np.float64
    l1_index: int
    l2: np.float64
    l2_index: int
