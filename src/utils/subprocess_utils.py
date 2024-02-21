import logging
import subprocess
from platform import system
from shlex import split as shlex_split


def execute_command(command: str) -> tuple[int, list[str]]:
    """Execute OS command.
    :param str command: command to execute
    :rtype bool
    :returns True if error occurred
    """
    output = []
    result = subprocess.run(shlex_split(command), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if result.returncode != 0:
        decoded_output = result.stdout.decode('cp866' if system() == 'Windows' else 'utf8')
        output = decoded_output.splitlines()
    return result.returncode, output


def logging_sp_exec_error(command: str, return_code: int, output: list[str]):
    """Logging info for 'execute_command' error result"""
    logging.error(f'Error while executing command {command!r}, return code: {return_code}, details:')
    for record in output:
        logging.error('   ' + record)
