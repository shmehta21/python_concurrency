# Thumbnail Maker Workflow

1.) Downloads the images from the source location. (I/O bound operation)
2.) Perform the resize operation keeping the dimensions intact. (CPU bound operation)

For this eg, we will consider foll image sizes
Large : 200*200
Medium: 64 * 64
Small: 32 *32

Also includes examples from AsyncIO lib using async generators, coroutines, aiohttp, async with , async for etc
