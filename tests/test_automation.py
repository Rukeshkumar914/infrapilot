import pytest

from infrapilot.automation import (
    create_directory,
    create_file,
    list_directory,
    move_path,
    get_path_info,
)


def test_create_directory(tmp_path):
    directory = tmp_path / "backup" / "logs"

    result = create_directory(directory)

    assert directory.exists()
    assert directory.is_dir()
    assert result["created"] is True
    assert result["type"] == "directory"


def test_create_existing_directory(tmp_path):
    directory = tmp_path / "backup"

    create_directory(directory)
    result = create_directory(directory)

    assert directory.exists()
    assert result["created"] is True


def test_create_file(tmp_path):
    file_path = tmp_path / "logs" / "app.log"

    result = create_file(file_path, "InfraPilot started")

    assert file_path.exists()
    assert file_path.read_text() == "InfraPilot started"
    assert result["created"] is True
    assert result["size_bytes"] == len("InfraPilot started")


def test_create_file_without_overwrite(tmp_path):
    file_path = tmp_path / "app.txt"
    file_path.write_text("Original content")

    with pytest.raises(FileExistsError):
        create_file(file_path, "New content")

    assert file_path.read_text() == "Original content"


def test_create_file_with_overwrite(tmp_path):
    file_path = tmp_path / "app.txt"
    file_path.write_text("Original content")

    create_file(file_path, "Updated content", overwrite=True)

    assert file_path.read_text() == "Updated content"


def test_list_directory(tmp_path):
    (tmp_path / "app.txt").write_text("Hello")
    (tmp_path / "backup").mkdir()

    result = list_directory(tmp_path)

    names = [item["name"] for item in result]

    assert "app.txt" in names
    assert "backup" in names


def test_list_directory_missing(tmp_path):
    with pytest.raises(FileNotFoundError):
        list_directory(tmp_path / "missing")


def test_list_directory_not_a_directory(tmp_path):
    file_path = tmp_path / "app.txt"
    file_path.write_text("Hello")

    with pytest.raises(NotADirectoryError):
        list_directory(file_path)


def test_move_file(tmp_path):
    source = tmp_path / "source.txt"
    destination = tmp_path / "backup" / "source.txt"

    source.write_text("Backup data")

    result = move_path(source, destination)

    assert not source.exists()
    assert destination.exists()
    assert destination.read_text() == "Backup data"
    assert result["moved"] is True


def test_move_missing_source(tmp_path):
    with pytest.raises(FileNotFoundError):
        move_path(
            tmp_path / "missing.txt",
            tmp_path / "destination.txt",
        )


def test_move_existing_destination_without_overwrite(tmp_path):
    source = tmp_path / "source.txt"
    destination = tmp_path / "destination.txt"

    source.write_text("Source")
    destination.write_text("Destination")

    with pytest.raises(FileExistsError):
        move_path(source, destination)

    assert source.exists()
    assert destination.read_text() == "Destination"


def test_get_path_info_file(tmp_path):
    file_path = tmp_path / "app.txt"
    file_path.write_text("InfraPilot")

    result = get_path_info(file_path)

    assert result["name"] == "app.txt"
    assert result["type"] == "file"
    assert result["size_bytes"] == len("InfraPilot")


def test_get_path_info_directory(tmp_path):
    directory = tmp_path / "backup"
    directory.mkdir()

    result = get_path_info(directory)

    assert result["name"] == "backup"
    assert result["type"] == "directory"
    assert result["size_bytes"] is None


def test_get_path_info_missing(tmp_path):
    with pytest.raises(FileNotFoundError):
        get_path_info(tmp_path / "missing")
