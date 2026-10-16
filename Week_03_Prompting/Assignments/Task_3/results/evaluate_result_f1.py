"""Evaluate Task 2 Text-to-SQL predictions with macro Result-Set F1."""

import csv
import json
import re
import sqlite3
from collections import Counter, defaultdict, deque
from pathlib import Path

RESULTS_DIR = Path(__file__).resolve().parent
TASK_3_DIR = RESULTS_DIR.parent
ASSIGNMENTS_DIR = TASK_3_DIR.parent

DATA_DIR = ASSIGNMENTS_DIR / "Task_2" / "data"
MODEL_ANSWERS_DIR = ASSIGNMENTS_DIR / "Task_2" / "modelAnswers"

LABELS_PATH = DATA_DIR / "restaurants_dataset.csv"
SCHEMA_PATH = DATA_DIR / "restaurants-schema.csv"
DATABASE_PATH = DATA_DIR / "restaurants-db.txt"

RESULTS_PATH = RESULTS_DIR / "task3_metric_results.csv"

PREDICTION_PATHS = {
    "APE": MODEL_ANSWERS_DIR / "Result-ape.csv",
    "RTF": MODEL_ANSWERS_DIR / "Result-rtf.csv",
    "CRISP": MODEL_ANSWERS_DIR / "Result-crisp.csv",
}
EXACT_ACCURACIES = {"APE": 0.7742, "RTF": 0.9484, "CRISP": 0.9484}


def sqlite_type(schema_type):
    normalized_type = schema_type.strip().lower()
    if normalized_type.startswith("int"):
        return "INTEGER"
    if normalized_type.startswith("decimal") or normalized_type.startswith("float"):
        return "REAL"
    return "TEXT"


def load_database():
    """Build the same in-memory SQLite database used by the Task 2 evaluator."""
    tables = {}
    with SCHEMA_PATH.open(encoding="utf-8", newline="") as schema_file:
        for table, field, primary_key, _foreign_key, column_type in csv.reader(
            schema_file, skipinitialspace=True
        ):
            table = table.strip()
            field = field.strip()
            if table == "-":
                continue
            tables.setdefault(table, []).append(
                (field, sqlite_type(column_type), primary_key.strip().lower() == "y")
            )

    connection = sqlite3.connect(":memory:")
    for table, columns in tables.items():
        definitions = []
        for field, column_type, primary_key in columns:
            definition = f'"{field}" {column_type}'
            if primary_key:
                definition += " PRIMARY KEY"
            definitions.append(definition)
        connection.execute(f'CREATE TABLE "{table}" ({", ".join(definitions)})')

    with DATABASE_PATH.open(encoding="utf-8") as database_file:
        for line_number, line in enumerate(database_file, start=1):
            match = re.fullmatch(r"([A-Z_]+)\((.*)\)", line.rstrip("\r\n"))
            if match is None:
                raise ValueError(f"Invalid database record on line {line_number}")
            table, values_text = match.groups()
            if table not in tables:
                raise ValueError(f"Unknown table {table!r} on line {line_number}")

            values = next(csv.reader([values_text], skipinitialspace=True))
            columns = tables[table]
            if len(values) != len(columns):
                raise ValueError(
                    f"Expected {len(columns)} values for {table} on line "
                    f"{line_number}, got {len(values)}"
                )

            converted_values = []
            for value, (_field, column_type, _primary_key) in zip(values, columns):
                if column_type == "INTEGER":
                    converted_values.append(int(value))
                elif column_type == "REAL":
                    converted_values.append(float(value))
                else:
                    converted_values.append(value)
            placeholders = ", ".join("?" for _ in columns)
            connection.execute(
                f'INSERT INTO "{table}" VALUES ({placeholders})', converted_values
            )
    return connection


def load_labels():
    """Load expected rows in file order, including repeated question text."""
    labels = []
    with LABELS_PATH.open(encoding="utf-8", newline="") as source:
        for line_number, row in enumerate(csv.DictReader(source), start=2):
            try:
                result = json.loads(row["result"])
            except json.JSONDecodeError as error:
                raise ValueError(
                    f"Invalid JSON label result on line {line_number} of {LABELS_PATH}"
                ) from error
            if not isinstance(result, list):
                raise ValueError(
                    f"Expected a JSON array on line {line_number} of {LABELS_PATH}"
                )
            labels.append((row["question"], result))
    return labels


def load_predictions(path):
    """Index predictions by question while retaining duplicate occurrence order."""
    predictions = defaultdict(deque)
    with path.open(encoding="utf-8", newline="") as source:
        reader = csv.DictReader(source)
        required = {"question", "predicted_sql"}
        if reader.fieldnames is None or not required.issubset(reader.fieldnames):
            raise ValueError(f"{path} must contain question and predicted_sql columns")
        for row in reader:
            predictions[row["question"]].append(row["predicted_sql"])
    return predictions


def row_multiset(rows):
    return Counter(tuple(row) for row in rows)


def result_set_f1(expected_rows, predicted_rows):
    """Return multiset row F1, including the specified empty-result behavior."""
    expected = row_multiset(expected_rows)
    predicted = row_multiset(predicted_rows)
    expected_count = sum(expected.values())
    predicted_count = sum(predicted.values())

    if expected_count == 0 and predicted_count == 0:
        return 1.0
    if expected_count == 0 or predicted_count == 0:
        return 0.0

    correct_count = sum((expected & predicted).values())
    precision = correct_count / predicted_count
    recall = correct_count / expected_count
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def evaluate_predictions(connection, labels, prediction_path):
    """Evaluate all labels; missing predictions and invalid SQL receive zero."""
    predictions = load_predictions(prediction_path)
    scores = []
    invalid_sql = 0
    missing_predictions = 0

    for question, expected_rows in labels:
        if not predictions[question]:
            scores.append(0.0)
            missing_predictions += 1
            continue
        predicted_sql = predictions[question].popleft()
        try:
            predicted_rows = connection.execute(predicted_sql).fetchall()
        except sqlite3.Error:
            scores.append(0.0)
            invalid_sql += 1
            continue
        scores.append(result_set_f1(expected_rows, predicted_rows))

    extra_predictions = sum(len(items) for items in predictions.values())
    if extra_predictions:
        raise ValueError(
            f"{prediction_path} contains {extra_predictions} unmatched predictions"
        )
    if not scores:
        raise ValueError(f"No labels found in {LABELS_PATH}")
    return sum(scores) / len(scores), len(scores), invalid_sql, missing_predictions


def write_results(results):
    with RESULTS_PATH.open("w", encoding="utf-8", newline="") as destination:
        writer = csv.writer(destination)
        writer.writerow(["framework", "exact_accuracy", "result_set_f1"])
        for framework in PREDICTION_PATHS:
            writer.writerow(
                [framework, f"{EXACT_ACCURACIES[framework]:.4f}", f"{results[framework]:.4f}"]
            )

def main():
    csv.field_size_limit(1_000_000_000)
    labels = load_labels()
    connection = load_database()
    results = {}
    try:
        for framework, prediction_path in PREDICTION_PATHS.items():
            score, count, invalid, missing = evaluate_predictions(
                connection, labels, prediction_path
            )
            results[framework] = score
            print(f"{framework}: Macro Result-Set F1 = {score:.4f}")
            print(
                f"  Evaluated questions: {count}; invalid SQL: {invalid}; "
                f"missing predictions: {missing}"
            )
    finally:
        connection.close()

    write_results(results)
    
    print(f"Results written to {RESULTS_PATH}")


if __name__ == "__main__":
    main()
