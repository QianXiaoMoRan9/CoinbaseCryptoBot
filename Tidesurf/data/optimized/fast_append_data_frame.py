import pandas as pd
from typing import List, Dict


class FastAppendDataFrame:
    prev_df: pd.DataFrame or None = None
    columns: List[str]
    data_dict: Dict[str, List]

    def __init__(self, columns: List[str], prev_df: pd.DataFrame or None = None):
        if prev_df is not None:
            assert columns == list(
                prev_df.columns), f"Column schema mush match prev_df. Expect: {prev_df.columns}, Got: {columns}"
            self.prev_df = prev_df
        self.columns = columns
        self.data_dict = dict()
        for column in columns:
            self.data_dict[column] = list()

    def append(self, data: List):
        assert len(data) == len(
            self.columns), f"Data provided does not align with column schema Expect: {self.columns}, Got: {data}"
        for i in range(len(self.columns)):
            self.data_dict[self.columns[i]].append(data[i])

    def get_df(self, append_new_to_bottom: bool or None = None) -> pd.DataFrame:
        res = pd.DataFrame(self.data_dict, columns=self.columns)
        if self.prev_df is not None:
            assert append_new_to_bottom is not None, "Prev_df is not None, please define how are you going to combine with previous df"
            if append_new_to_bottom:
                res = pd.concat([self.prev_df, res])
            else:
                res = pd.concat([res, self.prev_df])
        return res
