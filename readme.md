## Met Office to Influx
Downloads weather data from Met Office DataHub API (https://metoffice.apiconnect.ibmcloud.com/metoffice/production/) and inserts to InfluxDB

### Requirements
```sh
pip install -p requirements.txt
```

### Execution
```sh
python3 main.py
```

### Docker Compose
```sh
weatherscraper:
  image: ghcr.io/stuartgraham/metoffice2influx:latest
  restart: always
  container_name: metoffice2influx
  environment:
    - LIVE_CONN=True
    - API_CLIENT=SoMe-GuId
    - API_SECRET=SoMe-PaSsWoRd
    - INFLUX_HOST=influx.test.local
    - INFLUX_HOST_PORT=8086
    - INFLUX_DATABASE=weatherstats
    - LATITUDE=58.642334
    - LONGITUDE=-3.070539
    - RUNMINS=60
```

### Kubernetes CronJob
```sh
apiVersion: batch/v1
kind: CronJob
metadata:
  name: metoffice2influx
spec:
  schedule: '@hourly'
  successfulJobsHistoryLimit: 1
  failedJobsHistoryLimit: 0
  jobTemplate:
    spec:
      template:
        spec:
          containers:
            - name: metoffice2influx
              image: ghcr.io/stuartgraham/metoffice2influx:latest
              imagePullPolicy: IfNotPresent
              envFrom:
              - secretRef:
                  name: metoffice2influx
              env:
              - name: RUNMINS
                value: "0"
              - name: LATITUDE
                value: "58.642334"
              - name: LONGITUDE
                value: "-3.070539"
              - name: INFLUX_HOST
                value: weatherstats
              - name: INFLUX_HOST_PORT
                value: "8086"
              - name: INFLUX_ORG
                value: ORG
              - name: INFLUX_BUCKET
                value: BUCKET
              securityContext:
                allowPrivilegeEscalation: false
              resources:
                requests:
                  memory: 15Mi
                limits:
                  memory: 30Mi
          restartPolicy: Never
---
apiVersion: v1
kind: Secret
metadata:
  name: metoffice2influx
type: Opaque
data:
  API_CLIENT: base64 encoded metoffice client_id
  API_SECRET: base64 encoded metoffice client_secret
  INFLUX_TOKEN: base64 encoded influxdb2 token
```
