# NTIS-SOF

## Overview
 NTIS-SOF is a technical project for a command-line interface to with the Stack Overflow API. Allows users to fetch, bookmark, and manage user data efficiently.

## Major Libraries Used
- Click: Command-line interface creation
- Pydantic: Data validation and settings management
- SQLAlchemy: Database interactions
- Rich: Rich text and beautiful terminal formatting
- Requests: HTTP requests to the Stack Overflow API
- PyYAML: YAML configuration file parsing
- Redis: Caching and data storage
- Docker: Containerization for database and Redis

## Installation and Setup

### Prerequisites
- `Python` 3.12 or higher
- `Docker` and `Docker Compose`

### Steps
1. Clone the repository:
   ```
   git clone https://github.com/MeshalAl/NTIS-SOF.git
   ```
2. Navigate to the project directory:
   ```
   cd NTIS-SOF
   ```
3. Install required Python packages:
   ```
   pip install -r requirements.txt
   ```
4. Create or use the included  `.env` file.

    Create a `.env` file in the root directory with the following format:

    ```
    DATABASE_URL=postgresql://ntis:ntis@localhost:5432/ntis
    REDIS_HOST=localhost
    REDIS_PORT=6379
    ```

    Adjust these values according to your specific setup.

    Note: The included `.env` is using localhost defaults that are loadded by `Docker Compose`

4. Start Docker containers:
   ```
   docker compose up -d
   ```
5. run the CLI:
   ```
   python sofcli.py
   ```

For more information on setup options:
```
python sofcli.py --help
```

## Usage

### Basic Command Structure
```
python sofcli.py [OPTIONS] [COMMAND] [OPTIONS] [SUBCOMMAND] [OPTIONS]
```

For a list of all available commands:
```
python sofcli.py --help
```


## Main Commands

1. **fetch**: Retrieve user data from Stack Overflow API
   ```
   python sofcli.py fetch [SUBCOMMAND] [OPTIONS]
   ```
   Subcommands:
   1. **`users-by-id`**
      ```
      python sofcli.py fetch users-by-id [OPTIONS]
      ```
      Options:
      - `-dc, --display-columns TEXT`: Specify columns to display (can be used multiple times)
      - `-id, --user-id INTEGER`: Specify user IDs to fetch (can be used multiple times, required)

   2. **`users-bulk`**
      ```
      python sofcli.py fetch users-bulk [OPTIONS]
      ```
      Options:
      - `-p, --page INTEGER`: Page number to fetch (1-24, default: 1)
      
      **NOTE**: pages limited to 24 due to restriction by SOFAPI on public calls.

      - `-ps, --pagesize INTEGER`: Number of users to fetch per page (default: 10)
      - `-pr, --page-range INTEGER`: Number of pages to fetch (default: 1)
      - `--order [asc|desc]`: Order to apply (default: desc)
      - `--sort [creation|reputation|name]`: Sort to apply (default: creation)
      - `-dc, --display-columns TEXT`: Specify columns to display, use `users-bulk --help` for valid columns

   Global Options:
   - `--no-cache`: Disable caching

2. **`bookmark`**: Manage user bookmarks
   ```
   python sofcli.py bookmark [SUBCOMMAND] [OPTIONS]
   ```
   Subcommands:
   1. **`view`**
      ```
      python sofcli.py bookmark view [OPTIONS]
      ```
      Options:
      - `-ps, --page-size INTEGER`: Number of users to display per page (default: 10)
      - `-p, --page INTEGER`: Page number to display (default: 1)
      - `-dc, --display-columns TEXT`: Specify columns to display (can be used multiple times)
      - `-id, --user-ids INTEGER`: Specify user IDs to view (can be used multiple times)

   2. **`add`**
      ```
      python sofcli.py bookmark add [OPTIONS]
      ```
      Input: 

      Subcommand accepts data from `fetch` and `sof-file`, or can be used directly by adding `-id` option.

      Options:
      - `-id, --user-id INTEGER`: Specify user IDs to add (can be used multiple times)
    

   3. **remove**
      ```
      python sofcli.py bookmark remove [OPTIONS]
      ```
      input:

        Subcommand accepts data from `fetch` and `sof-file`, or can be used directly by adding `-id` option.
    
      Options:
      - `-id, --user-ids INTEGER`: Specify user IDs to remove (can be used multiple times)
      - `-a, --all`: Remove all bookmarks

3. **sof_file**: Manage SOF files for user data
   ```
   python sofcli.py sof_file [SUBCOMMAND] [OPTIONS]
   ```
   Subcommands:
   1. **`save`**
      ```
      python sofcli.py sof_file save [OPTIONS]
      ```
      input:

        Subcommand requires piped data from `fetch` command

      Options:
      - `-p, --path TEXT`: Absolute path to the .SOF file (optional)

   2. **`load`**
      ```
      python sofcli.py sof_file load [OPTIONS]
      ```
      Options:
      - `-p, --path TEXT`: Absolute path to the .SOF file (optional)
      - `-dc, --display-columns TEXT`: Specify columns to display (can be used multiple times)


