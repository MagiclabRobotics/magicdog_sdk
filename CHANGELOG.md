
# Changelog
All significant changes will be documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and adheres to [Semantic Versioning](https://semver.org/).

## [v1.2.0] - 2025-11-03

**Corresponding Core Firmware Version: >= MagicDog 20251031**

### Added
- Added SLAM mapping and navigation interfaces;

### Changed
- Added more SDK log outputs;
- Optimized underlying topic communication logic;
- Added timeout parameter to some RPC interfaces;
- Updated `example` samples;

### Deprecated
- Removed the global `SetTimeout` interface;

## [v0.0.3-hotfix1] - 2025-11-03

**Corresponding Core Firmware Version: MagicDog 20250804**

### Fixed
- Fixed occasional data loss in subscribe data subscription;

### Changed
- Updated README instructions

## [v0.0.3] - 2025-09-17

**Corresponding Core Firmware Version: MagicDog 20250804**

### Added
- Project initialization and establishment of base directory structure
- Implemented and uploaded core functional modules, supporting C++ and Python
- Added basic test samples
- Added basic files including README, LICENSE, .gitignore, etc.