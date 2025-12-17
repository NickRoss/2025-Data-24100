# Project Part #7: Final Submission

This document outlines the requirements for the final part of our data serving API.

### Coding Standards

During the quarter, you will be expected to adhere to the coding standards found [here](https://github.com/dsi-clinic/the-clinic/blob/main/coding-standards/coding-standards.md) and we will frequently use [this rubric](https://github.com/dsi-clinic/the-clinic/blob/main/rubrics/final-technical-cleanup.md) as a checklist for your code.

### Branches

When you submit the code, there should only be _a single branch_ with the name `main`. All other branches need to be deleted.

### Grading

All grading will be done based on a specific commit hash off of the main branch. At the time that an assignment is due, students must submit the commit hash associated with their commit to Canvas. You need to submit the _full_ commit hash which is a 40-digit-long hash of letters and numbers. It will generally look something like this: `2a2a59af9feacbdd2cd772884b24641c3b75dff7`.

To find the commit hash, you can either use the command line or check GitHub's commit history.

Note that any changes requested in the grading of the previous part need to be corrected.

## Part VII: Final Submission

Your code must conform to all the requirements of all previous parts, including [Part VI](./part_6.md).

### Backtesting API

In this section we will add a `v4` route which will backtest a trading strategy based on our data.

Given a base URL of `/api/v4/`, implement the following endpoint with the functionality below. Note that all requests need to go through the same authentication as `v1`, `v2`, and `v3` (e.g., using the `DATA-241-API-KEY` environment variable). If the key is invalid or not present in the header, the request should return a status code of 401.

| Endpoint name | Request Type | Request Info | Expected Response | Other Notes |
| --- | --- | --- | --- | --- |
| `back_test` | POST |  Returns the nominal value of a specific trading strategy.  | It should respond with a JSON object of the form: `{ 'return' : "float(2)" \| example: 123.45, 'num_observations': int }` with **status code 200 on success**. | More info about the request below. |

The POST request body should have the following schema:

```
{
    "value_1" : Price Target,
    "value_2" : Price Target,
    "operator" : LT or LTE,
    "purchase_type": B or S,
    "start_date": date,
    "end_date": date
}
```

The objective of this exercise is to define a condition (based on `value_1`, `value_2`, and the `operator`) and, if that condition is met between the dates specified, to either buy or sell a share of the stock depending on the `purchase_type`.

The price target consists of two components: a price type (`O`, `C`, `L`, `H`) and a number (`1–10`) which represents n days in the past.

The operator consists of either less than (`LT`, which represents <) or less than or equal (`LTE`, which represents ≤).

For every day between the `start_date` and `end_date` (inclusive on both sides) evaluate the metrics and decide to buy or sell that stock that day (by sell we mean short the stock — selling a share to someone else) if the condition is met.

How to interpret the condition: take `value_1` and `value_2` and then use the operator to compare.

Let's consider the example here:

```
{
    "value_1" : "O1",
    "value_2" : "C1",
    "operator" : "LT",
    "purchase_type": "B", 
    "start_date": "2020-01-03",
    "end_date": "2020-01-03"
}
```

In this case we can read this as: Buy (since `B`) if `O1 LT C1`, i.e., if the previous trading day's open is strictly less than its close. We will do this on a single day.
  
Let's consider the following example to help us understand how to do the calculation for a particular stock:


<table>
<caption>Microsoft Snippet</caption>
<tr>
<td><pre>
Symbol  Date         Open     Close   High     Low
------  -----------  -------  ------  -------  --------
MSFT    01-Jan-2020  157.7    157.7   157.7    157.7
MSFT    02-Jan-2020  158.78   160.62  160.73   158.33
MSFT    03-Jan-2020  158.32   158.62  159.945  158.06
MSFT    06-Jan-2020  157.08   159.03  159.1    156.51
MSFT    07-Jan-2020  159.32   157.58  159.67   157.32
MSFT    08-Jan-2020  158.93   160.09  160.8    157.9491
MSFT    09-Jan-2020  161.835  162.09  162.215  161.03
MSFT    10-Jan-2020  162.82   161.34  163.22   161.18
MSFT    13-Jan-2020  161.76   163.28  163.31   161.26
MSFT    14-Jan-2020  163.39   162.13  163.6    161.72
MSFT    15-Jan-2020  162.62   163.18  163.94   162.57
</pre></td>
</tr>
</table>

To calculate the return, go through every stock that has data on January 3rd (such as `MSFT`) and see if the condition is met. In this case, the `O1` price is `158.78` and the `C1` price is `160.62`. Our condition is met (`158.78 < 160.62`), so Microsoft will be included in our calculations.

Since we are buying the stock, we will, as we did in the previous assignment, buy the stock at the open and sell the stock at the close of the 3rd, which yields a return of `158.62 - 158.32 = 0.30`.

Repeat this over all stocks that exist on January 3rd and sum the total return to send back in the response.

Let's do another one:

```
{
    "value_1" : "O1",
    "value_2" : "O2",
    "operator" : "LTE",
    "purchase_type": "S", 
    "start_date": "2020-01-13",
    "end_date": "2020-01-14"
}
```

This strategy says: "Sell if yesterday's open price is less than or equal to the open price from two days ago."

| Date | Notes | 
| --- | --- | 
| January 13th | <ul><li>O1 (open from yesterday - Jan 10): 162.82</li><li>O2 (open from 2 days ago - Jan 9): 161.835</li><li>162.82 ≰ 161.835 (condition NOT met)</li></ul> |
| January 14th | <ul><li>O1 (open from yesterday - Jan 13): 161.76</li><li>O2 (open from 2 days ago - Jan 10): 162.82</li><li>161.76 ≤ 162.82 (condition MET)</li><li>Since this is a sell/short strategy:</li><li>Sell at open (163.39), buy back at close (162.13)</li><li>Return = 163.39 - 162.13 = 1.26</li></ul> |


The other piece of the response is the `num_observations`. This should count the number of stock-days that met the criteria. Continuing the last example, Microsoft would add 1 to the number of observations reported because only 1 of the 2 days met the criteria and was counted.

#### Backtesting Specifications:

- If either the start or end date is not a trading day, your route should return an error (status code 400).
- I strongly advise you to add an indexes to the `stocks` table to make sure that your code is performant.
- All dates will be of the format ['Y-m-d'](https://strftime.org/), as in the previous parts.
- A trading day is defined as one that is in the dataset. If the date exists in the `stocks` table (e.g., in the original ZIP files), then you should consider it a trading day.
- **Important:** When calculating historical lookback dates (e.g., O1, O2, C3), you must only use actual trading days from your dataset. Do not assume dates by calendar arithmetic (e.g., "1 day ago" is not necessarily yesterday - it's the previous trading day in your data). All date operations must account for weekends and holidays by querying actual dates from your stocks table. Never query your database with a date that might not exist in your dataset, as this can cause errors.
- No request should take more than a few seconds (say 5). If it does you should add an index to the table to make sure that the query is faster.
- You can assume that the back-testing window will never be more than 10 days. 
- You should not include any stock-date combination as an observation unless all of the required dates are there. For example, if `O3` is requested, but the stock was just created in the dataset (such as they just had an IPO) then that stock would _not_ be included as an observation. 
- Do not use pandas `read_sql` to interface with the database. You are welcome to put data from SQL into a DataFrame, but that action and code must be written by hand.
- **Testing:** Make sure to add a new test (number 22) which runs a schema and exact test on the results of a specific call to `/api/v4/back_test`.


### MCP Server Implementation

You must implement an MCP (Model Context Protocol) server that exposes your API functionality as tools that AI assistants can use.

#### MCP Requirements

- The MCP server must expose the following tools that correspond to your API endpoints:
  - **From v1/v2 API (1 tool required):** 
    - `/api/v2/{YEAR}` - Get row count for a specific year
  - **From v3 API (5 tools required):**
    - `/api/v3/accounts` (GET) - List all accounts
    - `/api/v3/accounts` (POST) - Create a new account
    - `/api/v3/accounts/<int>` (GET) - Get stocks owned by an account
    - `/api/v3/stocks` (POST) - Add stock to an account
    - `/api/v3/accounts/return/<int>` (GET) - Calculate return for an account
  - **From v4 API (1 tool required):**
    - `/api/v4/back_test` (POST) - Run backtesting strategy
- Each tool must have:
  - A clear, descriptive name
  - A detailed description explaining what the tool does
  - Proper input schema (via type hints and docstrings)
  - Proper error handling
- The MCP server must be able to communicate with your tools.
- The MCP server should use async/await patterns as appropriate. Please use the code found in [17_MCP](../lecture_examples/17_MCP/) as a framework. Pay close attention to where `await` and `async` are found in the code.
- Tools should use type aliases.

#### MCP Library and Configuration

**Required Library:** You must use the `fastmcp` library (not `mcp.server.stdio` or other implementations). Install it with:
```bash
uv add fastmcp
```

Your MCP server should import and use FastMCP:
```python
from fastmcp import FastMCP

mcp = FastMCP("Stock API MCP Server")
```

**Transport Configuration:** Your MCP server must use **SSE (Server-Sent Events) transport** to communicate with clients. The server must be configured to run with the following parameters:
```python
if __name__ == "__main__":
    mcp.run(transport="sse", host="0.0.0.0", port=3000)
```

- The MCP server should listen on **port 3000**
- The server must be accessible from outside the container (hence `host="0.0.0.0"`)
- Using SSE transport allows AI assistants and other clients to connect to your MCP server over HTTP

### Docker Compose Migration

**Because you now have two services (your Flask API and your MCP server), you must use Docker Compose to manage both services.**

All Docker commands must now use Docker Compose instead of single-container Docker commands.

#### Docker Compose Requirements

- You must create a `docker-compose.yml` file in the root of your repository that defines two services:
  - One service for your Flask application
  - One service for your MCP server
- All `make` commands must use `docker compose` instead of `docker run`.
- Your `Makefile` should be updated to use Docker Compose commands:
  - `make build` should use `docker compose build`
  - `make flask` should use `docker compose up flask-app` (or your service name)
  - `make mcp` should use `docker compose up mcp-server` (or your service name)
  - `make interactive` should use `docker compose run --rm <service-name> /bin/bash`
  - `make notebook` should use `docker compose run --rm <service-name> ...` (with appropriate command to start Jupyter)
  - Database commands (`db_create`, `db_load`, etc.) should use `docker compose run --rm <service-name> ...`
  - `make test` should use `docker compose run --rm <service-name> ...`
  - `make autodocs` should use `docker compose run --rm <service-name> ...` (with appropriate command to start autodocs)
  - `make logs-mcp` or similar should use `docker compose logs mcp-server` (or your service name)
  - `make start-all` should start both services together (Flask API and MCP server) using `docker compose up -d flask-app mcp-server` (or your service names)
- Your project structure should be organized appropriately for Docker Compose (see `lecture_examples/16_compose` and `lecture_examples/17_MCP` for reference).
- All environment variables should be defined in the `docker-compose.yml` file's `environment` section for each service. Both `RAW_DATA_DIR` and `DATA_241_API_KEY` should be pulled in from the _host_ environment.
- Port mappings should be defined in the `docker-compose.yml` file's `ports` section for each service.
  - Flask app should expose its API port (e.g., `"4000:5000"` to map container port 5000 to host port 4000)
  - **MCP server must expose port 3000** (e.g., `"3000:3000"`) for SSE transport
  - Note: When using `docker compose up`, ports defined in the yml file are automatically mapped.
  - When using `docker compose run`, you have two options: (1) add `-p` flags to the command, or (2) add `--service-ports` flag to use the ports from the yml file.
  - Do not put port mappings in the Makefile
- Volume mounts should be defined in the `docker-compose.yml` file.
  - The MCP server needs access to your Flask API code and/or needs appropriate volume mounts to its own codebase for development
- You may add additional services to your `docker-compose.yml` if needed (e.g., for documentation, testing, etc.),but they are _not_ required.

### Final Review

This final submission represents a comprehensive review of your entire project. All previous parts should be complete and working correctly, and you must have a working MCP server.

#### Additional Details

- Please make sure to go back to the original specification for the entire API. As part of the final review, another look at all of these will be completed. This final look will be deeper than what was originally undertaken.
- If you wish to receive a solid score, go back and verify against the original rubric the standard that you are checking for. I would strongly recommend deleting and re-cloning the repo, making sure that everything works correctly from a clean start.
- **Make sure that your database is not in the repository.** The database needs to be generated by the user.
- Make sure the code works before submitting.
- Your MCP server must be properly integrated into your Docker Compose setup.
- All services (Flask API, MCP server, etc.) should be defined in your `docker-compose.yml`.
- Make sure your MCP server can successfully communicate with your Flask API.

### Additional Fixes

Please correct all of the feedback for Part VI. A portion of the grade will be set to making sure that your code continues to pass the standards set by Part VI.

## How will this be graded

- We will check out the code at the commit hash that you submit.
- All of the previous coding standards will be checked, and all of the previous APIs (`v1`, `v2`, `v3`, and `v4`) will also be tested.
- We will run `ruff`, using the `pyproject.toml` file here to make sure that your code conforms to the standards therein.
- We will also verify that the `.pre-commit-config.yaml` is in the repo and able to be installed and used.
- We will run the `make` commands outlined above and verify that they work according to the standards set out above. All commands must use Docker Compose.
- We will verify that your `docker-compose.yml` file is properly configured and that all services can be started and stopped correctly.
- We will run an autograder on the endpoints to make sure that they return the correct data and information. This includes types and casing. E.g. _use testing_ to ensure compliance!
- Your code will also be read over to make sure that it conforms to the standards laid out in class. If you want to receive full credit, make sure that your code has sound logic, is easy to read, maintains a good separation of concerns, and does not violate the DRY principle.
- Finally, your code will also be read to make sure that all documentation is up to date and that the code has a consistent set of abstraction standards.
- There should be no `print` statements. Everything should be logged with an _appropriate_ level.
- All documented code needs to have good faith level of effort that briefly explains the required purpose. Doc strings that say `This is the doc string` or other low-effort submissions will be graded accordingly.
- Your code should also be responsive to changes requested by previous submissions. If you received feedback previously to make a change to the code this change should be present.
- No errors or warnings should occur in normal operations.
- Extraneous code, such as that generated by an LLM doing nothing, will be heavily penalized. 
- The database file itself should not be committed to the repo.
- You should never load the entire dataset into a DataFrame. You need to use SQL commands to select only the relevant data.
- We will verify that your MCP server is properly configured and can be started.
- We will test that your MCP tools are properly exposed and functional.
- We will verify that your MCP server can communicate with your Flask API.
