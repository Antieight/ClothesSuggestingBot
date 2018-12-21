SERVICE_WEATHER = 0
SERVICE_CLOTHES_SET = 1


def is_valid_service_id(service_id: int) -> bool:
    return service_id in range(2)
