import os

def get_monthly_partition_file_name(base_directory: str, product_id: str, year, month) -> str:
    return os.path.join(base_directory, product_id, f'{product_id}_{year}_{month}.parquet')
