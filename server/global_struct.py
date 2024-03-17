import threading
from threading import Lock

class Thread_struct:
    stop_generation = threading.Event()
    thread_pool_executor = None
    num_samples_generated = 0
    num_faults_generated = 0
    lock = Lock()
    mongo = None

