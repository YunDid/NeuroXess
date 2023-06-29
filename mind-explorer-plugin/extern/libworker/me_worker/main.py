import asyncio
import os.path
import sys
import time

import click
import loguru
from loguru import logger

from me_worker.config import settings
from me_worker.config.settings import setting

# print(sys.path)

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo('Version 1.0.0')
    ctx.exit()


@click.group()
@click.option('--version', '-v', is_flag=True, callback=print_version,
              expose_value=False, is_eager=True)
@click.option('--remove-console-log', '-rmclog', type=click.BOOL, default=False)
@click.pass_context
def cli(ctx, remove_console_log):
    logformat = "{time:YYYY-MM-DD HH:mm:ss} | {process} | {thread} | {level} | {file}:{line} - {message}"
    logpath = os.environ.setdefault("LOGURU_PATH", os.path.join(os.path.join(os.path.dirname(__file__), '..'), 'logs'))
    if setting.loguru_path:
        logpath = setting.loguru_path

    if logpath and not os.path.isdir(logpath):
        os.makedirs(logpath)

    loguru.logger.info(ctx.__dict__)

    if remove_console_log:
        logger.remove()

    logger.add(os.path.join(logpath, f'{ctx.invoked_subcommand}-err.log'), level='ERROR', format=logformat, rotation="500 MB")
    logger.add(os.path.join(logpath, f'{ctx.invoked_subcommand}-app.log'), format=logformat, rotation="500 MB", level=setting.loguru_level)


WORKER_DICT = {
}


@cli.command()
@click.argument('workername', type=click.Choice(list(WORKER_DICT.keys())))
@click.option("--restart", type=click.BOOL, default=False)
def worker(workername, restart):
    """
    start a worker
    """
    import asyncio
    # from app.worker.algo_spike_worker import AlgoSpikeWorker
    loguru.logger.info(workername)

    try:
        loop = asyncio.get_event_loop()
        worker = WORKER_DICT[workername]
        loop.run_until_complete(worker.run())
    except Exception as e:
        if restart:
            loguru.logger.exception(e)
            time.sleep(1)
            loguru.logger.warning("start now...")
            restart_program()
        else:
            raise e

def restart_program():
    python = sys.executable
    os.execl(python, python, *sys.argv)



if __name__ == '__main__':
    logger.configure(handlers=[
        dict(sink=sys.stdout,
             format="{time:YYYY-MM-DD HH:mm:ss} | {process} | {thread} | {level} | {file} {function}:{line} - {message}",
             level=setting.loguru_level
             )],
    )

    cli(obj={})

