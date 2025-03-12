from django.core.management.base import BaseCommand
import threading
import time
import logging
from tasks.models import Task
from django.db import transaction

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Scaling Parameters
TASK_THRESHOLD = 10
MAX_WORKERS = 5
MIN_WORKERS = 1
TASK_CHECK_INTERVAL = 5

# Worker Management
active_workers = MIN_WORKERS
worker_threads = {}
worker_shutdown_flags = {}

def process_tasks(worker_id):
    """Worker logic for processing tasks"""
    global active_workers
    while not worker_shutdown_flags[worker_id]:
        with transaction.atomic():
            task = Task.objects.filter(status='pending').first()
            if not task:
                break  # 🚨 Break worker loop when no more pending tasks

            task.status = 'in_progress'
            task.save()
            logging.info(f"🛠️ Worker-{worker_id} started task ID: {task.id}")

        time.sleep(3)  # Simulate task processing time

        with transaction.atomic():
            task.status = 'completed'
            task.save()
            logging.info(f"✅ Worker-{worker_id} completed task ID: {task.id}")

    logging.info(f"🚫 Worker-{worker_id} has stopped.")

def scale_up():
    global active_workers
    if active_workers < MAX_WORKERS:
        worker_id = active_workers + 1
        worker_shutdown_flags[worker_id] = False
        thread = threading.Thread(target=process_tasks, args=(worker_id,), daemon=True)
        worker_threads[worker_id] = thread
        thread.start()

        active_workers += 1
        logging.info(f"🔼 Scaling UP: Now running {active_workers} worker(s).")

def scale_down():
    global active_workers
    if active_workers > MIN_WORKERS:
        worker_id = active_workers
        worker_shutdown_flags[worker_id] = True  # Signal worker to stop

        # Ensure worker thread exits before cleanup
        if worker_id in worker_threads:
            worker_threads[worker_id].join(timeout=2)
            del worker_threads[worker_id]  # Clean up thread reference
        
        del worker_shutdown_flags[worker_id]  # Clean up shutdown flag

        active_workers -= 1
        logging.info(f"🔽 Scaling DOWN: Now running {active_workers} worker(s).")

def check_task_volume():
    global active_workers

    while True:
        try:
            pending_tasks = Task.objects.filter(status='pending').count()
            logging.info(f"📋 Current pending tasks: {pending_tasks}")

            # 🚨 Immediate break condition when no pending tasks exist
            if pending_tasks == 0:
                logging.info("🚨 Immediate Scale-Down Trigger: No pending tasks found.")
                while active_workers > MIN_WORKERS:
                    scale_down()
                break  # 🚨 Exit loop after scaling down all remaining workers

            # Scale up logic
            if pending_tasks > active_workers * 2:
                scale_up()

        except Exception as e:
            logging.error(f"❌ Error while checking task volume: {e}")

        time.sleep(TASK_CHECK_INTERVAL)

class Command(BaseCommand):
    help = "Simulated auto-scaling logic for task management."

    def handle(self, *args, **kwargs):
        scaling_thread = threading.Thread(target=check_task_volume, daemon=True)
        scaling_thread.start()

        # Start initial worker(s)
        for worker_id in range(1, MIN_WORKERS + 1):
            worker_shutdown_flags[worker_id] = False
            thread = threading.Thread(target=process_tasks, args=(worker_id,), daemon=True)
            worker_threads[worker_id] = thread
            thread.start()

        logging.info("✅ Auto-scaling logic started successfully.")

        while threading.active_count() > 1:
            time.sleep(1)  # Keep the management command alive until all threads finish