### Examples

1. Fetch data for multiple users with specific display columns:
   ```
   python sofcli.py fetch -id 1234 -id 5678 -dc display_name -dc reputation
   ```

2. Add fetched users to bookmarks:
   ```
   python sofcli.py fetch -id 1234 -id 5678 | python sofcli.py bookmark add
   ```

3. Save fetched data to SOF file:
   ```
   python sofcli.py fetch -id 1234 -id 5678 -dc display_name -dc reputation | python sofcli.py sof_file save --path users.sofusers
   ```

4. Load SOF file and add users to bookmarks:
   ```
   python sofcli.py sof_file load --path users.sof | python sofcli.py bookmark add
   ```


## Features

- Interactive page navigation for fetch and bookmark view commands

- Caching system for improved performance

- API backoff timer to ensure compliance with Stack Overflow API usage limits

    ![alt text](./docs/images/interactive_api_view.gif)

- Data piping between commands:

    ![alt text](./docs/images/multi_pipes.gif)

  
- Customizable display columns for output

  ![alt text](./docs/images/fetch_options.gif)


# Configuration

The application uses defaults.yaml for most of its settings
YAML Configuration File (`config/defaults.yaml`)

## Configuration Precedence

1. Command-line options
3. YAML config file settings

# Possible Improvements:

1. Code reusability on some areas:
   - Implement shared utility functions for common operations across commands.

   - Create a base command class with common functionality for specific command classes to inherit from.

2. Unified methods:

   - Standardize option naming conventions across commands.

   - Create a unified approach for handling interactive table across different commands.

3. Error handling:
   - Implement a centralized error handling mechanism for consistent error messages and logging.

4. Testing:
   - Create unit and integration tests.

5. Documentation:
   - Generate automatic documentation from command help texts.

6. Caching strategy:
   - Refine the caching mechanism, possibly implementing a tiered strategy?

7. User experience:
   - Implement interactive prompts for complex operations.
   - Add progress bars for long-running operations.



## Data Schemas

This section describes the main data models used in the NTIS-SOF-API CLI application.

### SOFUser

Represents a [Stack Overflow User](https://api.stackexchange.com/docs/types/user) object

```python
class SOFUser(BaseModel):
    user_id: int
    account_id: int
    display_name: str
    user_age: int | None = None
    reputation: int
    location: str | None = None
    user_type: str
    last_access_date: int | None = None
    view_count: int | None = None
    question_count: int | None = None
    answer_count: int | None = None
    profile_image: str | None = None
```

### Bookmark

Extends SOFUser to include bookmark-specific fields.

```python
class Bookmark(SOFUser):
    created_at: datetime | None = Field(default_factory=datetime.now)
    updated_at: datetime | None = Field(default_factory=datetime.now)
```

### BookmarkDB

Represents a bookmark as stored in the database.

```python
class BookmarkDB(Bookmark):
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```

## File Handling Models

### SOFFile

Represents the piping structure of a .SOF file, containing user data and metadata.

```python
class SOFFile(BaseModel):
    users: list[SOFUser]
    meta: dict[str, Any]
```

## Configuration Models

### APIParams

Represents parameters for API requests.

```python
class APIParams(BaseModel):
    page: int = Field(..., ge=1)
    pagesize: int = Field(..., ge=1, le=100)
    order: str
    sort: str
    site: str
    filter: str
```

### byIDParams

Represents parameters for fetching users by ID.

```python
class byIDParams(BaseModel):
    filter: str
    site: str
```

### APIConfig

Represents the API configuration passed down the chain of commands

```python
class APIConfig(BaseModel):
    params: APIParams
    use_cache: bool
```

### RedisConfig

Represents the Redis configuration based on `defaults.yaml`

```python
class RedisConfig(BaseModel):
    decode_responses: bool
    cache_expire: int
```

### SOFConfig

Represents the SOF file handler configuration.

```python
class SOFConfig(BaseModel):
    default_path: str
```

### Config

Represents the overall application configuration.

```python
class Config(BaseModel):
    api: APIConfig
    redis: RedisConfig
    sof_handler: SOFConfig
```

These schemas define the structure of data used throughout the application, including user data, bookmarks, file formats, and various configuration settings. They use Pydantic models to ensure data validation and provide a clear structure for the application's data flow.


## Troubleshooting

If you encounter issues:
1. Ensure all prerequisites are installed correctly
2. Verify Docker containers are running: `docker compose ps`
3. Verify your `.env` values if not using defaults.


