import uuid

import numpy as np

from fedasync.commons.conf import Config
from fedasync.server.strategies.AsyncFL import AsyncFL

from fedasync.server.worker_manager import WorkerManager

from fedasync.server.objects.worker import Worker

strat = AsyncFL()
strat.current_version = 1
Config.TMP_LOCAL_MODEL_FOLDER = './'
worker_manager = WorkerManager()
for i in range(2):
    worker = Worker("worker" + str(i), "", "")
    worker.weight_file = "weights.npy"
    worker.alpha = 1
    worker.uuid = str(uuid.uuid4())
    worker.current_version = 1
    worker_manager.add_worker(worker)
    worker_manager.worker_update_queue[worker.uuid] = worker

# test strat.aggregate function
strat.aggregate(worker_manager.worker_pool, worker_manager.worker_update_queue)