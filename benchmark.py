import asyncio
import argparse
import inspect
import os
from concurrent.futures import ThreadPoolExecutor, Future, wait
from datetime import datetime
from functools import wraps
from time import perf_counter
from typing import Iterable, TypeVar, Generator, Callable

import aiohttp
import requests


T = TypeVar("T")

server_host = os.environ.get("BENCHMARK_SERVER_HOST", "127.0.0.1")
server_port = os.environ.get("BENCHMARK_SERVER_PORT", "8080")
url = f"http://{server_host}:{server_port}/multiply"

print(f"Going to make calls to the url: {url}")

sync_session = requests.Session()
async_session: aiohttp.ClientSession = None


def chunkify(items: Iterable[T], size: int = 100) -> Generator[T, None, None]:
    for i in range(0, len(items), size):
        yield items[i:i + size]


def sync_get(number: int) -> int:
    resp = sync_session.get(url, params={"number": number})
    data = resp.json()
    result = data["result"]
    return result


async def async_get(number: int) -> int:
    async with async_session.get(url, params={"number": number}) as resp:
        data = await resp.json()
        result = data["result"]
        return result


def benchmark(f: Callable) -> Callable:
    if inspect.iscoroutinefunction(f):
        async def async_wrapper(*args, **kwargs):

            print(f"Start: {datetime.now()}")
            start = perf_counter()

            await f(*args, **kwargs)

            end = perf_counter()
            total = end - start
            print(f"Elapsed time: {total:.6f} seconds")
            print(f"End: {datetime.now()}")
        return async_wrapper
    else:
        @wraps(f)
        def sync_wrapper(*args, **kwargs):
            print(f"Start: {datetime.now()}")
            start = perf_counter()

            f(*args, **kwargs)

            end = perf_counter()
            total = end - start
            print(f"Elapsed time: {total:.6f} seconds")
            print(f"End: {datetime.now()}")
        return sync_wrapper


@benchmark
def threads_recreate(queries: list[int], chunk_size: int):
    for chunk in chunkify(queries, size=chunk_size):
        with ThreadPoolExecutor(max_workers=chunk_size) as tpe:
            for number in chunk:
                tpe.submit(sync_get, number)


@benchmark
def threads_reuse(queries: list[int], chunk_size: int):
    with ThreadPoolExecutor(max_workers=chunk_size) as tpe:
        for chunk in chunkify(queries, size=chunk_size):
            futures: list[Future] = []
            for number in chunk:
                f = tpe.submit(sync_get, number)
                futures.append(f)
            wait(futures)


@benchmark
def threads_map(queries: list[int]):
    with ThreadPoolExecutor(max_workers=len(queries)) as tpe:
        tpe.map(sync_get, queries)


@benchmark
async def async_for(queries: list[int]):
    global async_session
    async_session = aiohttp.ClientSession()

    async with async_session:
        tasks = []
        for i in queries:
            task = asyncio.create_task(async_get(i))
            tasks.append(task)
        await asyncio.gather(*tasks)

        
@benchmark
async def async_map(queries: list[int]):
    def launch(number: int):
        return asyncio.create_task(async_get(number))
    
    global async_session
    async_session = aiohttp.ClientSession()

    async with async_session:
        tasks = list(map(launch, queries))
        await asyncio.gather(*tasks)


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("test_name")
    parser.add_argument("-c", "--chunk", type=int, default=100)
    parser.add_argument("-r", "--requests", type=int, default=100)
    args = parser.parse_args()

    queries = list(range(args.requests))
    test_name = str(args.test_name).lower().replace("-", "_")
    match test_name:
        case "threads_recreate":
            threads_recreate(queries, args.chunk)
        case "threads_reuse":
            threads_reuse(queries, args.chunk)
        case "threads_map":
            threads_map(queries)
        case "async_for":
            asyncio.run(async_for(queries))
        case "async_map":
            asyncio.run(async_for(queries))
        case _:
            print("Unknown test")


if __name__ == "__main__":
    main()