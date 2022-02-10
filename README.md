# aiodownloads

Asynchronous downloads

## Usage

Inherit `aiodownloads.Downloader` then override handle_success, handle_fail methods

## Examples

- Download list of urls

```python
import asyncio

from aiodownloads import Downloader

urls = [
    'https://httpbin.org/status/200',
    'https://httpbin.org/status/400'
]
class UrlsDownloader(Downloader):

    async def handle_success(self, resp, item):
        content = await resp.read()
        # save content stuff

    async def handle_fail(self, resp, item):
        ...

url_downloader = UrlsDownloader()
asyncio.run(url_downloader.download(urls))
```
