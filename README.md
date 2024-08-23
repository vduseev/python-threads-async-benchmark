# Python threads vs. async benchmark

## Summary

This benchmark measures performance difference between:

`ThreadPoolExecutor` + `requests` 

vs.

`asyncio` + `aiohttp`.

Multiple methods are used:

1. Execute N requests in a thread pool of size S, submitting to the pool, and recreating the thread pool every time.
2. Execute N requests in a thread pool of size S, submitting to the pool, but reusing the same pool.
3. Execute N requests in a thread pool of size N, using `map()` instead of a for loop to submit requests.
4. Execute N requests in asyncio event loop using `create_task()` and creating them using a for loop.
5. Execute N requests in asyncio event loop using `create_task()` and creating them using a `map()` function.

## Results

A simple for loop that creates async tasks within the asyncio loop is the fastest option. Async is faster than threads.

```
Summary
  .venv/bin/python benchmark.py async-for -r 1000 ran
    1.01 ± 0.22 times faster than .venv/bin/python benchmark.py async-map -r 1000
    1.54 ± 0.20 times faster than .venv/bin/python benchmark.py threads-recreate -r 1000
    1.55 ± 0.21 times faster than .venv/bin/python benchmark.py threads-reuse -r 1000
    1.57 ± 0.21 times faster than .venv/bin/python benchmark.py threads-map -r 1000
```

## Usage

### Contents

* Benchmark code is stored in the `benchmark.py` file.
* HTTP server code is stored in the `server.py` file.

### Steps

1. Configure a Python virtual environemnt with dependencies
1. Start server in a different shell

   ```shell 
   uvicorn --host 0.0.0.0 --port 8080 --no-access-log --log-level critical "server:app"
   ```

1. Run a specific benchmark to do a single test run

   Available commands:

   ```shell
   usage: benchmark.py [-h] [-c CHUNK] [-r REQUESTS] test_name

   positional arguments:
     test_name

   options:
     -h, --help            show this help message and exit
     -c CHUNK, --chunk CHUNK
     -r REQUESTS, --requests REQUESTS
   ```

   Running:

   ```shell
   python benchmark.py threads-recreate -r 100 -c 100
   ```

1. Run a full proper benchmark using `hyperfine`

   ```shell
   ./run.sh
   ```

## Setup

### Requirements

2x `c5.large` EC2 instance running on dedicated hardware, running Ubuntu 24.02.

### Instance configuration

The configuration must be done both on the server instance and on the client instance. 

Once you've logged in to the AAWS instance, do the following

```shell
# Become root
sudo su

# Install hyperfine and Python
apt update
add-apt-repository ppa:deadsnakes/ppa
apt install hyperfine python3.10 python3.12

# Clone this repo
git clone https://github.com/vduseev/python-threads-async-benchmark.git /benchmark
cd /benchmark

# Install dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Server

```shell
uvicorn --host 0.0.0.0 --port 8080 --no-access-log --log-level critical "server:app"
```

## Client

```shell
# Point the client to the correct server
export BENCHMARK_SERVER_HOST=<ip_address_of_server>
export BENCHMARK_SERVER_PORT=8080

# Run the hyperfine benchmarks
./run.sh
```
