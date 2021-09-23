#! /usr/bin/env python3
# coding: utf-8
###############################################################################
# FILE     : cache.py
# SYNOPSIS : Utilities for caches.
# LICENSE  : MIT
###############################################################################


###############################################################################
# IMPORTS
###############################################################################

import collections
import hashlib
import logging
import os

from PIL import Image
from concurrent import futures
from pathlib import Path
from tqdm import tqdm

import settings


###############################################################################
# CONSTANTS
###############################################################################

IMAGES_GLOB_PREFIX = '**/*.'


###############################################################################
# CLASSES
###############################################################################

ImageCacheData = collections.namedtuple(
    'ImageCacheData',
    [
        'cache_file',
        'size',
        'width',
        'height',
        'mtime'
    ]
)


ImageData = collections.namedtuple(
    'ImageData',
    [
        'image_file',
        'cache_file',
        'size',
        'width',
        'height',
        'mtime'
    ]
)


ImageFileMapping = collections.namedtuple(
    'FileMapping',
    [
        'image_file_name',
        'cache_image_file_name'
    ]
)


class ImageFileCache:
    """
    Represents cached information concerning image files.
    """

    def __init__(self, db_file, cache_dir, image_dir, image_type):
        """
        Parameters
        ----------
        db_file : str
            Canonical path for file to store all cache information
        cache_dir : str
            POSIX form of canonical path to the cache directory
        image_dir : str
            POSIX form of canonical path of the root images file directory
        image_type : str
            File extension for the type of image to consider
        """

        logger = logging.getLogger(__name__)
        logger.debug(
            f"  Enter ImageFileCache.__init__({self}, "
            f"'{db_file}', "
            f"'{cache_dir}', "
            f"'{image_dir}', "
            f"'{image_type}')"
        )
        cache = {}
        if Path(db_file).is_file():
            with open(db_file, 'r', encoding='utf-8') as f:
                for line in f:
                    (
                        filename,
                        cached_file,
                        size,
                        width,
                        height,
                        mtime
                    ) = line.strip().split('|')
                    cache[filename] = ImageCacheData(
                        cached_file,
                        int(size),
                        int(width),
                        int(height),
                        float(mtime)
                    )
        logger.debug(f"    Cache read from database '{db_file}' = {cache}")

        data = []
        cache_misses = []
        for entry in Path(image_dir).glob(IMAGES_GLOB_PREFIX + image_type):
            image = entry.as_posix()
            if image.startswith(cache_dir):
                continue
            image_file_stat = entry.stat()
            image_mtime = image_file_stat.st_mtime
            anomaly = False
            code = hashlib.sha3_224()
            code.update(bytes(image, 'utf-8', 'ignore'))
            cache_image_file = (
                f"{cache_dir}"
                f"{code.hexdigest()}"
                f"{settings.CACHE_FILE_EXTENSION}"
            )
            if image in cache:
                cache_image_info = cache[image]
                if not Path(cache_image_file).is_file():
                    anomaly = True
                    logger.warning(
                        f"    No cache file '{cache_image_file}' for image "
                        f"'{image}' !"
                    )
                elif image_mtime > cache_image_info.mtime:
                    anomaly = True
                    logger.warning(
                        f"    Image '{image}' has mtime {image_mtime} but is "
                        f"recorded with mtime {cache_image_info.mtime} !"
                    )
            else:
                anomaly = True

            if anomaly:
                cache_misses.append(ImageFileMapping(image, cache_image_file))
                width, height = Image.open(image).size
                cache[image] = ImageCacheData(
                    cache_image_file,
                    image_file_stat.st_size,
                    width,
                    height,
                    image_mtime
                )
            icd = cache[image]
            data.append(
                ImageData(
                    image,
                    icd.cache_file,
                    icd.size,
                    icd.width,
                    icd.height,
                    icd.mtime
                )
            )

        if cache_misses:
            logger.debug(f"    Cache misses = {cache_misses}")
            if not Path(cache_dir).is_dir():
                Path(cache_dir).mkdir(parents=True)
            tasks_left = len(cache_misses)
            cpus = os.cpu_count()
            slice_start = 0
            progress = tqdm(
                total=tasks_left,
                position=0,
                leave=True,
                desc='Creating cache'
            )
            while tasks_left > 0:
                workers = min(cpus, tasks_left)
                slice_end = slice_start + workers
                with futures.ThreadPoolExecutor(workers) as executor:
                    result = executor.map(
                        make_cache_image_file,
                        cache_misses[slice_start:slice_end:]
                    )
                progress.update(len(list(result)))
                slice_start = slice_end
                tasks_left -= workers

            p = Path(db_file).parent
            if not p.is_dir():
                p.mkdir(parents=True)
            with open(db_file, 'w', encoding='utf-8') as f:
                for k, v in cache.items():
                    print(
                        k,
                        v.cache_file,
                        v.size,
                        v.width,
                        v.height,
                        v.mtime,
                        file=f,
                        sep='|'
                    )
            logger.debug(f"    Cache saved to database '{db_file}' = {cache}")

        self._data = data

        logger.debug(f"    Active images cache = {data}")
        logger.debug(f"  Leave ImageFileCache.__init__({self}, ...)")

    @property
    def data(self):
        return(self._data)


###############################################################################
# FUNCTIONS
###############################################################################

def make_cache_image_file(file_info):
    """
    Creates an icon using an ImageFileMapping object.

    Parameters
    ----------
    file_info : ImageFileMapping
        An image file name and the name of the cache file to make from it
    """

    with Image.open(file_info.image_file_name).convert('RGB') as image:
        image.thumbnail((settings.ICON_WIDTH, settings.ICON_HEIGHT))
        image.save(file_info.cache_image_file_name)

    return(True)


###############################################################################
# END
###############################################################################
# Local variables:
# mode: python
# End:
