import uvicorn
import socket

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCard


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


def create_agent_a2a_server(
    agent_executor, agent_card: AgentCard
) -> A2AStarletteApplication:
    request_handler = DefaultRequestHandler(
        agent_executor=agent_executor, task_store=InMemoryTaskStore()
    )

    app = A2AStarletteApplication(agent_card=agent_card, http_handler=request_handler)
    return app


async def run_server(create_agent_function, port: int, name: str):
    try:
        app = create_agent_function()

        config = uvicorn.Config(
            app.build(), host="127.0.0.1", port=port, log_level="error", loop="asyncio"
        )

        server = uvicorn.Server(config)

        log_a2a_api_call(
            "server.serve()", f"server: {name}, port: {port}, host: 127.0.0.1"
        )
        await server.serve()
    except Exception as e:
        log_error(f"run_server() error: {e} - name: {name}, port: {port}")


def is_port_in_use(port: int, host: str = "127.0.0.1") -> bool:
    """Return True if a TCP port is already bound on the given host."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.2)
            return sock.connect_ex((host, port)) == 0
    except Exception:
        return False


def log_a2a_protocol(
    message: str, direction: str = "→", sender: str = "", receiver: str = ""
):
    """Log A2A protocol messages with special formatting."""
    import traceback

    caller = traceback.extract_stack()[-2]
    caller_info = (
        f"{Colors.OKCYAN}{caller.filename.split('/')[-1]}:{caller.lineno}{Colors.ENDC}"
    )

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
    import traceback

    caller = traceback.extract_stack()[-2]
    caller_info = (
        f"{Colors.OKCYAN}{caller.filename.split('/')[-1]}:{caller.lineno}{Colors.ENDC}"
    )
    print(
        f"{Colors.OKCYAN}[A2A API]{Colors.ENDC} {caller_info} | {Colors.HEADER}{api_name}{Colors.ENDC} | {Colors.OKBLUE}{details}{Colors.ENDC}"
    )


def log_a2a_function_call(function_name: str, details: str = ""):
    """Log A2A function calls specifically."""
    import traceback

    caller = traceback.extract_stack()[-2]
    caller_info = (
        f"{Colors.OKCYAN}{caller.filename.split('/')[-1]}:{caller.lineno}{Colors.ENDC}"
    )
    print(
        f"{Colors.HEADER}[A2A FUNC]{Colors.ENDC} {caller_info} | {Colors.HEADER}{function_name}{Colors.ENDC} | {Colors.OKBLUE}{details}{Colors.ENDC}"
    )


def log_error(message: str):
    """Log error message with red color."""
    import traceback

    caller = traceback.extract_stack()[-2]
    caller_info = f"{Colors.LIGHT_GRAY}{caller.filename.split('/')[-1]}:{caller.lineno}{Colors.ENDC}"
    print(
        f"{Colors.LIGHT_RED}[ERROR]{Colors.ENDC} {caller_info} | {Colors.LIGHT_RED}{message}{Colors.ENDC}"
    )


def log_agent_start(agent_name: str, port: int = None):
    """Log when an agent starts."""
    import traceback

    caller = traceback.extract_stack()[-2]
    caller_info = (
        f"{Colors.OKCYAN}{caller.filename.split('/')[-1]}:{caller.lineno}{Colors.ENDC}"
    )
    port_info = f" on port {port}" if port else ""
    print(
        f"{Colors.OKGREEN}[AGENT START]{Colors.ENDC} {caller_info} | {Colors.BOLD}{agent_name}{Colors.ENDC}{port_info}"
    )


def log_agent_activity(agent_name: str, activity: str):
    """Log agent activity/status updates."""
    import traceback

    caller = traceback.extract_stack()[-2]
    caller_info = (
        f"{Colors.OKCYAN}{caller.filename.split('/')[-1]}:{caller.lineno}{Colors.ENDC}"
    )
    print(
        f"{Colors.PURPLE}[AGENT]{Colors.ENDC} {caller_info} | {Colors.BOLD}{agent_name}{Colors.ENDC}: {Colors.OKBLUE}{activity}{Colors.ENDC}"
    )


def log_agent_request(agent_name: str, query: str, context_id: str = None):
    """Log when an agent receives a request."""
    import traceback

    caller = traceback.extract_stack()[-2]
    caller_info = (
        f"{Colors.OKCYAN}{caller.filename.split('/')[-1]}:{caller.lineno}{Colors.ENDC}"
    )
    context_info = f" [ctx:{context_id}]" if context_id else ""
    query_preview = query[:50] + "..." if len(query) > 50 else query
    print(
        f"{Colors.LIGHT_BLUE}[AGENT REQ]{Colors.ENDC} {caller_info} | {Colors.BOLD}{agent_name}{Colors.ENDC}{context_info}: {Colors.LIGHT_GRAY}{query_preview}{Colors.ENDC}"
    )


def log_agent_response(agent_name: str, status: str, context_id: str = None):
    """Log agent response status."""
    import traceback

    caller = traceback.extract_stack()[-2]
    caller_info = (
        f"{Colors.OKCYAN}{caller.filename.split('/')[-1]}:{caller.lineno}{Colors.ENDC}"
    )
    context_info = f" [ctx:{context_id}]" if context_id else ""
    print(
        f"{Colors.LIGHT_GREEN}[AGENT RESP]{Colors.ENDC} {caller_info} | {Colors.BOLD}{agent_name}{Colors.ENDC}{context_info}: {Colors.WARNING}{status}{Colors.ENDC}"
    )


def log_system_event(event: str, details: str = ""):
    """Log system-level events."""
    import traceback

    caller = traceback.extract_stack()[-2]
    caller_info = (
        f"{Colors.OKCYAN}{caller.filename.split('/')[-1]}:{caller.lineno}{Colors.ENDC}"
    )
    details_info = f" | {details}" if details else ""
    print(
        f"{Colors.HEADER}[SYSTEM]{Colors.ENDC} {caller_info} | {Colors.BOLD}{event}{Colors.ENDC}{details_info}"
    )
