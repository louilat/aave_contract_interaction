"""Functions to write data to s3"""

import io
import pandas as pd
from pandas import DataFrame
from .logger import Logger


def upload_current_data_to_daily_files(
    current_data: DataFrame, bucket: str, key: str, client_s3, logger: Logger
) -> None:
    matching_files = client_s3.list_objects_v2(
        Bucket=bucket,
        Prefix=key,
    )
    CsvBuffer = io.StringIO()
    try:
        if len(matching_files["Contents"]) == 1:
            logger.log(f"      Found one existing file for: {key}")
            daily_config_data = pd.read_csv(
                client_s3.get_object(Bucket=bucket, Key=key).get("Body")
            )
            daily_config_data = pd.concat((daily_config_data, current_data))
            daily_config_data.to_csv(CsvBuffer, index=False)
            client_s3.put_object(Body=CsvBuffer.getvalue(), Bucket=bucket, Key=key)
            logger.log(f"      Updated file and uploaded it at: {key}")

        elif len(matching_files["Contents"]) == 0:
            logger.log(f"      Did not find exising file corresponding to: {key}")
            current_data.to_csv(CsvBuffer, index=False)
            client_s3.put_object(Body=CsvBuffer.getvalue(), Bucket=bucket, Key=key)
            logger.log(f"      Created a new one")

    except KeyError:
        logger.log(f"      Did not find exising file corresponding to: {key}")
        current_data.to_csv(CsvBuffer, index=False)
        client_s3.put_object(Body=CsvBuffer.getvalue(), Bucket=bucket, Key=key)
        logger.log(f"      Created a new one")
