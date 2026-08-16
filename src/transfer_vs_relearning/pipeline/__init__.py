"""Manifest-driven experiment planning, tracing, and artifact contracts.

The package deliberately keeps its initializer import-free: the planner reads existing training
configs, while the opt-in trainer tracing hook imports a pipeline submodule.
"""
