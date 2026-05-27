import structlog
from pymongo import monitoring

logger = structlog.get_logger(__name__)

_IGNORED_COMMANDS = {
    "hello",
    "ismaster",
    "isMaster",
    "ping",
    "buildInfo",
    "saslStart",
    "saslContinue",
    "endSessions",
}


class MongoQueryLogger(monitoring.CommandListener):
    """
    Logs Mongo command durations.

    - If log_all=False, only logs commands >= slow_query_ms.
    - Ignores handshake/heartbeat commands to reduce noise.
    """

    def __init__(self, *, slow_query_ms: int, log_all: bool = False) -> None:
        self.slow_query_ms = slow_query_ms
        self.log_all = log_all

    def started(self, event: monitoring.CommandStartedEvent) -> None:
        # No-op: we log only completed/failed commands with final duration.
        return

    def succeeded(self, event: monitoring.CommandSucceededEvent) -> None:
        command_name = event.command_name
        if command_name in _IGNORED_COMMANDS:
            return

        duration_ms = round(event.duration_micros / 1000, 2)
        is_slow = duration_ms >= self.slow_query_ms
        if not self.log_all and not is_slow:
            return

        # For most command shapes, command[command_name] holds target collection.
        target = event.reply.get("ns") if isinstance(event.reply, dict) else None
        log_fn = logger.warning if is_slow else logger.info
        log_fn(
            "mongo.query",
            command=command_name,
            duration_ms=duration_ms,
            database=event.database_name,
            target=target,
            slow=is_slow,
        )

    def failed(self, event: monitoring.CommandFailedEvent) -> None:
        command_name = event.command_name
        if command_name in _IGNORED_COMMANDS:
            return
        duration_ms = round(event.duration_micros / 1000, 2)
        logger.error(
            "mongo.query_failed",
            command=command_name,
            duration_ms=duration_ms,
            database=event.database_name,
            failure=event.failure,
        )
