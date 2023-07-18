from asynfed.commons.utils import AWSConnector
from asynfed.commons.utils import MinioConnector

from asynfed.commons.messages.server.server_response_to_init import StorageInfo


class ClientStorageAWS(AWSConnector):
    def __init__(self, config: StorageInfo, parent=None):
        # server pass client keys as in these variables
        config.access_key = config.client_access_key
        config.secret_key = config.client_secret_key
        super().__init__(config, parent)


class ClientStorageMinio(MinioConnector):
    def __init__(self, config: StorageInfo, parent=None):
        # server pass client keys as in these variables
        config.access_key = config.client_access_key
        config.secret_key = config.client_secret_key
        super().__init__(config, parent)