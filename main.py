import time
from utils import logger
from multiprocessing.dummy import Pool
from core import perform_wrap_unwrap_cycles
from core import get_points

def read_private_keys(file_path):
    with open(file_path, 'r') as file:
        private_keys = [line.strip() for line in file.readlines()]
    return private_keys


if __name__ == '__main__':

    private_keys = read_private_keys('private_keys.txt')

    logger.info(f'Load {len(private_keys)} wallets')
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
                executor.map(perform_wrap_unwrap_cycles, private_keys)
        case 2:
            with Pool(processes=threads) as executor:
                executor.map(get_points, private_keys)



    logger.info('Work completed successfully')
    time.sleep(1)
    input('\nPress Enter To Exit..')

