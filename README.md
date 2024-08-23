# Benchmark: requests vs. aiohttp

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

*Python 3.10*:

```
Benchmark 1: venv310/bin/python benchmark.py threads-recreate -r 1000
  Time (mean ± σ):      1.098 s ±  0.005 s    [User: 1.022 s, System: 0.133 s]
  Range (min … max):    1.091 s …  1.108 s    10 runs
 
Benchmark 2: venv310/bin/python benchmark.py threads-reuse -r 1000
  Time (mean ± σ):      1.092 s ±  0.005 s    [User: 1.036 s, System: 0.131 s]
  Range (min … max):    1.082 s …  1.098 s    10 runs
 
Benchmark 3: venv310/bin/python benchmark.py threads-map -r 1000
  Time (mean ± σ):      1.096 s ±  0.005 s    [User: 1.032 s, System: 0.135 s]
  Range (min … max):    1.088 s …  1.103 s    10 runs
 
Benchmark 4: venv310/bin/python benchmark.py async-for -r 1000
  Time (mean ± σ):     693.6 ms ±   2.1 ms    [User: 559.1 ms, System: 51.7 ms]
  Range (min … max):   691.4 ms … 698.7 ms    10 runs
 
Benchmark 5: venv310/bin/python benchmark.py async-map -r 1000
  Time (mean ± σ):     694.3 ms ±   2.0 ms    [User: 553.2 ms, System: 55.6 ms]
  Range (min … max):   690.7 ms … 698.6 ms    10 runs
 
Summary
  venv310/bin/python benchmark.py async-for -r 1000 ran
    1.00 ± 0.00 times faster than venv310/bin/python benchmark.py async-map -r 1000
    1.57 ± 0.01 times faster than venv310/bin/python benchmark.py threads-reuse -r 1000
    1.58 ± 0.01 times faster than venv310/bin/python benchmark.py threads-map -r 1000
    1.58 ± 0.01 times faster than venv310/bin/python benchmark.py threads-recreate -r 1000
```

*Python 3.12*:

```
Benchmark 1: venv312/bin/python benchmark.py threads-recreate -r 1000
  Time (mean ± σ):      1.101 s ±  0.004 s    [User: 1.019 s, System: 0.138 s]
  Range (min … max):    1.094 s …  1.107 s    10 runs
 
Benchmark 2: venv312/bin/python benchmark.py threads-reuse -r 1000
  Time (mean ± σ):      1.095 s ±  0.004 s    [User: 1.032 s, System: 0.139 s]
  Range (min … max):    1.089 s …  1.101 s    10 runs
 
Benchmark 3: venv312/bin/python benchmark.py threads-map -r 1000
  Time (mean ± σ):      1.095 s ±  0.006 s    [User: 1.032 s, System: 0.132 s]
  Range (min … max):    1.087 s …  1.104 s    10 runs
 
Benchmark 4: venv312/bin/python benchmark.py async-for -r 1000
  Time (mean ± σ):     691.8 ms ±   1.8 ms    [User: 561.1 ms, System: 49.3 ms]
  Range (min … max):   689.1 ms … 694.4 ms    10 runs
 
Benchmark 5: venv312/bin/python benchmark.py async-map -r 1000
  Time (mean ± σ):     691.5 ms ±   1.5 ms    [User: 559.0 ms, System: 51.3 ms]
  Range (min … max):   688.3 ms … 693.3 ms    10 runs
 
Summary
  venv312/bin/python benchmark.py async-map -r 1000 ran
    1.00 ± 0.00 times faster than venv312/bin/python benchmark.py async-for -r 1000
    1.58 ± 0.01 times faster than venv312/bin/python benchmark.py threads-map -r 1000
    1.58 ± 0.01 times faster than venv312/bin/python benchmark.py threads-reuse -r 1000
    1.59 ± 0.01 times faster than venv312/bin/python benchmark.py threads-recreate -r 1000
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

   The benchmark script `run.sh` does something you could do yourself but it saves you some typing.

   It has sensible default but expects you to point it to the python interpreter to use. This is
   to be able to run the test against different virtual environments that belong to different Python
   versions.


   ```shell
   ./run.sh ".venv/bin/python" --warmup 10 --runs 10 --output "results.json"
   ```

## Proper test

### Setup equirements

2x `c5.large` EC2 instance running on dedicated hardware, running Ubuntu 24.02.

### Instance configuration

The configuration must be done both on the server instance and on the client instance. 

Once you've logged in to the AAWS instance, do the following

```shell
# Become root
sudo su

# Install hyperfine and Python
apt update
add-apt-repository -y ppa:deadsnakes/ppa
apt install -y hyperfine python3.10 python3.12 python3.10-venv python3.12-venv

# Clone this repo
git clone https://github.com/vduseev/requests-vs-aiohttp.git /benchmark
cd /benchmark

# Install dependencies
python3.10 -m venv venv310
python3.10 -m venv venv312
./venv310/bin/pip install -r requirements.txt
./venv312/bin/pip install -r requirements.txt
```

### Running the test

#### Server

```shell
uvicorn --host 0.0.0.0 --port 8080 --no-access-log --log-level critical "server:app"
```

#### Client

```shell
# Point the client to the correct server
export BENCHMARK_SERVER_HOST=<ip_address_of_server>
export BENCHMARK_SERVER_PORT=8080

# Run the hyperfine benchmarks for Python 3.10
./run.sh "venv310/bin/python" -w 20 -r 100 -q 1000 -o "results-310.json"

# Run the hyperfine benchmarks for Python 3.12
./run.sh "venv312/bin/python" -w 20 -r 100 -q 1000 -o "results-312.json"
```
