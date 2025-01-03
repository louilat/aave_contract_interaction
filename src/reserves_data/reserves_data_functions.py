"""Functions to interact with the UiPoolDataProvider contract and extract reserves data"""

from web3 import Web3
from dotenv import load_dotenv
from pandas import DataFrame
from ..utils.logger import Logger

load_dotenv()


def get_reserves_data_from_contract(
    api_url: str, abi: dict, pool_addresses_provider: str, logger: Logger
) -> tuple[list[str], list[tuple], tuple]:
    """
    Queries the UiPoolDataProvider contract to extract reserves information:
        - list of the reserves in the pool
        - for each reserve, some configuration data (flags, factors, thresholds...),
            and some current financial data (indexes, rates ...)

    More info about the UiPoolDataProvider contract at:
    https://aave.com/docs/developers/smart-contracts/view-contracts#uipooldataprovider

    Args:
        api_url (str): The endpoint of the API used to connect with the blockchain and
            interact with the UiPoolDataProvider smart contract.
        contract_address (str): The address of the UiPoolDataProvider smart contract
        abi (dict): The ABI of the UiPoolDataProvider smart contract
        pool_addresses_provider (str): The given provider for the associated pool
    Returns:
        list: The list of the initialized reserves in the pool (elements of the list are
            the addresses of the reserves' underlying assets)
        dict:
    """
    w3 = Web3(Web3.HTTPProvider(api_url))
    if w3.is_connected():
        logger.log("Successfully connected to the API")
    else:
        raise Exception("Cannot connect to the API")

    contract = w3.eth.contract(
        address="0x3F78BBD206e4D3c504Eb854232EdA7e47E9Fd8FC",
        abi=abi,
    )

    # # function getReservesList(IPoolAddressesProvider provider) public view override returns (address[] memory)
    # logger.log("   --> Extracting reserves list...")
    # reserves_list = contract.functions.getReservesList(pool_addresses_provider).call()
    # logger.log("       Done !")

    # function getReservesData(IPoolAddressesProvider provider) public view override returns (AggregatedReserveData[] memory, BaseCurrencyInfo memory)
    logger.log("   --> Extracting reserves data...")
    reserves_data, base_currency_info = contract.functions.getReservesData(
        pool_addresses_provider
    ).call()
    logger.log("       Done !")
    return reserves_data, base_currency_info


def transform_reserves_configuration_data(
    current_timestamp: float, reserves_data: list[tuple]
) -> DataFrame:
    """
    Creates a dataframe with the reserves' current configuration values (a row = a reserve). The
    configuration values are the following:
        - underlyingAsset, name, symbol, decimals, baseLTVasCollateral, reserveLiquidationThreshold,
        reserveLiquidationBonus, reserveFactor, usageAsCollateralEnabled, borrowingEnabled,
        isActive, isFrozen

    Args:
        current_timestamp (float): Query timestamp corresponding to the data stored in reserves_data
        reserves_data (list[tuple]): Second output from `get_reserves_data_from_contract()` function
    Returns:
        DataFrame: The dataset with the current configuration values for each reserve
    """
    config_columns_list = [
        "underlyingAsset",
        "name",
        "symbol",
        "decimals",
        "baseLTVasCollateral",
        "reserveLiquidationThreshold",
        "reserveLiquidationBonus",
        "reserveFactor",
        "usageAsCollateralEnabled",
        "borrowingEnabled",
        "isActive",
        "isFrozen",
    ]

    reserves_configuration_list = [data[:12] for data in reserves_data]
    reserves_configuration = DataFrame(
        reserves_configuration_list, columns=config_columns_list
    )
    reserves_configuration["query_timestamp"] = current_timestamp
    return reserves_configuration


def transform_reserves_base_data(
    current_timestamp: float, reserves_data: list[tuple]
) -> DataFrame:
    """
    Creates a dataframe with the reserves' current base data (a row = a reserve).

    Args:
        current_timestamp (float): Query timestamp corresponding to the data stored in reserves_data
        reserves_data (list[tuple]): Second output from `get_reserves_data_from_contract()` function
    Returns:
        DataFrame: The dataset with the current base values for each reserve
    """
    base_columns_list = [
        "liquidityIndex",
        "variableBorrowIndex",
        "liquidityRate",
        "variableBorrowRate",
        "lastUpdateTimestamp",
        "aTokenAddress",
        "variableDebtTokenAddress",
        "interestRateStrategyAddress",
        "availableLiquidity",
        "totalScaledVariableDebt",
        "priceInMarketReferenceCurrency",
        "priceOracle",
        "variableRateSlope1",
        "variableRateSlope2",
        "baseVariableBorrowRate",
        "optimalUsageRatio",
        "isPaused",
        "isSiloedBorrowing",
        "accruedToTreasury",
        "unbacked",
        "isolationModeTotalDebt",
        "flashLoanEnabled",
        "debtCeiling",
        "debtCeilingDecimals",
        "borrowCap",
        "supplyCap",
        "borrowableInIsolation",
        "virtualAccActive",
        "virtualUnderlyingBalance",
    ]

    reserves_base_list = [data[12:] for data in reserves_data]
    reserves_base = DataFrame(reserves_base_list, columns=base_columns_list)
    reserves_base["query_timestamp"] = current_timestamp
    return reserves_base


def transform_base_currency_info(
    current_timestamp: float, base_currency_info: tuple
) -> DataFrame:
    base_currency_columns = [
        "marketReferenceCurrencyUnit",
        "marketReferenceCurrencyPriceInUsd",
        "networkBaseTokenPriceInUsd",
        "networkBaseTokenPriceDecimals",
    ]
    base_currency = DataFrame([base_currency_info], columns=base_currency_columns)
    base_currency["query_timestamp"] = current_timestamp
    return base_currency
