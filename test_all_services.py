# test_all_services.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sql_services.insert_datacenter import insert_datacenter
from sql_services.insert_metric_definition import insert_metric_definition
from sql_services.insert_file_upload_log import insert_file_upload_log

def run_tests():
    # Step 1: Insert a sample datacenter
    insert_datacenter(name="TestDC", location="London", provider="Azure")

    # Step 2: Insert a sample unified metric definition
    insert_metric_definition(
        unified_key="jrc.it.cpu.utilization",
        tags=["cpu", "utilization", "performance"],
        sources=["azure.vm.cpu", "naive.cpu", "row0.cpu_usage"]
    )

    # Step 3: Insert a sample upload log
    # Assume datacenter_id = 1 (you may need to check actual ID in your DB)
    insert_file_upload_log(
        filename="azure_metrics.json",
        datacenter_id=1,
        uploaded_by="admin_user"
    )

if __name__ == "__main__":
    run_tests()
