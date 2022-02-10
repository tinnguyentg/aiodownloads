"""Asynchronous downloads"""

import asyncio
from abc import ABC, abstractmethod
from typing import Any, Iterable, Type

import aiohttp

Session = Type[aiohttp.ClientSession]
Items = Iterable[Any]
Item = Any
Response = Type[aiohttp.ClientResponse]


class Downloader(ABC):
    """Asynchronous downloader

    Inherit this then override handle_success, handle_fail methods.
    If your resources you want download are not list of url,
    you may want to override get_item_url
    """

    def __init__(self, semaphore_value: int = 2) -> None:
        self._semaphore_value = semaphore_value
        self.sem = None

    async def download(self, items: Items, **kwargs):
        """Download items then return data

        Parameters
        ----------
        items : Items
            if items are not list of urls, you must override get_item_url
            to get url for request
        kwargs : will passed to aiohttp.ClientSession parameters
        """
        tasks = []
        self.sem = asyncio.BoundedSemaphore(self.semaphore_value)
        async with aiohttp.ClientSession(**kwargs) as session:
            for item in items:
                tasks.append(asyncio.create_task(self.download_one(session, item)))

            await asyncio.gather(*tasks)

    async def download_one(self, session: Session, item: Item):
        """Request item's url"""
        async with self.sem:
            url = self.get_item_url(item)
            async with session.get(url) as resp:
                await self.handle_response(resp, item)

    def get_item_url(self, item: Item):
        """Get url from item"""
        return item

    async def handle_response(self, resp: Response, item: Item):
        try:
            resp.raise_for_status()
            await self.handle_success(resp, item)
        except aiohttp.ClientResponseError:
            await self.handle_fail(resp, item)

    @abstractmethod
    async def handle_success(self, resp: Response, item: Item):
        """Handle successful response"""
        # do your stuff with successful response here
        ...

    @abstractmethod
    async def handle_fail(self, resp: Response, item: Item):
        """Handle failed response"""
        # do your stuff with failed response here
        ...

    @property
    def semaphore_value(self):
        return self._semaphore_value

    @semaphore_value.setter
    def semaphore_value(self, value: int):
        self._semaphore_value = value
