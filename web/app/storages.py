import os
from abc import ABC, abstractmethod
import logging

from fastapi import UploadFile
from imghdr import what
from uuid import uuid4

from app.config import settings


class BaseStorage(ABC):
    @staticmethod
    def generate_file_name(file_extension: str):
        return f'{uuid4()}.{file_extension}'

    @staticmethod
    async def is_image(file):
        header = await file.read(512)
        await file.seek(0)
        return what(None, header) is not None

    @abstractmethod
    async def upload_user_image(self, *, file: UploadFile) -> str | None:
        pass

    async def delete_user_image(self, *, file_name: str) -> bool:
        pass


class LocalStorage(BaseStorage):
    """
    Local storage for API.
    """
    

    async def upload_user_image(self, *, file: UploadFile) -> str | None:
        """
        Upload an image to user images directory.
        Return file name if success, None in case of error.
        """
        try:
            if not await self.is_image(file):
                return False
            file_name = self.generate_file_name(file.filename.split('.')[-1])
            file_content = await file.read()
            file_path = os.path.join(settings.MEDIA_DIR, settings.USER_IMAGES_FOLDER, file_name)
            with open(file_path, 'wb') as new_file:
                new_file.write(file_content)
            return file_name
        except Exception as err:
            logging.error(f'Error uploading file: {err} in {self.__class__.__name__}')
            return None

    async def delete_user_image(self, *, file_name: str) -> bool:
        """
        Delete an image from user images directory.
        """
        try:
            os.remove(os.path.join(settings.MEDIA_DIR, settings.USER_IMAGES_FOLDER, file_name))
            return True
        except Exception as err:
            logging.error(f'Error deleting file: {err} in {self.__class__.__name__}')
            return False


local_storage = LocalStorage()
