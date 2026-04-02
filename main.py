import argparse
from monopoly.pdf import PdfDocument, PdfParser
from monopoly.banks import BankDetector, banks
from monopoly.generic import GenericBank
from monopoly.pipeline import Pipeline

parser = argparse.ArgumentParser()
parser.add_argument("--file", help="bank statement in pdf")
parser.add_argument("--folder", help="folder to process the entire statements")


def main():
    args = parser.parse_args()
    print(f"got file: {args.file}")
    document = PdfDocument(file_path=args.file)
    document.unlock_document()
    detector = BankDetector(document)
    bank = detector.detect_bank(banks) or GenericBank
    pdf_parser = PdfParser(bank, document)
    pipeline = Pipeline(pdf_parser)

    statement = pipeline.extract(safety_check=False)
    transactions = pipeline.transform(statement)
    pipeline.load(
        transactions,
        statement,
        "./",
        preserve_filename=True,
    )

    transaction_as_dict = [transaction.as_raw_dict() for transaction in transactions]
    print(f"transactions: {transaction_as_dict}")


if __name__ == "__main__":
    main()
