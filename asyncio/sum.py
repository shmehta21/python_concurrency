import asyncio
import json
import time
import aiohttp


async def worker(name, n, session):
	print(f'worker-{name}')
	url = f'https://qrng.anu.edu.au/API/jsonI.php?length={n}&type=uint16'
	response = await session.request(method='GET', url=url)#Note how ClientSession object is used to make a HTTP GET request
	value = await response.text()
	json_val = json.loads(value)
	return sum(json_val['data'])
	



async def main():
	async with aiohttp.ClientSession() as session:
		#response = await worker('Bob',3, session) Takes about 3 seconds to return this response for 1 request
		sums = await asyncio.gather(*(worker(f'w{i}', n, session ) for i, n in enumerate(range(2,15)))) #Finishes with all of these within ~2.5 secs.Beauty of asyncio!
		print(f'Sums->{sums}')
	

if __name__ == '__main__':
	start = time.perf_counter()
	asyncio.run(main())
	elapsed = time.perf_counter() - start
	print(f'executed in {elapsed:0.2f} seconds')