from pathlib import Path
import sys

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
    rq: str = check_rq()
    if rq.count('.') == 3 and rq.replace('.','').isdigit():
        print('Numeric')
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
