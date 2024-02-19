from dataclasses import dataclass

from fastapi import Query


@dataclass
class CommonQueryParams:
    records_count: int = Query(10, description='Number of records to return. Omitted if all_records == true')
    all_records: bool = Query(False, description='Return all records')


@dataclass
class DownloadBlackListQueryParams(CommonQueryParams):
    filter_records: bool = Query(True, description='Filter records with allowed addresses and networks')
    filename: str = Query('', description='Set filename to download as file', example='text.txt')


@dataclass
class DownloadWhitelistQueryParams:
    records_count: int = Query(10, description='Number of records to return. Omitted if all_records == true')
    all_records: bool = Query(False, description='Return all records')
    with_networks: bool = Query(True, description='Add allowed networks in donwload set')
    filename: str = Query('', description='Set filename to download as file', example='text.txt')


@dataclass
class HistoryQueryParams:
    time_offset: str = Query(
        '24h',
        description=(
            'Show addresses modified in specified last period. '
            'You can specify time units by suffix: '
            'use '
            's - for seconds, '
            'm - for minutes, '
            'h - for hours, '
            'h - for days'
        ),
        example='60m',
    )
    all_records: bool = Query(False, description='Return all records, omit "time_offset" parameter')
