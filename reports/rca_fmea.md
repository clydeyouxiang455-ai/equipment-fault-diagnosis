# RCA and Preliminary FMEA

This is an investigation aid. Severity=7 and Detection=5 are illustrative engineering judgments; Occurrence=2 or 3 is assigned only from synthetic-data indicator frequency. RPN=S x O x D is illustrative only, not a measured plant risk score or action priority.

## 5 Why prompt

1. Why was a failure label observed? It may reflect a documented synthetic-data rule or random flag; first reconcile the target with the indicator columns because the official CSV contains mismatches.
2. Why was that operating condition present? Examine operating state, load, tool condition and configuration.
3. Why might that condition persist? Inspect control logic, setup, thermal path, wear-management and measurement quality.
4. Why was it not detected earlier? Review monitoring coverage, calibration status and inspection triggers.
5. What is the verified root cause? Do not answer until physical inspection and a controlled validation provide evidence.

## Fishbone / Ishikawa prompt

Investigate **Machine** (mechanisms/interfaces), **Method** (setup/control logic), **Measurement** (calibration/sampling), **Material or Tooling** (wear/load), **Environment** (thermal conditions), and **People/Management** (maintenance/standard work). These are hypothesis categories, not dataset-derived causes.

| failure_indicator | flagged_records | flag_rate | cooccurring_machine_failures | indicator_without_machine_failure | target_alignment_rate | records_with_multiple_mode_flags | potential_effect | possible_cause | existing_evidence | alternative_explanations | additional_measurements | recommended_verification | severity | occurrence | detection | rpn |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| HDF | 115 | 0.0115 | 115 | 0 | 1.0000 | 24 | Unexpected equipment fault indication; impact requires asset context | Dataset flag tied to low temperature difference and lower rotational speed | Observed synthetic-dataset flag frequency | Sensor error, configuration differences, or unmeasured maintenance/operating context | Calibration status, configuration ID, maintenance history, subsystem inspection results | Review temperature sensors, thermal path and operating state; test a controlled operating envelope | 7 | 3 | 5 | 105 |
| OSF | 98 | 0.0098 | 98 | 0 | 1.0000 | 24 | Unexpected equipment fault indication; impact requires asset context | Dataset flag tied to tool-wear and torque product with Type-specific thresholds | Observed synthetic-dataset flag frequency | Sensor error, configuration differences, or unmeasured maintenance/operating context | Calibration status, configuration ID, maintenance history, subsystem inspection results | Inspect tool condition/load path; verify torque calibration and configuration threshold | 7 | 2 | 5 | 70 |
| PWF | 95 | 0.0095 | 95 | 0 | 1.0000 | 24 | Unexpected equipment fault indication; impact requires asset context | Dataset flag tied to calculated rotational power outside documented bounds | Observed synthetic-dataset flag frequency | Sensor error, configuration differences, or unmeasured maintenance/operating context | Calibration status, configuration ID, maintenance history, subsystem inspection results | Verify speed/torque instrumentation and load condition; repeat under controlled load | 7 | 2 | 5 | 70 |
| TWF | 46 | 0.0046 | 46 | 0 | 1.0000 | 24 | Unexpected equipment fault indication; impact requires asset context | Dataset-generated tool-wear failure flag | Observed synthetic-dataset flag frequency | Sensor error, configuration differences, or unmeasured maintenance/operating context | Calibration status, configuration ID, maintenance history, subsystem inspection results | Inspect tool wear measurement and replacement criteria; compare with controlled wear samples | 7 | 2 | 5 | 70 |