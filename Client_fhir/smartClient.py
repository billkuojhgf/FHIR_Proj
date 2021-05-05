import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c", "--config", help="So, what should I put in here?")
    args = parser.parse_args()
    print(args.config)
