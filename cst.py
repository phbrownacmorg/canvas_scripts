from pathlib import Path
import subprocess
import sys


def check_status() -> str:
    result = ''
    u_DEd = Path('U:/DEd')
    statusfile = u_DEd.joinpath('cst_state.txt')
    if statusfile.is_file():
        with open(statusfile) as f:
            result = f.read().strip()
    echofile = u_DEd.joinpath('cst_echo.txt')
    with open(echofile, mode='w') as f2:
        f2.write(result)

    print(result)
    return result

def check_rq() -> str:
    result = ''
    rq_src = Path.home().joinpath('Dropbox', 'DEd', 'Canvas', 'cst.txt')
    #print(rq_src)
    if rq_src.is_file():
        with open(rq_src) as f:
            result = f.read().strip()
    print(result)

    return result

def main(args: list[str]) -> int:
    status: str = check_status()
    if not status.startswith('OK'):
        rq: str = check_rq()
        if rq.count('.') == 3 and rq.replace('.','').isdigit():
            print('Numeric')
            flags = subprocess.DETACHED_PROCESS
            subprocess.Popen(['ssh', 'cst'], creationflags=flags)
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
