# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- A converter to YOLO format
- Installation guide
- Linear interpolation for a single point
- Video frame filter

### Changed
- Outside and keyframe buttons in the side panel for all interpolation shapes (they were only for boxes before)

### Deprecated
-

### Removed
-

### Fixed
- Fixed incorrect width of shapes borders in some cases
- Fixed annotation parser for tracks with a start frame less than the first segment frame
- Fixed interpolation on the server near outside frames

### Security
-

## [0.4.2] - 2019-06-03
### Fixed
- Fixed interaction with the server share in the auto annotation plugin

## [0.4.1] - 2019-05-14
### Fixed
- JavaScript syntax incompatibility with Google Chrome versions less than 72

## [0.4.0] - 2019-05-04
### Added
- OpenVINO auto annotation: it is possible to upload a custom model and annotate images automatically.
- Ability to rotate images/video in the client part (Ctrl+R, Shift+Ctrl+R shortcuts) (#305)
- The ReID application for automatic bounding box merging has been added (#299)
- Keyboard shortcuts to switch next/previous default shape type (box, polygon etc) [Alt + <, Alt + >] (#316)
- Converter for VOC now supports interpolation tracks
- REST API (/api/v1/*, /api/docs)
- Semi-automatic semantic segmentation with the [Deep Extreme Cut](http://www.vision.ee.ethz.ch/~cvlsegmentation/dextr/) work

### Changed
- Propagation setup has been moved from settings to bottom player panel
- Additional events like "Debug Info" or "Fit Image" have been added for analitics
- Optional using LFS for git annotation storages (#314)

### Deprecated
- "Flip images" flag in the create task dialog will be removed. Rotation functionality in client part have been added instead.

### Removed
-

### Fixed
- Django 2.1.5 (security fix, https://nvd.nist.gov/vuln/detail/CVE-2019-3498)
- Several scenarious which cause code 400 after undo/redo/save have been fixed (#315)

## [0.3.0] - 2018-12-29
### Added
- Ability to copy Object URL and Frame URL via object context menu and player context menu respectively.
- Ability to change opacity for selected shape with help "Selected Fill Opacity" slider.
- Ability to remove polyshapes points by double click.
- Ability to draw/change polyshapes (except for points) by slip method. Just press ENTER and moving a cursor.
- Ability to switch lock/hide properties via label UI element (in right menu) for all objects with same label.
- Shortcuts for outside/keyframe properties
- Support of Intel OpenVINO for accelerated model inference
- Tensorflow annotation now works without CUDA. It can use CPU only. OpenVINO and CUDA are supported optionally.
- Incremental saving of annotations.
- Tutorial for using polygons (screencast)
- Silk profiler to improve development process
- Admin panel can be used to edit labels and attributes for annotation tasks
- Analytics component to manage a data annotation team, monitor exceptions, collect client and server logs
- Changeable job and task statuses (annotation, validation, completed). A job status can be changed manually, a task status is computed automatically based on job statuses (#153)
- Backlink to a task from its job annotation view (#156)
- Buttons lock/hide for labels. They work for all objects with the same label on a current frame (#116)

### Changed
- Polyshape editing method has been improved. You can redraw part of shape instead of points cloning.
- Unified shortcut (Esc) for close any mode instead of different shortcuts (Alt+N, Alt+G, Alt+M etc.).
- Dump file contains information about data source (e.g. video name, archive name, ...)
- Update requests library due to https://nvd.nist.gov/vuln/detail/CVE-2018-18074
- Per task/job permissions to create/access/change/delete tasks and annotations
- Documentation was improved
- Timeout for creating tasks was increased (from 1h to 4h) (#136)
- Drawing has become more convenience. Now it is possible to draw outside an image. Shapes will be automatically truncated after drawing process (#202)

### Fixed
- Performance bottleneck has been fixed during you create new objects (draw, copy, merge etc).
- Label UI elements aren't updated after changelabel.
- Attribute annotation mode can use invalid shape position after resize or move shapes.
- Labels order is preserved now (#242)
- Uploading large XML files (#123)
- Django vulnerability (#121)
- Grammatical cleanup of README.md (#107)
- Dashboard loading has been accelerated (#156)
- Text drawing outside of a frame in some cases (#202)

## [0.2.0] - 2018-09-28
### Added
- New annotation shapes: polygons, polylines, points
- Undo/redo feature
- Grid to estimate size of objects
- Context menu for shapes
- A converter to PASCAL VOC format
- A converter to MS COCO format
- A converter to mask format
- License header for most of all files
- .gitattribute to avoid problems with bash scripts inside a container
- CHANGELOG.md itself
- Drawing size of a bounding box during resize
- Color by instance, group, label
- Group objects
- Object propagation on next frames
- Full screen view

### Changed
- Documentation, screencasts, the primary screenshot
- Content-type for save_job request is application/json

### Fixed
- Player navigation if the browser's window is scrolled
- Filter doesn't support dash (-)
- Several memory leaks
- Inconsistent extensions between filenames in an annotation file and real filenames

## [0.1.2] - 2018-08-07
### Added
- 7z archive support when creating a task
- .vscode/launch.json file for developing with VS code

### Fixed
- #14: docker-compose down command as written in the readme does not remove volumes
- #15: all checkboxes in temporary attributes are checked when reopening job after saving the job
- #18: extend CONTRIBUTING.md
- #19: using the same attribute for label twice -> stuck

### Changed
- More strict verification for labels with attributes

## [0.1.1] - 2018-07-6
### Added
- Links on a screenshot, documentation, screencasts into README.md
- CONTRIBUTORS.md

### Fixed
- GitHub documentation

## 0.1.0 - 2018-06-29
### Added
- Initial version

## Template
```
## [Unreleased]
### Added
-

### Changed
-

### Deprecated
-

### Removed
-

### Fixed
-

### Security
-
```
