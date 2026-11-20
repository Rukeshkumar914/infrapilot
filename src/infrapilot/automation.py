from pathlib import Path
import shutil


def create_directory(path):
    """Create a directory, including missing parent directories."""
    directory = Path(path).expanduser()

    directory.mkdir(parents=True, exist_ok=True)

    return {
        "path": str(directory.resolve()),
        "created": True,
        "type": "directory",
    }


def create_file(path, content="", overwrite=False):
    """Create a file without overwriting existing data by default."""
    file_path = Path(path).expanduser()

    file_path.parent.mkdir(parents=True, exist_ok=True)

    if file_path.exists() and not overwrite:
        raise FileExistsError(
            f"File already exists: {file_path}"
        )

    mode = "w" if overwrite else "x"

    with file_path.open(mode, encoding="utf-8") as file:
        file.write(content)

    return {
        "path": str(file_path.resolve()),
        "created": True,
        "size_bytes": file_path.stat().st_size,
    }


def list_directory(path):
    """List files and directories with basic metadata."""
    directory = Path(path).expanduser()

    if not directory.exists():
        raise FileNotFoundError(
            f"Directory does not exist: {directory}"
        )

    if not directory.is_dir():
        raise NotADirectoryError(
            f"Not a directory: {directory}"
        )

    items = []

    for item in sorted(directory.iterdir()):
        items.append({
            "name": item.name,
            "path": str(item.resolve()),
            "type": "directory" if item.is_dir() else "file",
            "size_bytes": item.stat().st_size if item.is_file() else None,
        })

    return items


def move_path(source, destination, overwrite=False):
    """Move a file or directory safely."""
    source_path = Path(source).expanduser()
    destination_path = Path(destination).expanduser()

    if not source_path.exists():
        raise FileNotFoundError(
            f"Source does not exist: {source_path}"
        )

    if destination_path.exists() and not overwrite:
        raise FileExistsError(
            f"Destination already exists: {destination_path}"
        )

    if destination_path.exists() and overwrite:
        if destination_path.is_dir():
            shutil.rmtree(destination_path)
        else:
            destination_path.unlink()

    destination_path.parent.mkdir(parents=True, exist_ok=True)

    shutil.move(str(source_path), str(destination_path))

    return {
        "source": str(source_path.resolve()),
        "destination": str(destination_path.resolve()),
        "moved": True,
    }


def get_path_info(path):
    """Return information about a file or directory."""
    target = Path(path).expanduser()

    if not target.exists():
        raise FileNotFoundError(
            f"Path does not exist: {target}"
        )

    return {
        "name": target.name,
        "path": str(target.resolve()),
        "type": "directory" if target.is_dir() else "file",
        "size_bytes": target.stat().st_size if target.is_file() else None,
    }
