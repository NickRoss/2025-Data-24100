# Project Part #6

This document outlines the requirements for the next part of our data serving API.

### Coding Standards

During the quarter, you will be expected to adhere to the coding standards found [here](https://github.com/dsi-clinic/the-clinic/blob/main/coding-standards/coding-standards.md) and we will frequently use [this rubric](https://github.com/dsi-clinic/the-clinic/blob/main/rubrics/final-technical-cleanup.md) as a checklist for your code.

### Branches

During this quarter we will be using branches and pull requests in order to submit code. **Any commits directly to the main branch will result in points being deducted.** 

### Grading

All grading will be done based on a specific commit hash off of the main branch. At the time that an assignment is due, students must submit the commit hash associated with their commit to Canvas. You need to submit the _full_ commit hash which is a 40-digit-long hash of letters and numbers. It will generally look something like this: `2a2a59af9feacbdd2cd772884b24641c3b75dff7`.

To find the commit hash, you can either use the command line or check GitHub's commit history.

Note that any changes requested in the grading of the previous part need to be corrected.

## Part VI: Adding tests and autodocs

- Your code must conform to all the requirements of all previous parts, including [Part V](./part_5.md).

### Autodocs

Using the `mkdocs` package, please set up autodocs. Similar to the lecture example, please create:

  1. An `about` page which includes your names and light biographical details. By "light," I mean only what you are willing to share publicly. Or you can just make up a short bio. Make this look nice and use some HTML tags to organize it. You will be graded on making it look professional and clean. A wall of text without any formatting or text with grammar/readability errors will result in a lower grade.
  2. An `index` page which contains a brief description of the project and what you have done. This should be short and sweet — but also look nice. Please add at least one image, using HTML tags to make the image look well-formatted.
  3. A `docs` page consisting of documentation generated from the code. All functions need to be accessible via the docs (including functions from the tests), so verify that all files were appropriately processed. Note: This documentation needs to be well written; it should be descriptive of what the code is doing. While there are quite a few "boilerplate" functions that will not need any description beyond a sentence, functions which contain logic should be explained. 

Please refer to the notes about how to set up autodocs. When the autodoc server is run, it should be accessible on port 4040. Start it via `make autodocs`. 

### Tests

Leveraging the `pytest` library, please write end-to-end tests for every `v1` and `v2` route. Note: This does _not_ include `v3` routes. 

For each route you need to write a schema test using the `jsonschema` library. This should be a complete schema for what is returned and should include status code. There are 3 `v1` routes (0–2) and 6 `v2` routes (3–8), for a total of 9 test functions.

Note: When you name the tests, use a naming convention which identifies the route based on the numbers above. So the `v1` routes should have names like `test_0_v1_row_count`, `test_1_v1_...`, `test_2_v1_...` where the enumerated numbers align with the numbers in parentheses above. 

Please also write tests which do the following:
- Send a request without any API key and verify that the returned response is correct (for one `v1` route and one `v2` route). This is two different calls within a single test function (test number 9).
- Send a request against `/api/v2/{YEAR}` with an incorrect year (such as 1980) and verify that it returns the correct status code (test number 10).
- Send a request with an invalid API key and verify that the returned response is correct (for one `v1` route and one `v2` route). This is two different calls within a single test function (test number 11).

- Adding up the above, there should be 9 + 1 + 1 + 1 = 12 test functions in your test suite. Please make sure to name them properly. All of these tests should both reflect the rubric as well as pass.

- In terms of names, they should all follow the convention: `test_{test-number:int}_{whatever you want to name it}`. You can name them whatever you would like as long as it follows good naming practices.

- You will also need to install `pytest-cov` to generate the coverage report (required).

- You can find a breakdown of all tests and their numbers in the chart here:

| Test Number | Route | Info | 
| --- | --- | --- |
| 0 | `/api/v1/row_count` | Schema Test | 
| 1 | `/api/v1/unique_nyse_stock_count` | Schema Test | 
| 2 | `/api/v1/unique_nasdaq_stock_count` | Schema Test | 
| 3 | `/api/v2/{YEAR}` | Schema Test | 
| 4 | `/api/v2/open/{SYMBOL}` | Schema Test | 
| 5 | `/api/v2/close/{SYMBOL}` | Schema Test |  
| 6 | `/api/v2/high/{SYMBOL}` | Schema Test | 
| 7 | `/api/v2/low/{SYMBOL}` | Schema Test | 
| 8 | `/api/v2/high_low/{SYMBOL}` | Schema Test |
| 9 | `v1` and `v2` | One route of each `v`-type to test a missing API Key |
| 10 | `/api/v2/{YEAR}` | Incorrect year |
| 11 | `v1` and `v2` | One route of each `v`-type to test an _invalid_ API Key |

### Specifications:

- You do NOT need to use type hints for this project. If want to experiment with type hints on some functions that is totally fine. Your grade will not be affected if you have some functions with type hints and some functions without type hints. 
- Your documentation will be read over for grammar. Make sure that you are consistent in tense and usage. 
- All functions in your code need to have proper documentation. You need to make sure that your autodocs build is able to find all of the required files and processes them appropriately.

#### Updates to Make / Docker
- There are no changes to the Dockerfile, but there are two additional Make commands required.
- `make autodocs` should build and start the `mkdocs` server on port 4040 (externally). When `make autodocs` is running, it should be possible to go to the local server and see the autodocs server running.
- `make tests` should run the Python test suite as described above, reporting coverage using `pytest-cov`.


### Logging

- If you have not already done so, please remove all print statements and add logging instead. 
  
- Update all logs to use a custom logger. As in the demonstration in class, the log format should be `log_format = "%(asctime)s | %(levelname)s | %(message)s"`.
- The log specification is as follows:

| System | Level | Description | 
| --- | --- | --- | 
| All `manage_db` commands | INFO | <ul><li>When a command starts (and which command)</li><li>When a command ends (and how long it took)</li></ul> | 
| `manage_db` loading commands | DEBUG | <ul><li>As each year and market is loaded, log the time it took to load that year and market</li></ul> | 
| `manage_db` table creation commands | DEBUG | <ul><li>Notification that the table was created (with its name)</li></ul> | 
| All routes | DEBUG | <ul><li>Time it took to respond to the route</li><li>The body, header, and route</li><li>The response</li></ul> | 
| All routes | INFO | <ul><li>All non-2xx responses (e.g., 500, 404)</li></ul>| 
| All routes | WARN | <ul><li>Any time the incorrect (or no) API key is provided</li></ul> | 

- All logs should contain specific and useful information regarding the process, written in a professional manner. 
- No other `print` statements should exist. If there are additional things you want to report, please use an appropriate log command.
- You do not need to override the Werkzeug library logging if you do not wish to. 


#### Additional details

- Please make sure to go back to the original specification for the entire API. As part of the review, another look at all of these will be completed.
- You are welcome to add any additional tests, just make sure that the 12 tests above follow the standards previously defined.
- **Make sure that your database is not in the repository.** The database needs to be generated by the user.

### Additional Fixes

Please correct all of the feedback for Part V. A portion of the grade will be set to making sure that your code continues to pass the standards set by Part V.

## How will this be graded

- We will check out the code at the commit hash that you submit.
- All of the previous coding standards will be checked, and all of the previous APIs (`v1`, `v2`, `v3`, and `v4`) will also be tested.
- We will run `ruff`, using the [`pyproject.toml`](pyproject.toml) file here to make sure that your code conforms to the standards therein.
- We will also verify that the `.pre-commit-config.yaml` is in the repo and able to be installed and used.
- We will run the `make` commands outlined above and verify that they work according to the standards set out above.
- We will run an autograder on the endpoints to make sure that they return the correct data and information. This includes types and casing.
- Your code will also be read over to make sure that it conforms to the standards laid out in class. If you want to receive full credit, make sure that your code has sound logic, is easy to read, maintains a good separation of concerns, and does not violate the DRY principle.
- Finally, your code will also be read to make sure that all documentation is up to date and that the code has a consistent set of abstraction standards.
- There should be no `print` statements. Everything should be logged with an _appropriate_ level.
- All documented code needs to have good faith level of effort that briefly explains the required purpose. Doc strings that say `This is the doc string` or other low-effort submissions will be graded accordingly.
- Your code should also be responsive to changes requested by previous submissions. If you received feedback previously to make a change to the code this change should be present.
- No errors or warnings should occur in normal operations.
- Extraneous code, such as that generated by an LLM doing nothing, will be heavily penalized. 
- The database file itself should not be committed to the repo.
- You should never load the entire dataset into a DataFrame. You need to use SQL commands to select only the relevant data. No pandas based SQL commands are to be used. 
