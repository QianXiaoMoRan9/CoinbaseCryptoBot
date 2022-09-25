class BasePricing(object):
    def __init__(self):
        pass
    
    def compute_target_price_and_stop_loss(self):
        raise NotImplementedError("Error: compute_target_price_and_stop_loss is not implemented")
    
    def compute_max_position_to_take(self):
        raise NotImplementedError("Error: compute_max_position_to_take is not implemented")
