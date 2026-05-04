class ServiceUnavailableError(Exception):
    """Upstream API unreachable (timeout/connection). Message is safe for clients."""

    def __init__(self, message: str = 'Art Institute service is temporarily unavailable.'):
        self.message = message
        super().__init__(message)
