# manage utility for maintenance purposes
import argparse
import asyncio
import logging
import sys
import uuid
from typing import Optional
from typing import Type
from typing import Union

from src.db.adapters.redis_set_db_entity_adapter import RedisSetDbEntityAdapter
from src.db.adapters.set_db_entity_str_adapter import SetDbEntityStrAdapterUUID
from src.db.storages.redis_db import context_async_redis_client
from src.service.token_db_services import AdminTokensSetDBEntityService
from src.service.token_db_services import AgentTokensSetDBEntityService


async def process_token(
    token_db_srv: Type[Union[AgentTokensSetDBEntityService, AdminTokensSetDBEntityService]],
    token: uuid.UUID,
    type_of_service: str,
):
    async with context_async_redis_client('token administration task') as redis_client:
        db_srv = token_db_srv(SetDbEntityStrAdapterUUID(RedisSetDbEntityAdapter(redis_client)))
        await db_srv.write_records([token])
        logging.info(
            'Added/Updated %s in storage, token info %s', type_of_service, str(token)[:4] + '....' + str(token)[-4:]
        )


def process_tokens(admin_token: Optional[uuid.UUID], agent_token: Optional[uuid.UUID]):
    token = agent_token if agent_token is not None else admin_token
    assert token is not None, 'Token variable must be not None'
    asyncio.run(
        process_token(
            token_db_srv=AgentTokensSetDBEntityService if agent_token else AdminTokensSetDBEntityService,
            token=token,
            type_of_service='agent token' if agent_token else 'admin_token',
        )
    )


def main(args: list[str]):
    # parse args
    parser = argparse.ArgumentParser(description='Blacklist administration utility')
    subparsers = parser.add_subparsers(
        title='administration subcommands', description='use this commands to manage application'
    )
    tokens = subparsers.add_parser(
        'tokens', description='add tokens to application storage', help='add tokens to application storage'
    )
    tokens.add_argument(
        '--admin',
        type=uuid.UUID,
        help='add administration token to application storage',
        required=False,
        metavar='[UUID value]',
    )
    tokens.add_argument(
        '--agent',
        type=uuid.UUID,
        help='add agent token to application storage',
        required=False,
        metavar='[UUID value]',
    )
    parsed_args = vars(parser.parse_args(args))
    if parsed_args:
        admin_token: Optional[uuid.UUID] = parsed_args['admin']
        agent_token: Optional[uuid.UUID] = parsed_args['agent']
        if admin_token or agent_token:
            process_tokens(admin_token, agent_token)
        else:
            parser.error('No tokens options (--admin, --agent) specified. Use at least one of them')
    else:
        parser.error('No options specified. Use --help for list of available options')


if __name__ == '__main__':
    cmd_args = sys.argv[1:]
    main(cmd_args)
