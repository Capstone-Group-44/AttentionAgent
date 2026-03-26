from subject_holdout_training import (
    DEFAULT_PRODUCTION_OUTPUT_DIR,
    RELATIVE_FEATURES,
    parse_args,
    train_xgb_production_model,
)


if __name__ == "__main__":
    args = parse_args()
    train_xgb_production_model(
        feature_columns=RELATIVE_FEATURES,
        dataset_path=args.dataset,
        output_dir=DEFAULT_PRODUCTION_OUTPUT_DIR,
        model_name="xgb_relative_production",
        validation_fraction=args.test_size,
    )
