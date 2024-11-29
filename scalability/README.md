# Steps to Test TigerVector Scalability

## 1. Deploy TigerVector on a Cluster
- Follow the instructions in the `README` file located in the `../comparison` directory to set up the database.

## 2. Install wrk2
- Download and install `wrk2` from [its GitHub repository](https://github.com/giltene/wrk2).

## 3. Run Tests
- Execute the test script:
  ```bash
  ./running.sh
  ```

## 4. Collect and Analyze Results
- Collect the output of `Requests/sec:` from the test results.
- Use the provided script to calculate QPS:
  ```bash
  python3 calc.py
  ```
