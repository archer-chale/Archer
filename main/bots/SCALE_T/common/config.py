


class BotConfig:
    def __init__(self, container_name: str) -> None:
        self.container_name = container_name


# End goal for now is
# ST_AAPL_<custom_id>_live
# if this is going to be the name, then it must be propagated down from container launcher