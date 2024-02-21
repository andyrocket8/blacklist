from dataclasses import dataclass
from typing import Optional

from fastapi import Query


@dataclass
class CommonQueryParams:
    records_count: int = Query(10, description='Number of records to return. Omitted if all_records == true')
    all_records: bool = Query(False, description='Return all records')
    address_group: Optional[str] = Query(None, description='Group of address, if not specified - default group')


@dataclass
class DownloadListQueryParams:
    records_count: int = Query(10, description='Number of records to return. Omitted if all_records == true')
    all_records: bool = Query(True, description='Return all records')
    filename: str = Query('', description='Set filename to download as file', example='text.txt')


@dataclass
class DownloadBlackListQueryParams(DownloadListQueryParams):
    filter_records: bool = Query(True, description='Filter records with allowed addresses and networks')
    banned_address_groups: str = Query(
        '',
        description='Select only specified banned address records. If not set merge data from all banned sets',
        openapi_examples={
            'All banned groups': {'summary': 'Retrieve all addresses from all banned address groups', 'value': ''},
            'Only default group': {
                'summary': 'Retrieve addresses only from default banned address group',
                'value': 'default',
            },
            'Some distinct groups': {
                'summary': 'Retrieve only distinct banned address groups (enumerate group names separated by comma)',
                'value': 'group_1,group_2',
            },
        },
    )
    allowed_address_groups: str = Query(
        '',
        description='Filter only with specified allowed address groups. If not set merge data from all allowed sets',
        openapi_examples={
            'All allowed groups': {'summary': 'Retrieve all addresses from all allowed address groups', 'value': ''},
            'Only default group': {
                'summary': 'Retrieve addresses only from default allowed address group',
                'value': 'default',
            },
            'Some distinct groups': {
                'summary': 'Retrieve only distinct allowed address groups (enumerate group names separated by comma)',
                'value': 'group_1,group_2',
            },
        },
    )


@dataclass
class DownloadWhitelistQueryParams(DownloadListQueryParams):
    with_networks: bool = Query(False, description='Add allowed networks in download set')
    allowed_groups: str = Query(
        '', description='Groups to download, list separated by comma. If not specified then download all groups'
    )


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


@dataclass
class CountAddress:
    address_group: Optional[str] = Query(None, description='Group of address, if not specified - default group')
