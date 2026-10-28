# CoBaseline Real CoStretch Historical Ingestion R1

**State:** bounded read-only ingestion of one committed historical benchmark family.  
**Source:** `benchmarks/costretch_r1/output/benchmark_evo.jsonl`

This is the first bridge from the synthetic CoBaseline frontier semantics into a real committed CoStretch result family.

The importer accepts only these three rows:

- `queue_output_serial`
- `queue_output_fixed_2`
- `queue_output_fixed_4`

It refuses normalization unless all three share:

- task count = 160;
- exact digest root;
- proof class;
- benchmark boundary;
- run timestamp;
- zero retries;
- zero failed tasks;
- full completion.

Metrics used:

- verified items / second: maximize;
- elapsed seconds: minimize;
- correctness: hard floor 1.0;
- recovery success: hard floor 1.0.

Worker width is preserved as descriptive evidence, not an optimization objective.

The expected historical result is that width 4 dominates serial and width 2 **inside this exact bounded fixture only**.

No claim is made that width 4 is universally optimal, current on X2, production-safe, sustained capacity, energy-efficient, or receiver-validated.

Rails:

`HISTORICAL_PASS_NE_CURRENT_RUNTIME`  
`WIDTH_4_WIN_NE_UNIVERSAL_OPTIMUM`  
`OFFLINE_FIXTURE_NE_X2_CALIBRATION`  
`RECORDED_THROUGHPUT_NE_SUSTAINED_CAPACITY`  
`PARETO_FRONTIER_NE_SINGLE_SCORE`
