# Project Part #5

This document outlines the requirements for the next part of our data serving API.

### Coding Standards

During the quarter, you will be expected to adhere to the coding standards found [here](https://github.com/dsi-clinic/the-clinic/blob/main/coding-standards/coding-standards.md), and we will frequently use [this rubric](https://github.com/dsi-clinic/the-clinic/blob/main/rubrics/final-technical-cleanup.md) as a checklist for your code.

### Branches

During this quarter we will be using branches and pull requests in order to submit code. **Any commits directly to the main branch will result in points being deducted.** 

### Grading

All grading will be done based off a specific commit hash off of the main branch. At the time that an assignment is due students must submit the commit hash associated with their commit to canvas. You need to submit the _full_ commit hash which is a 40 digit long hash of letters and numbers. It will generally look something like this: `2a2a59af9feacbdd2cd772884b24641c3b75dff7`.

To find the commit hash, you can either use the command line or check GitHub's commit history.

Note that any changes requested in the grading of the previous part need to be corrected.

## Part V: Linting, Documentation, and Accounts

The goal of this assignment is to:
1. Get your code up to the standards required by ruff, specifically the [pyproject.toml](./pyproject.toml)
2. Implement a pre-commit hook, as per the [pre-commit-config.yaml](./pre-commit-config.yaml) (Note: The file should be named `.pre-commit-config.yaml` with a leading dot, but in this repo it is named `pre-commit-config.yaml` without the dot for easier access).
3. Generate an account system for people to track their stock ownership over the time period
4. Convert everything to use `log` rather than print statements.

Specifically, we will create endpoints that:
1. Add stocks to an account
2. Remove stocks from an account
3. Add accounts
4. Delete accounts
5. Calculate the return of the stocks owned by a specific account

Your code must conform to all the requirements of [Part IV](./part_4.md).

### Specifications

#### Updates to Make / Docker
- In addition to existing `make` commands your `db_create` command now needs to create an `accounts` and `stocks_owned` table with the data definition spelled out below. When you create these they should be empty.
- Implement these changes using the `db_manage.py` command.
- Please also create a Make command (DB management) called `db_clean_account` which only resets the `accounts` and `stocks_owned` tables. This should maintain the table, but delete all rows from inside of it. It should be another management command.


#### Table definitions

- There will be two tables as defined below:

```sql
CREATE TABLE accounts (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);
```

```sql
CREATE TABLE stocks_owned (
   account_id INTEGER,
   symbol TEXT NOT NULL,
   purchase_date DATE NOT NULL,
   sale_date DATE NOT NULL,
   number_of_shares INTEGER NOT NULL
);
```

#### Logging

- Update all logs to use a custom logger. As in the demonstration in class, the log format should be `log_format = "%(asctime)s | %(levelname)s | %(message)s"`.
- The log specification is as follows:

| System | Level | Description | 
| --- | --- | --- | 
| All `manage_db` commands | INFO | <ul><li>When a command starts (and which command)</li><li>When a command ends (and how long it took)</li></ul> | 
| `manage_db` loading commands | DEBUG | <ul><li>As each year and market is loaded, log the time it took to load that year and market</li></ul> | 
| `manage_db` table creation commands | DEBUG | <ul><li>Notification that the table was created (with its name)</li></ul> | 
| All routes | DEBUG | <ul><li>Time it took to respond to the route</li><li>The body, header, and route</li><li>The response</li></ul> | 
| All routes | INFO | <ul><li>All non-2xx responses (e.g., 500, 404)</li></ul>| 
| All routes | WARNING | <ul><li>Any time the incorrect (or no) API key is provided</li></ul> | 

- All logs should contain specific and useful information regarding the process, written in a professional manner. 
- No other `print` statements should exist. If there are additional things you want to report, please use an appropriate log command.
- You do not need to override the Werkzeug library logging if you do not wish to. 

#### Updates to Flask
  
- None of the previous endpoints should change from the specification. We will be adding a `v3` set of endpoints.

- Given a base URL of `/api/v3/`, implement the following endpoints with the functionality below. Note that all requests need to go through the same authentication as `v1` and `v2` (e.g., using the `DATA-241-API-KEY` environment variable). If the key is invalid or not present in the header, the request should return a status code of 401.

- Note on date formatting: In the database tables, all dates are stored as `date` types. When they are sent in the request and when they are returned they should all be formatted as a string in `Y-m-d` format.

| Endpoint name | Request Type | Request Info | Expected Response | Other Notes |
| --- | --- | --- | --- | --- | 
| `accounts` | GET |  This lists all accounts. | It should respond with a JSON-formatted list of all the accounts. Each item in the list is of the form: `{ 'account_id' : INT, 'name' : str }` | If no accounts exist it should return an empty list. Upon success, the status code should be 200. |
| `accounts` | POST | This is to create an account. The request body should contain a JSON object `{ 'name' : str }` and it should add a row to the accounts table with that name. | The request should respond with a JSON object of the form `{ 'account_id' : INT }` which is the account ID for this newly created user. | It should return a status code of 201 if an account is created, 409 if the name already exists. |
| `accounts` | DELETE | This will delete an account. Request body should contain a JSON object `{ 'account_id' : INT }` | The request should respond with a JSON object of the form `{ 'account_id' : INT }`. | This should delete the account and all stocks associated with the account. If the account does not exist, then it should return a status code of 404. If the account does exist and is deleted it should return a status code of 204. |
| `accounts/<INT>` | GET | This lists all stocks owned by an account. The integer in the URL should correspond to the account ID. | The response should contain, in the body, a JSON object of the form `{ 'account_id' : INT, 'name' : string, 'stock_holdings' : [{'symbol' : str, 'purchase_date' : str, 'sale_date' : str, 'number_of_shares': int}, ...] }`. Note the `stock_holdings` are a list of JSON objects. | If the account does not exist then it should return a 404. If the account does not hold any stocks the `stock_holdings` should be an empty list. |
| `stocks/<symbol>` | GET | This should list details of all stock holdings across all accounts. | The response should be a JSON object of the form: `{ 'symbol': str, 'holdings': [{'account_id' : int, 'purchase_date' : str, 'sale_date' : str, 'number_of_shares': int }, ...] }`. This is a dictionary that contains a list inside the `holdings` key. | If there are no holdings associated with the stock it should return an empty list. The status code should be 200. |
| `stocks` | POST | Request body should contain a JSON object of the form `{ 'account_id' : int, 'symbol': str, 'purchase_date' : str, 'sale_date': str, 'number_of_shares': INT }` | This should return the appropriate status code and nothing more. | An account can own the same stock multiple times with the same or different dates. Account ID and symbol are not to be assumed unique. A 201 status code should be returned upon success. If either the purchase_date or sale_date is not a valid trading day, then return a 400. |
| `stocks` | DELETE | Request body should contain a JSON object of the form `{ 'account_id' : int, 'symbol': str, 'purchase_date' : str, 'sale_date': str, 'number_of_shares': INT }` | This should return the appropriate status code and nothing else. | This should delete a single holding from an account. Note that if the full information (dates, account, and symbol) does not match, then a 404 should be returned. If the delete is successful then it should return a 204. |
| `accounts/return/<int>` | GET | | This should return the nominal return (how much the account made) across all their holdings. The format should be `{ 'account_id' : int, 'return': float }`. More information on the calculation is below. | If the account ID does not exist it should return status code 404; otherwise it should return 200. |

#### Additional details

- As mentioned in class, I strongly advise you to add an index to the `stocks` table to make sure that your code is performant.
- All dates will be in the format `Y-m-d`, as in the previous parts.
- A trading day is defined as one that is in the dataset. If the date exists in the `stocks` table (e.g., in the original ZIP files) then you should consider it a trading day.
- No request should take more than a few seconds (say 5). If it does, you should add an index to the table to make sure that the query is faster.
- To calculate the return, take the `close` price for the stock on the day that it was sold and subtract the `open` price for the day that it was bought. Multiply this by the number of shares owned. Since an account can have multiple stock holdings, the above calculation should be repeated for all stocks owned by the specific account.

$$
\text{return} = \sum_{\text{holdings}} \text{num\\_shares}
\left( \text{close}_{\text{sales\\_date}} - \text{open}_{\text{purchase\\_date}} \right)
$$

- To determine a "valid" date when adding a stock to an account you should verify that both the `purchase_date` and `sale_date` symbol-date combinations exist in the data. If either combination does not exist, then return a 400. This is important since if either date does not exist then calculating the return would not be possible.

- You should not be able to add stocks to an account that does not exist.

### Additional Fixes

Please correct all of the feedback for Part IV. A portion of the grade will be set to making sure that your code continues to pass the standards set by Part IV.

## How will this be graded

- We will check out the code at the commit hash that you submit.
- All of the previous coding standards will be checked, and all of the previous APIs (`v1` and `v2`) will also be tested.
- We will run `ruff`, using the `pyproject.toml` file here to make sure that your code conforms to the standards therein.
- We will also verify that the `.pre-commit-config.yaml` is in the repo and able to be installed and used.
- We will run the `make` commands outlined above and verify that they work according to the standards set out above.
- We will run an autograder on the endpoints to make sure that they return the correct data and information.
- Your code will also be read over to make sure that it conforms to the standards laid out in class. If you want to receive full credit, make sure that your code has sound logic, is easy to read, maintains a good separation of concerns, and does not violate the DRY principle.
- Finally, your code will also be read to make sure that all documentation is up to date and that the code has a consistent set of abstraction standards.
- There should be no `print` statements. Everything should be logged with an _appropriate_ level.
- All documented code needs to have good faith level of effort that briefly explains the required purpose. Doc strings that say `This is the doc string` or other low-effort submissions will be graded accordingly.
- Your code should also be responsive to changes requested by previous submissions. If you received feedback previously to make a change to the code this change should be present.
- No errors or warnings should occur in normal operations.
- Extraneous code, such as that generated by an LLM doing nothing, will be heavily penalized. 
- The database file itself should not be committed to the repo.
- You should never load the entire dataset into a DataFrame. You need to use SQL commands to select only the relevant data.
