from pydantic import BaseModel


class RedisConfig(BaseModel):
    """Configuration for redis database"""

    redis_host: str = 'localhost'  # redis host
    redis_port: int = 6379  # redis port
    redis_db: int = 0  # redis DB number
    redis_use_authentication: bool = False  # set to True to use ACL based authentication
    redis_username: str = ''  # redis authentication username (from ACL)
    redis_password: str = ''  # redis authentication password (from ACL)

    def get_redis_uri(self):
        return f'redis://{self.redis_host}:{self.redis_port}?db={self.redis_db}'

    def get_redis_uri_for_celery(self):
        return f'redis://{self.redis_host}:{self.redis_port}/{self.redis_db}'
