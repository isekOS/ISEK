# Color codes for colorful logging
class Colors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    PURPLE = "\033[35m"
    ORANGE = "\033[33m"
    PINK = "\033[95m"
    # Additional colors for more variety
    LIGHT_BLUE = "\033[94m"
    LIGHT_GREEN = "\033[92m"
    LIGHT_RED = "\033[91m"
    LIGHT_YELLOW = "\033[93m"
    LIGHT_MAGENTA = "\033[95m"
    DARK_GRAY = "\033[90m"
    LIGHT_GRAY = "\033[37m"


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------
# NOTE: Keep these small utilities above the public logging helpers so they
# are available everywhere below.


def _caller_info() -> str:
    """Return the *caller* filename and line-number in unified colored format.

    We step three frames up the stack so that the reported location always
    corresponds to the original call-site and not to the internals of the
    logging helpers themselves.
    """
    import traceback
    import os

    frame = traceback.extract_stack()[-4]  # see docstring for frame math
    filename = os.path.basename(frame.filename)
    return f"{Colors.OKCYAN}{filename}:{frame.lineno}{Colors.ENDC}"


def log_a2a_protocol(
    message: str, direction: str = "→", sender: str = "", receiver: str = ""
):
    """Log A2A protocol messages with special formatting."""
    caller_info = _caller_info()

    if direction == "→":
        if sender and receiver:
            print(
                f"{Colors.LIGHT_MAGENTA}[A2A OUT]{Colors.ENDC} {caller_info} | from {Colors.LIGHT_GREEN}{sender}{Colors.ENDC} to {Colors.LIGHT_GREEN}{receiver}{Colors.ENDC} : {Colors.LIGHT_BLUE}{message}{Colors.ENDC}"
            )
        else:
            print(
                f"{Colors.LIGHT_MAGENTA}[A2A OUT]{Colors.ENDC} {caller_info} | {Colors.LIGHT_BLUE}{message}{Colors.ENDC}"
            )
    elif direction == "←":
        if sender and receiver:
            print(
                f"{Colors.LIGHT_YELLOW}[A2A IN]{Colors.ENDC} {caller_info} | from {Colors.LIGHT_GREEN}{sender}{Colors.ENDC} to {Colors.LIGHT_GREEN}{receiver}{Colors.ENDC} : {Colors.LIGHT_BLUE}{message}{Colors.ENDC}"
            )
        else:
            print(
                f"{Colors.LIGHT_YELLOW}[A2A IN]{Colors.ENDC} {caller_info} | {Colors.LIGHT_BLUE}{message}{Colors.ENDC}"
            )
    else:
        if sender and receiver:
            print(
                f"{Colors.LIGHT_MAGENTA}[A2A]{Colors.ENDC} {caller_info} | from {Colors.LIGHT_GREEN}{sender}{Colors.ENDC} to {Colors.LIGHT_GREEN}{receiver}{Colors.ENDC} : {Colors.LIGHT_BLUE}{message}{Colors.ENDC}"
            )
        else:
            print(
                f"{Colors.LIGHT_MAGENTA}[A2A]{Colors.ENDC} {caller_info} | {Colors.LIGHT_BLUE}{message}{Colors.ENDC}"
            )


def log_a2a_api_call(api_name: str, details: str = ""):
    """Log A2A API calls specifically."""
    caller_info = _caller_info()
    print(
        f"{Colors.OKCYAN}[A2A API]{Colors.ENDC} {caller_info} | {Colors.HEADER}{api_name}{Colors.ENDC} | {Colors.OKBLUE}{details}{Colors.ENDC}"
    )


def log_a2a_function_call(function_name: str, details: str = ""):
    """Log A2A function calls specifically."""
    caller_info = _caller_info()
    print(
        f"{Colors.HEADER}[A2A FUNC]{Colors.ENDC} {caller_info} | {Colors.HEADER}{function_name}{Colors.ENDC} | {Colors.OKBLUE}{details}{Colors.ENDC}"
    )


def log_error(message: str):
    """Log error message with red color."""
    caller_info = f"{Colors.LIGHT_GRAY}{_caller_info()}{Colors.ENDC}"
    print(
        f"{Colors.LIGHT_RED}[ERROR]{Colors.ENDC} {caller_info} | {Colors.LIGHT_RED}{message}{Colors.ENDC}"
    )


def log_agent_start(agent_name: str, port: int = None):
    """Log when an agent starts."""
    caller_info = _caller_info()
    port_info = f" on port {port}" if port else ""
    print(
        f"{Colors.OKGREEN}[AGENT START]{Colors.ENDC} {caller_info} | {Colors.BOLD}{agent_name}{Colors.ENDC}{port_info}"
    )


def log_agent_activity(agent_name: str, activity: str):
    """Log agent activity/status updates."""
    caller_info = _caller_info()
    print(
        f"{Colors.PURPLE}[AGENT]{Colors.ENDC} {caller_info} | {Colors.BOLD}{agent_name}{Colors.ENDC}: {Colors.OKBLUE}{activity}{Colors.ENDC}"
    )


def log_agent_request(agent_name: str, query: str, context_id: str = None):
    """Log when an agent receives a request."""
    caller_info = _caller_info()
    context_info = f" [ctx:{context_id}]" if context_id else ""
    query_preview = query[:50] + "..." if len(query) > 50 else query
    print(
        f"{Colors.LIGHT_BLUE}[AGENT REQ]{Colors.ENDC} {caller_info} | {Colors.BOLD}{agent_name}{Colors.ENDC}{context_info}: {Colors.LIGHT_GRAY}{query_preview}{Colors.ENDC}"
    )


def log_agent_response(agent_name: str, status: str, context_id: str = None):
    """Log agent response status."""
    caller_info = _caller_info()
    context_info = f" [ctx:{context_id}]" if context_id else ""
    print(
        f"{Colors.LIGHT_GREEN}[AGENT RESP]{Colors.ENDC} {caller_info} | {Colors.BOLD}{agent_name}{Colors.ENDC}{context_info}: {Colors.WARNING}{status}{Colors.ENDC}"
    )


def log_system_event(event: str, details: str = ""):
    """Log system-level events."""
    caller_info = _caller_info()
    details_info = f" | {details}" if details else ""
    print(
        f"{Colors.HEADER}[SYSTEM]{Colors.ENDC} {caller_info} | {Colors.BOLD}{event}{Colors.ENDC}{details_info}"
    )
