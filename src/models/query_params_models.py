from dataclasses import dataclass

from fastapi import Query


@dataclass
class CommonQueryParams:
    records_count: int = Query(10, description='Number of records to return. Omitted if all_records == true')
    all_records: bool = Query(False, description='Return all records')
    filter_records: bool = Query(True, description='Filter records with allowed addresses and networks')


@dataclass
class DownloadQueryParams(CommonQueryParams):
    filename: str = Query('', description='Set filename to download as file', example='text.txt')
