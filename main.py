import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--file", help="bank statement in pdf")
parser.add_argument("--folder", help="folder to process the entire statements")


def main():
    args = parser.parse_args()
    print(f"got file: {args.file}")


if __name__ == "__main__":
    main()
