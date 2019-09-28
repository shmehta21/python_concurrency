from random import randint
import time
import asyncio

#Asyncio apps also run on a single core of the cpu and work on the underlying principle
#of co-operative multitasking. If you really want to exploit all cpu cores and achieve true
#parallelism, using mutliprocessing lib should be the option.

def odds(start, stop):
	 for odd in range(start, stop+1, 2):
	 	yield odd

async def square_odds(start, stop):
	for odd in odds(start, stop):
		await asyncio.sleep(2)
		yield odd ** 2

#This block of code is a co-routine. Returns a coroutine object. To run a 
#co-routine you need to run it inside an event loop
#Event loop is the core of every asyncio app. They execute async tasks
async def randn(): 
	await asyncio.sleep(3)
	return randint(1,10)

async def main():
	odd_values = [odd for odd in odds(3,15)]
	odds2 = tuple(odds(21,29))
	print(odd_values)
	print(odds2)
	start = time.perf_counter()
	r = await randn()
	elapsed = time.perf_counter()-start
	print(f'Random value ->{r} took {elapsed:0.2f} seconds')

	start = time.perf_counter()
	#Calling a co-routine multiple times using asyncio.gather which will capture results from all async tasks
	#Unpack the result of list comprehension using * and hand it over to gather
	r = await asyncio.gather(*[randn() for _ in range(10)])
	elapsed = time.perf_counter()-start
	print(f'Random value ->{r} took {elapsed:0.2f} seconds')

	#Using an async for loop to loop over an asynchronous generator
	async for so in square_odds(11,17):
		print(f'{so}')



if __name__ =='__main__':
	asyncio.run(main())
	