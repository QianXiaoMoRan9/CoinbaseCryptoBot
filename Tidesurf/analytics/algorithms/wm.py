from dataclasses import dataclass
import numpy as np
import json

"""
h1           /
 \    h2    /
  \  /  \  /
   l1    l2

"""


@dataclass
class W:
    h1: np.float64
    # in ms
    h1_timestamp: int
    h2: np.float64
    h2_timestamp: int
    l1: np.float64
    l1_timestamp: int
    l2: np.float64
    l2_timestamp: int

    def __hash__(self):
        return hash([
            self.h1,
            self.h1_timestamp,
            self.h2,
            self.h2_timestamp,
            self.l1,
            self.l1_timestamp,
            self.l2,
            self.l2_timestamp])

    def __repr__(self):
        return json.dumps({
            "h1": self.h1,
            "h1_timestamp": self.h1_timestamp,
            "h2": self.h2,
            "h2_timestamp": self.h2_timestamp,
            "l1": self.l1,
            "l1_timestamp": self.l1_timestamp,
            "l2": self.l2,
            "l2_timestamp": self.l2_timestamp
        })


"""
     h1      h2
    /  \    /  \
   /    \  /    \
  /      l2      \
l1                \
"""


@dataclass
class M(W):
    pass
