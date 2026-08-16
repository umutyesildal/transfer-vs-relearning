# Study adapters

This directory is reserved for frozen study-level Slurm adapters.

The local study controller does not generate or submit arbitrary jobs from YAML. A Slurm adapter
belongs here only after its scientific recipe, resource contract, output namespace, and
authorization boundary are frozen and covered by tests.
