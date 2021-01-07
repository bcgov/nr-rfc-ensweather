import sys

base = '/'.join(__file__.split('/')[:-2])
if base not in sys.path:
    sys.path.append(base)
if not base:
    base = './'


def main():
    pass


if __name__ == '__main__':
    main()
