from pathlib import Path
import sys

from subject_holdout_training import BASE_DIR, RELATIVE_FEATURES, parse_args, run_subject_holdout


if __name__ == "__main__":
    args = parse_args()
    output_dir = Path(args.output_dir) if "--output-dir" in sys.argv else BASE_DIR / "docs" / "subject_holdout"
    run_subject_holdout(
        model_type="rf",
        feature_set_name="relative_v2",
        feature_columns=RELATIVE_FEATURES,
        dataset_path=args.dataset,
        output_dir=output_dir,
        validation_fraction=args.test_size,
    )
