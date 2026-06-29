VALID_STATUSES = {
    "pending",
    "running",
    "paused",
    "completed",
    "failed",
    "canceled",
}

STARTABLE_STATUSES = {"pending", "paused", "failed"}
TERMINAL_STATUSES = {"completed", "failed", "canceled"}
CONTROL_COMMANDS = {"pause", "cancel", "resume"}


def normalize_status(status: str | None) -> str:
    value = (status or "").strip().lower()
    if value not in VALID_STATUSES:
        raise ValueError(f"Unsupported task status: {status!r}")
    return value


def can_start_task(status: str | None) -> bool:
    return (status or "pending").strip().lower() in STARTABLE_STATUSES


def is_terminal_status(status: str | None) -> bool:
    return (status or "").strip().lower() in TERMINAL_STATUSES


def is_valid_control_command(command: str | None) -> bool:
    return (command or "").strip().lower() in CONTROL_COMMANDS
