from subject_holdout_training import ABSOLUTE_FEATURES, parse_args, run_subject_holdout


if __name__ == "__main__":
    args = parse_args()
    run_subject_holdout(
        model_type="rf",
        feature_set_name="absolute",
        feature_columns=ABSOLUTE_FEATURES,
        dataset_path=args.dataset,
        output_dir=args.output_dir,
        validation_fraction=args.test_size,
    )
