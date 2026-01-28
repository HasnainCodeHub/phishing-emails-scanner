"""CLI entry point for the Phishing Email Scanner.

Commands:
    scan --email TEXT --sender SENDER
    scan --file PATH --sender SENDER
    train
    evaluate
"""

import argparse
import asyncio
import sys

from src.config import ScannerConfig
from src.pipeline.scanner import EmailScanner


def _format_scan_result(result) -> str:
    """Format a ScanResult for CLI output."""
    lines = [
        "=== Scan Result ===",
        "",
        result.explanation,
    ]
    if result.llm_escalated:
        lines.append("")
        lines.append("[LLM Escalation: Triggered]")
    return "\n".join(lines)


async def _cmd_scan(args, config: ScannerConfig) -> None:
    """Execute the scan command."""
    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            email_text = f.read()
    else:
        email_text = args.email

    if not email_text:
        print("Error: No email text provided. Use --email or --file.", file=sys.stderr)
        sys.exit(1)

    scanner = EmailScanner(config)
    result = await scanner.scan(email_text, args.sender)
    print(_format_scan_result(result))


def _cmd_train(args) -> None:
    """Execute the train command."""
    from src.scoring.classifier import PhishingClassifier
    from src.features.extractor import extract_features

    import json
    import os
    import zipfile

    config = ScannerConfig()
    training_path = args.data or "data/training/emails.csv"

    # Download Kaggle dataset if not already present
    if not os.path.exists(training_path) and not os.path.exists("data/training/phishing_emails.json"):
        print("Downloading Kaggle phishing email dataset...")

        try:
            from kaggle.api.kaggle_api_extended import KaggleApi

            # Initialize Kaggle API
            api = KaggleApi()
            api.authenticate()

            # Download the dataset
            dataset_name = "naserabdullahalam/phishing-email-dataset"
            api.dataset_download_files(dataset_name, path="data/training/", unzip=True)
            print(f"Downloaded dataset from Kaggle: {dataset_name}")

            # Look for the downloaded files and process them
            import glob
            downloaded_files = glob.glob("data/training/*")
            print(f"Downloaded files: {downloaded_files}")

        except Exception as e:
            print(f"Error downloading Kaggle dataset: {e}")
            print("Please ensure you have Kaggle credentials set up (kaggle.json file)")
            print("Alternatively, provide your own training data with --data flag")
            return

    # Check for JSON file first
    json_path = "data/training/phishing_emails.json"
    if os.path.exists(json_path):
        training_path = json_path

    if training_path.endswith(".json"):
        with open(training_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        X = []
        y = []
        for item in data:
            # Handle different possible JSON structures
            if isinstance(item, dict):
                email_text = item.get("email_text", item.get("text", item.get("Email Text", "")))
                label = item.get("label", item.get("Label", item.get("Phishing", "")))

                # Normalize label
                label = str(label).strip().lower()
                label_val = 1 if label in ("phishing", "1", "true", "yes", "suspicious") else 0

                if email_text:
                    features = extract_features(email_text, item.get("sender", item.get("sender", "")))
                    X.append(features)
                    y.append(label_val)
    else:
        import csv
        import sys
        # Increase field size limit to handle large fields in the dataset
        csv.field_size_limit(sys.maxsize // 100)

        X = []
        y = []

        with open(training_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            # Handle different possible CSV formats
            for row in reader:
                # Check for different possible column names
                email_text = row.get("email_text",
                                   row.get("text",
                                   row.get("Email Text",
                                   row.get("text_combined", ""))))

                # Handle different label column names and values
                label = row.get("label",
                              row.get("Label",
                              row.get("Phishing",
                              row.get("class", ""))))

                # Check if email_text is not empty/whitespace and label exists
                if email_text and str(email_text).strip() and label is not None:
                    # Normalize label
                    label = str(label).strip().lower()
                    label_val = 1 if label in ("phishing", "1", "true", "yes", "suspicious", "spam") else 0

                    # For Kaggle datasets, often there's no separate sender column
                    try:
                        features = extract_features(str(email_text).strip(), "")  # Empty sender
                        X.append(features)
                        y.append(label_val)
                    except ValueError:
                        # Skip rows that cause feature extraction errors (e.g., empty text)
                        continue

    if not X:
        print("No training data found. Please ensure the Kaggle dataset was downloaded properly.")
        print("Alternatively, provide your own training data with --data flag")
        return

    os.makedirs(os.path.dirname(config.model_path), exist_ok=True)
    PhishingClassifier.train(X, y, config.model_path, seed=config.random_seed)
    print(f"Model trained on {len(X)} samples and saved to {config.model_path}")


async def _cmd_evaluate(args, config: ScannerConfig) -> None:
    """Execute the evaluate command."""
    from src.evaluation.evaluator import evaluate, load_examples

    examples_path = args.examples or "tests/fixtures/example_emails.json"
    examples = load_examples(examples_path)
    scanner = EmailScanner(config)
    result = await evaluate(scanner, examples)

    print("=== Evaluation Results ===")
    print(f"Recall (primary):  {result.recall:.3f}")
    print(f"Precision:         {result.precision:.3f}")
    print(f"F1 Score:          {result.f1:.3f}")
    print("")
    print("Metric rationale: Recall is prioritized because missing a phishing")
    print("email (false negative) is more harmful than a false alarm.")
    print("")
    print("Per-Email Results:")
    print(f"{'ID':<20} {'Predicted':<12} {'Actual':<12} {'Score':<8} {'Correct'}")
    print("-" * 65)
    for e in result.per_email:
        marker = "YES" if e.correct else "** NO (FALSE NEGATIVE)" if e.actual == "Phishing" else "NO"
        print(f"{e.email_id:<20} {e.predicted:<12} {e.actual:<12} {e.risk_score:<8} {marker}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Explainable Phishing Email Scanner",
        prog="phishing-scanner",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Scan command
    scan_parser = subparsers.add_parser("scan", help="Scan an email for phishing")
    scan_parser.add_argument("--email", type=str, help="Email text to scan")
    scan_parser.add_argument("--file", type=str, help="Path to email file to scan")
    scan_parser.add_argument("--sender", type=str, required=True, help="Sender identifier")

    # Train command
    train_parser = subparsers.add_parser("train", help="Train the ML classifier")
    train_parser.add_argument("--data", type=str, help="Path to training data (CSV or JSON)")

    # Evaluate command
    eval_parser = subparsers.add_parser("evaluate", help="Evaluate scanner against example emails")
    eval_parser.add_argument("--examples", type=str, help="Path to example emails JSON")

    args = parser.parse_args()
    config = ScannerConfig()

    if args.command == "scan":
        asyncio.run(_cmd_scan(args, config))
    elif args.command == "train":
        _cmd_train(args)
    elif args.command == "evaluate":
        asyncio.run(_cmd_evaluate(args, config))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
