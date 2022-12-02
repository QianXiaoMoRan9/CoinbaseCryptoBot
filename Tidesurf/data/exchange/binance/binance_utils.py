import os


class BinanceUtils:
    @staticmethod
    def get_historic_data_folder(output_path: str, symbol: str, year: str or int, month: str or int) -> str:
        return os.path.join(output_path, output_path, symbol, str(year), str(month))

    @staticmethod
    def get_historic_data_path(output_path: str, symbol: str, year: str or int, month: str or int,
                               day: str or int) -> str:
        return os.path.join(
            BinanceUtils.get_historic_data_folder(output_path, symbol, year, month),
            f"{str(day)}.parquet")