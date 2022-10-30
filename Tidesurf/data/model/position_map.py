from typing import Dict, List
from Tidesurf.data.model.position import Position

class PositionMap(object):
    # symbol -> Position
    position_dict: Dict[str, List[Position]]

    def __init__(self):
        self.position_dict = dict()

    def add_position(self, position: Position):
        if position.symbol in self.position_dict:
            self.position_dict[position.symbol].append(position)
            return
        self.position_dict[position.symbol] = [position]

    def remove_position(self, position: Position):
        self.position_dict[position.symbol].remove(position)

    def get_product_positions(self, symbol) -> List[Position]:
        if symbol not in self.position_dict:
            return []
        return self.position_dict[symbol]

    @staticmethod
    def from_position_list(position_list: List[Position]) -> 'PositionMap':
        res = PositionMap()
        for position in position_list:
            res.add_position(position)
        return res

    def to_position_list(self) -> List[Position]:
        res = []
        for position_list in self.position_dict.values():
            res.extend(position_list)
        return res
