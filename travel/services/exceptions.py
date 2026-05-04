class ServiceUnavailableError(Exception):
    """Внешний сервис недоступен (сеть, таймаут). Сообщение уходит клиенту API."""

    def __init__(self, message: str = 'Art Institute service is temporarily unavailable.'):
        self.message = message
        super().__init__(message)
