from Tidesurf.data.model.tick import Tick
import numpy as np
class BasePricing(object):
    def __init__(self, *args, **kwargs):
        pass
    
    def compute_target_price_and_stop_loss(self, cur_tick: Tick) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        raise NotImplementedError("Error: compute_target_price_and_stop_loss is not implemented")
    
    def compute_max_position_to_take(self, cur_tick: Tick) -> float:
        raise NotImplementedError("Error: compute_max_position_to_take is not implemented")
