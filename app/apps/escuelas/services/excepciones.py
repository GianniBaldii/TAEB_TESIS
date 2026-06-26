class EscuelasError(Exception):
    """Error controlado del módulo de escuelas."""


class EscuelaActivaNoEncontradaError(EscuelasError):
    """El usuario no tiene una escuela activa sobre la que operar."""
