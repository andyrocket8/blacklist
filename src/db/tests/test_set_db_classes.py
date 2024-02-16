from dataclasses import dataclass
from datetime import date as dt_date
from datetime import datetime as dt_datetime
from typing import Generic
from uuid import UUID

from src.db.adapters.base_set_db_entity_adapter import BaseSetDbEntityStrAdapter
from src.models.transformation import Transformation
from src.models.uuid_transformation import UUIDStrTransformer
from src.schemas.abstract_types import K
from src.schemas.abstract_types import V

DATE_PATTERN = '%Y%m%d'


@dataclass(frozen=True)
class Car:
    brand: str
    model: str
    color: str
    date_of_registration: dt_date
    registration_no: str


@dataclass(frozen=True)
class SetTestData(Generic[K, V]):
    set_id: K
    set_data: tuple[V, ...]


class CarStrTransformation(Transformation[Car, str]):
    @classmethod
    def transform_to_storage(cls, value: Car) -> str:
        result: str = (
            f'{value.brand}:{value.model}:{value.color}:'
            f'{value.date_of_registration.strftime(DATE_PATTERN)}:{value.registration_no}'
        )
        assert len(result.split(':')) == 5, 'transform_to_storage failed, possible : in values of Car instance?'
        return result

    @classmethod
    def transform_from_storage(cls, value: str) -> Car:
        striped: list[str] = value.split(':')
        registration_date: dt_date = dt_datetime.strptime(striped[3], DATE_PATTERN).date()

        car_params: tuple[str, str, str, dt_date, str] = (
            striped[0],
            striped[1],
            striped[2],
            registration_date,
            striped[4],
        )
        return Car(*car_params)


class SetDbEntityStrCarAdapter(BaseSetDbEntityStrAdapter[UUID, Car]):
    """Entity for sets with UUID as keys and Car as values (for testing purposes)"""

    key_transformer = UUIDStrTransformer
    value_transformer = CarStrTransformation
