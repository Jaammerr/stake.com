def is_float(data: str) -> bool:
    try:
        float(data)
        return True
    except ValueError:
        return False
