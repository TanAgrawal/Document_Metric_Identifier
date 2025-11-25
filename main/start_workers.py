import subprocess

def start_workers(num_workers=4):
    processes = []
    for i in range(1, num_workers + 1):
        name = f"worker{i}@%h"
        print(f"Starting Celery worker: {name}")
        p = subprocess.Popen([
            "celery",
            "-A", "app.cel",
            "worker",
            "--loglevel=INFO",
            "--pool=solo",   
            "-n", name
        ])
        processes.append(p)

    print(f"Started {num_workers} Celery workers.")
    print("Press Ctrl+C to stop all workers.")

    try:
        for p in processes:
            p.wait()
    except KeyboardInterrupt:
        print("Stopping workers...")
        for p in processes:
            p.terminate()

if __name__ == "__main__":
    start_workers(num_workers=4) 
