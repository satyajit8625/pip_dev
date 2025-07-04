# Version Utils for Asset Management

This module provides utility functions for handling versioned asset file names, such as those used in animation, VFX, or game pipelines.

## Features
- Strip version suffix from file names (e.g., `char_v003` → `char`)
- Find the latest version number from a list of files
- Generate the next versioned file name automatically

## Usage

### Import
```python
from asset_maneger.publish_tool.core.version_utils import VersionUtils
```

### Strip Version Suffix
```python
name = VersionUtils.strip_version('char_v003')
print(name)  # Output: 'char'
```

### Find Latest Version
```python
files = ['char_v001.ma', 'char_v002.ma', 'char_v003.ma']
latest = VersionUtils.find_latest_version(files, 'char.ma')
print(latest)  # Output: 3
```

### Generate Next Versioned File Name
```python
files = ['char_v001.ma', 'char_v002.ma', 'char_v003.ma']
next_file = VersionUtils.update_version(files, 'char.ma')
print(next_file)  # Output: 'char_v004.ma'
```

## API

### VersionUtils.strip_version(name_part)
Removes a trailing version (e.g., `_v001`) from a file name part if present.

### VersionUtils.find_latest_version(file_list, base_file_name)
Finds the highest version number in a list of files matching the base file name pattern.

### VersionUtils.update_version(file_list, base_file_name)
Returns the next versioned file name based on the highest version found in the list.

## License
MIT License (or your preferred license)
