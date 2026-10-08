"""Diagnostics module for PLB Studio."""
from story_forge.diagnostics.activity_logger import (
    log_event,
    update_component_health,
    get_diagnostic_state,
    run_self_test,
    test_copy_mechanism,
    generate_session_report
)

__all__ = [
    "log_event",
    "update_component_health",
    "get_diagnostic_state",
    "run_self_test",
    "test_copy_mechanism",
    "generate_session_report"
]
