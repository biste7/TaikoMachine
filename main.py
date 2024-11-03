import time

from config import RPC_URL
from utils import logger
from multiprocessing.dummy import Pool
from core import perform_wrap_unwrap_cycles
from core import get_points
from itertools import islice
def read_file(file_path):
    with open(file_path, 'r') as file:
        private_keys = [line.strip() for line in file.readlines()]
    return private_keys

def read_proxy(file_path, count_keys):
    with open(file_path, 'r') as file:
        private_keys = [line.strip() for line in islice(file, count_keys)]
    return private_keys

if __name__ == '__main__':

    private_keys = read_file('private_keys.txt')



    proxy = read_proxy('proxy.txt', len(private_keys))

    args = [(private_key, proxy) for private_key, proxy in zip(private_keys, proxy)]
    rpc_url = RPC_URL

    logger.info(f'Load {len(private_keys)} wallets')
    logger.info(f'Load {len(proxy)} proxy')
    time.sleep(1)

    user_action: int = int(input('\n1. WRAP UNWRAP transactions'
                                 '\n2. Get rank and score'
                                 '\n3. Soon...'
                                 '\nChoose an action: '))
    threads: int = int(input('Threads: '))
    print('')

    match user_action:
        case 1:
            with Pool(processes=threads) as executor:
                executor.starmap(perform_wrap_unwrap_cycles, [(pk, proxy, rpc_url) for pk, proxy in args])
        case 2:
            with Pool(processes=threads) as executor:
                executor.map(get_points, private_keys)



    logger.info('Work completed successfully')
    time.sleep(1)
    input('\nPress Enter To Exit..')

