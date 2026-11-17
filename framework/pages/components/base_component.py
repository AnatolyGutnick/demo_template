"""Reusable UI part (header, modal, table row) scoped to a root locator."""

from playwright.sync_api import Locator


class BaseComponent:
    def __init__(self, root: Locator) -> None:
        self.root = root
