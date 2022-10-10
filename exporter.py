"""Application exporter"""

import os
import time
from prometheus_client import start_http_server, Gauge, Enum
import requests
import json
from intersight_auth import IntersightAuth


class AppMetrics:
    """
    Representation of Prometheus metrics and loop to fetch and transform
    application metrics into Prometheus metrics.
    """

    def __init__(self, polling_interval_seconds=60):
        self.polling_interval_seconds = polling_interval_seconds

        # Prometheus metrics to collect
        self.critical = Gauge("alarms_critical", "Critical Alarms")
        self.warning = Gauge("alarms_warning", "Warning Alarms")
        self.info = Gauge("alarms_info", "Info Alarms")
        self.cleared = Gauge("alarms_cleared", "Cleared Alarms")

    def run_metrics_loop(self):
        """Metrics fetching loop"""

        while True:
            self.fetch()
            time.sleep(self.polling_interval_seconds)

    def fetch(self):
        """
        Get metrics from application and refresh Prometheus metrics with
        new values.
        """
        # Update Prometheus metrics with application metrics
        AUTH = IntersightAuth(
            secret_key_filename='SecretKey.txt',
            api_key_id='xxxx/yyyy/zzzzz'
            )

        json_body = {
            "request_method": "GET",
            "resource_path": (
                    'https://intersight.com/api/v1/cond/Alarms?$apply=groupby((Severity),aggregate($count%20as%20count))'
            )
        }

        RESPONSE = requests.request(
            method=json_body['request_method'],
            url=json_body['resource_path'],
            auth=AUTH
        )

        recordCount = RESPONSE.json()["Results"]

        for r in recordCount:
            if(r["Severity"] == 'Critical'):
                self.critical.set(r["count"])
            if(r["Severity"] == 'Warning'):
                self.warning.set(r["count"])
            if(r["Severity"] == 'Info'):
                self.info.set(r["count"])
            if(r["Severity"] == 'Cleared'):
                self.cleared.set(r["count"])

def main():
    """Main entry point"""

    polling_interval_seconds = int(os.getenv("POLLING_INTERVAL_SECONDS", "600"))
    exporter_port = int(os.getenv("EXPORTER_PORT", "9877"))

    app_metrics = AppMetrics(polling_interval_seconds=polling_interval_seconds)

    start_http_server(exporter_port)
    app_metrics.run_metrics_loop()

if __name__ == "__main__":
    main()
