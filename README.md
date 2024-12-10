Installing dependencies:

	pip install -r requirements.txt


Subdomain enumeration:

    Finds and identifies subdomains of a target domain using a wordlist.
    Checks if subdomains are active (responding to a DNS query).
    Saves results to an SQLite database.

Listing directories:

    Searches and identifies directories available on a target website via HTTP requests.
    Uses a wordlist to test for common directory names.
    Saves valid directories to an SQLite database.

Storage of results:

    Data from domains, subdomains and directories is saved in a local SQLite database (default.db) for future reference or reuse.

Command line options:

    --sub: Starts subdomain enumeration.
    --dir: Starts listing directories.
    --verbose: Verbose mode to display additional details during execution.
    --delete: Deletes the existing database.
    -h or --help: Displays a detailed user guide.

