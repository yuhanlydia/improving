"""Run an unchanged experiment entrypoint with a bounded CUDA allocator."""
import argparse
import runpy
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--memory-cap-mb', type=int, required=True)
    parser.add_argument('--script', required=True)
    args, remainder = parser.parse_known_args()
    if args.memory_cap_mb <= 0:
        parser.error('memory cap must be positive')
    import torch
    total = torch.cuda.get_device_properties(0).total_memory
    fraction = args.memory_cap_mb * 1024**2 / total
    if fraction > 1:
        parser.error('memory cap exceeds device memory')
    torch.cuda.set_per_process_memory_fraction(fraction, device=0)
    print(f'CUDA allocator cap: {args.memory_cap_mb} MiB', flush=True)
    sys.argv = [args.script, *remainder]
    runpy.run_path(args.script, run_name='__main__')


if __name__ == '__main__':
    main()
