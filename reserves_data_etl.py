"""Aave reserves data ETL"""

import os
import json
import boto3
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

from src.reserves_data.reserves_data_functions import (
    get_reserves_data_from_contract,
    transform_reserves_base_data,
    transform_reserves_configuration_data,
)

from src.utils.logger import Logger
from src.utils.data_storage import upload_current_data_to_daily_files

logger = Logger()

# ALCHEMY_URL = os.getenv("ALCHEMY_URL")
# POOL_ADDRESSES_PROVIDER_MAINNET = os.getenv("POOL_ADDRESSES_PROVIDER_MAINNET")
# AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
# AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
# AWS_SESSION_TOKEN = os.getenv("AWS_SESSION_TOKEN")

ALCHEMY_URL = os.environ["ALCHEMY_URL"]
POOL_ADDRESSES_PROVIDER_MAINNET = os.environ["POOL_ADDRESSES_PROVIDER_MAINNET"]
AWS_ACCESS_KEY = os.environ["AWS_ACCESS_KEY"]
AWS_SECRET_KEY = os.environ["AWS_SECRET_KEY"]
AWS_SESSION_TOKEN = os.environ["AWS_SESSION_TOKEN"]

client_s3 = boto3.client(
    "s3",
    endpoint_url="https://" + "minio.lab.sspcloud.fr",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    aws_session_token=AWS_SESSION_TOKEN,
)

logger.log("****Starting reserves' data ETL****")

now = datetime.now(timezone.utc)
current_timestamp = now.timestamp()

logger.log(f"Starting extraction at time {now}, timestamp = {current_timestamp}")

with open("src/abi/UiPoolDataProviderV3.json") as abi_file:
    contract_abi = json.load(abi_file)

logger.log(
    "   [STEP 1] - Extracting current reserves info from UiPoolDataProvider smart contract..."
)

_, reserves_data, _ = get_reserves_data_from_contract(
    api_url=ALCHEMY_URL,
    abi=contract_abi,
    pool_addresses_provider=POOL_ADDRESSES_PROVIDER_MAINNET,
    logger=logger,
)

logger.log("   [STEP 2] - Creating the reserves' configuration dataset...")

current_configuration_data = transform_reserves_configuration_data(
    current_timestamp=current_timestamp,
    reserves_data=reserves_data,
)

logger.log("   [STEP 3] - Creating the reserves' base dataset...")

current_base_data = transform_reserves_base_data(
    current_timestamp=current_timestamp,
    reserves_data=reserves_data,
)

logger.log("   [STEP 4] - Saving outputs to s3...")

now_date_str = now.strftime("%Y-%m-%d")

logger.log("      --> Configuration data...")

upload_current_data_to_daily_files(
    current_data=current_configuration_data,
    bucket="llatournerie",
    key=f"aaveV3-live-data/configuration/reserve_configuration_{now_date_str}.csv",
    client_s3=client_s3,
    logger=logger,
)

logger.log("      --> Base data...")

upload_current_data_to_daily_files(
    current_data=current_configuration_data,
    bucket="llatournerie",
    key=f"aaveV3-live-data/base/reserve_base_{now_date_str}.csv",
    client_s3=client_s3,
    logger=logger,
)

logger.log("      Done!")
