import pyarrow as pa
import pyarrow.parquet as pq
import pandas as pd


class BaseFetcher(object):

    @staticmethod
    def save_df_to_parquet(df: pd.DataFrame, output_file: str):
        table = pa.Table.from_pandas(df=df)
        pq.write_table(table, output_file)

    @staticmethod
    def load_df_from_parquet(file_path: str) -> pd.DataFrame:
        return pd.read_parquet(file_path, engine='pyarrow')
