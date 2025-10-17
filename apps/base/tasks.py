from celery import shared_task


@shared_task
def notify_user(call_id):
    # Logic to notify user about the call
    print(f"Notify user about call with ID: {call_id}")
