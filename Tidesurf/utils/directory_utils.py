import os

def get_monthly_partition_file_name(base_directory: str, symbol: str, year, month) -> str:
    return os.path.join(base_directory, symbol, f'{symbol}_{year}_{month}.parquet')
