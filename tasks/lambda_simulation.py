import os
import logging

logging.basicConfig(level=logging.INFO)

def send_task_completion_notification(task_id, task_title):
    """Simulate AWS Lambda notification for completed tasks."""
    aws_service = os.getenv("AWS_SERVICE", "Simulated Lambda")  # Defaults to 'Simulated Lambda'
    notification_message = (
        f"[{aws_service}] Task ID {task_id} titled '{task_title}' has been marked as completed."
    )
    logging.info(notification_message)
