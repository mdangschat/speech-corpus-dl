"""Storage helper methods."""

import hashlib
import os
import shutil
import tarfile
import time


def delete_file_if_exists(path):
    """Delete the file for the given path, if it exists.

    Args:
        path (str): File path.

    Returns:
        Nothing.
    """
    if os.path.exists(path) and os.path.isfile(path):
        for i in range(5):
            try:
                os.remove(path)
                break
            except (OSError, ValueError) as exception:
                print('WARN: Error deleting ({}/5) file: {}'.format(i, path))
                if i == 4:
                    raise RuntimeError(path) from exception
                time.sleep(1)


def delete_directory_if_exists(path):
    """Recursive removal of a folder and all contained files.

    Args:
        path (str):  Directory path.

    Returns:
        Nothing.
    """

    if os.path.exists(path) and os.path.isdir(path):
        # https://docs.python.org/3/library/shutil.html#shutil.rmtree
        # Doesn't state which errors are possible.
        try:
            shutil.rmtree(path)
        except OSError as exception:
            raise exception


def md5(file_path):
    """Calculate the md5 checksum of files that do not fit in memory.

    Args:
        file_path (str): Path to file.

    Returns:
        str: md5 checksum.
    """
    hash_md5 = hashlib.md5()
    with open(file_path, 'rb') as file_handle:
        for chunk in iter(lambda: file_handle.read(4096), b''):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def makedirs(dirs):
    """Create a given directory or a list of directories, including required subdirectories.

    Args:
        dirs: String or list of strings.

    Returns:
        Nothing.
    """
    if isinstance(dirs, str):
        dirs = [dirs]

    for _dir in dirs:
        if not os.path.exists(_dir):
            os.makedirs(_dir, exist_ok=True)


def tar_extract_all(tar_path, target_path):
    """Extract a TAR archive. Overrides existing files.

    Args:
        tar_path (str): Path of TAR archive.
        target_path (str): Where to extract the archive.

    Returns:
        Nothing.
    """
    assert os.path.exists(target_path) and os.path.isdir(target_path), 'target_path does not exist.'
    with tarfile.open(tar_path, 'r') as tar:
        for file_ in tar:
            try:
                tar.extract(file_, path=target_path)
            except IOError:
                os.remove(os.path.join(target_path, file_.name))
                tar.extract(file_, path=target_path)
            finally:
                os.chmod(os.path.join(target_path, file_.name), file_.mode)
