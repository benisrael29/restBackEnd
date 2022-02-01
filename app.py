from flask import Flask, request,render_template
import sys
import json
import opsgenie_sdk
app = Flask(__name__)
opsgenie_api_key = '8fedb235-e7c0-4e2a-907f-05ef3dff1d01' #your teams opsgenie key

ls = []
container_logs = {
    "am-usage" : {},
    "insights-logs-appservicehttplogs" : {},
    "insights-metrics-pt1m": {}
}


"""
Opsgenie handles alerts and routes them to the right team. Routing and alerts are configured through the webapp.
Config the api_key for your team, here. This api can create, delete, and change alerts. Only create function is defined here.  
"""
class opsgenieConfig:
    def __init__(self, opsgenie_api_key):
        self.conf = self.conf = opsgenie_sdk.configuration.Configuration()
        self.conf.api_key['Authorization'] = opsgenie_api_key 

        self.api_client = opsgenie_sdk.api_client.ApiClient(configuration=self.conf)
        self.alert_api = opsgenie_sdk.AlertApi(api_client=self.api_client)

    def create(self, description, meteric, value, priority_code):
        body = opsgenie_sdk.CreateAlertPayload(
        message= 'Anomaly Detected in Web App {}:{}'.format(meteric,value),
        alias='python_sample', #nneds to be unique unless you are overwriting
        description= description,
        responders=[{
            'name': 'SampleTeam',
            'type': 'team'
        }],
        visible_to=[
        {'name': 'Sample',
        'type': 'team'}],
        actions=['Restart', 'AnExampleAction'],
        tags=['OverwriteQuietHours'],
        details={'key1': 'value1',
                'key2': 'value2'},
        entity='An example entity',
        priority=priority_code)
        
        try:
            create_response = self.alert_api.create_alert(create_alert_payload=body)
            print(create_response)
            return create_response
        except opsgenie_sdk.ApiException as err:
            print("Exception when calling AlertApi->create_alert: %s\n" % err)

@app.route('/', methods = ["POST","GET"])

@app.route('/main',methods = ["POST","GET"])
def getMain():
    x = None

    if request.method == 'POST':
        x = request.data.decode("utf-8") # gets data then goes from bytes to string
        x = json.loads(x)
        container_logs[x["name"]] = x["data"]
        
        anomalies_csbytes = x["insights-logs-appservicehttplogs"][0]["anomalies"]["anomalies"] #Csbytes
        anomalies_Scbytes = x["insights-logs-appservicehttplogs"][1]["anomalies"]["anomalies"] #ScStatus
        anomalies_timeTaken = x["insights-logs-appservicehttplogs"][2]["anomalies"]["anomalies"] #TimeTaken

        if anomalies_csbytes:
            value = x["insights-logs-appservicehttplogs"][0]["anomalies"]["anomalies"][0] #Csbytes
            createAlert("insights-logs-appservicehttplogs", "CsBytes", value, "P3")
        
        if anomalies_Scbytes:
            value = x["insights-logs-appservicehttplogs"][0]["anomalies"]["anomalies"][0] #Csbytes
            createAlert("insights-logs-appservicehttplogs", "ScBytes", value, "P2")

        if anomalies_timeTaken:            
            value = x["insights-logs-appservicehttplogs"][0]["anomalies"]["anomalies"][0] #Csbytes
            createAlert ("insights-logs-appservicehttplogs", "Time Taken", value, "P1")

    return ('Rest API')

def createAlert(description, meteric, value, priority):
    the_genie = opsgenieConfig(opsgenie_api_key)
    the_genie.create(description, meteric, value, priority)

