import argparse


def main() -> None:
    parser = argparse.ArgumentParser(description="AMIN Legal Model utilities")
    parser.add_argument(
        "--version",
        action="version",
        version="AMIN Legal Model 0.1.0",
    )
    parser.parse_args()
    print("AMIN Legal Model foundation is installed. No inference model is configured yet.")


if __name__ == "__main__":
    main()
