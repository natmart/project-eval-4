# pyshort

A simple URL shortener application built in Python.

## Features

- Create shortened URLs
- Redirect to original URLs
- Clean, simple API

## Installation

Run this to install in editable mode with development dependencies:

```bash
pip install -e ".[dev]"
```

## Usage

```python
from pyshort import create_short_url, get_long_url

# Create a short URL
short_url = create_short_url("https://example.com/very/long/url")

# Retrieve original URL
long_url = get_long_url(short_url)
```

## Testing

Run tests with pytest:

```bash
pytest
```

Run tests with coverage:

```bash
pytest --cov=pyshort
```

## Project Structure

```
.
├── pyshort/          # Main package
├── tests/            # Test suite
├── pyproject.toml    # Project configuration
└── README.md         # This file
```

## License

MIT