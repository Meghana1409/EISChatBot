from django.db import connections
import datetime
import re
import requests
import json
from dbOpTest.models import BrokerDetails,EGDetails,ServiceDetails,Schemas,ServerDetails,LayerDetails

def get_oracle_output(query):
    with connections['oracle'].cursor() as cursor:
        cursor.execute(query)
        result=cursor.fetchall()
        return result


def Hits(msg,hits_choice):
    if msg == "30 min":
        if hits_choice == "exp hits":
            query="select count(*) from EISAPP.api_log where  request_date_time >= sysdate-30/(24*60);"
        if hits_choice == "sys hits":
            query="select count(*) from EISAPP.backend_log where  request_date_time >= sysdate-30/(24*60);"
        '''if hits_choice == "port wise hits":
            query="select EXP_Port,count(1) from EISAPP.api_log where  request_date_time >= sysdate-30/(24*60) group by EXP_Port;"
        if hits_choice == "service wise hits":
            query="select API_Name,count(1) from EISAPP.api_log where  request_date_time >= sysdate-30/(24*60) group by API_Name;" '''
        returnstr="Total No. of Hits in last 30 Minutes : "
    elif msg == "1 hour":
        if hits_choice == "exp hits":
            query="select count(*) from EISAPP.api_log where  request_date_time >= sysdate-60/(24*60);"
        if hits_choice == "sys hits":
            query="select count(*) from EISAPP.backend_log where  request_date_time >= sysdate-60/(24*60);"
        '''if hits_choice == "port wise hits":
            query="select EXP_Port,count(1) from EISAPP.api_log where  request_date_time >= sysdate-60/(24*60) group by EXP_Port;"
        if hits_choice == "service wise hits":
            query="select API_Name,count(1) from EISAPP.api_log where  request_date_time >= sysdate-60/(24*60) group by API_Name;"'''
        returnstr="Total No. of Hits in last 1 Hour : "
    else:
        if hits_choice == "exp hits":
            query="select count(*) from EISAPP.api_log where TRUNC(REQUEST_DATE_TIME)=TRUNC(SYSDATE) "
        if hits_choice == "sys hits":
            query="select count(1) from EISAPP.backend_log where TRUNC(REQUEST_DATE_TIME)=TRUNC(SYSDATE) "
        '''if hits_choice == "port wise hits":
            query="select EXP_Port,count(1) from EISAPP.api_log where TRUNC(REQUEST_DATE_TIME)=TRUNC(SYSDATE) group by EXP_Port;"
        if hits_choice == "service wise hits":
            query="select API_Name,count(1) from EISAPP.api_log where TRUNC(REQUEST_DATE_TIME)=TRUNC(SYSDATE) group by API_Name;"'''
        returnstr="Total No. of Hits today Till now : "
    tables = get_oracle_output(query)
    return returnstr+str(tables[0][0])

def get_tables(request,refnum):
    result=[]
    query=f"select AL.RESPONSE_STATUS,AL.URN,AL.ORCH,OAL.URN_CHILD,AL.ERROR_CODE,AL.ERROR_DESCRIPTION,OAL.ERROR_CODE as orch_ERROR_CODE,OAL.ERROR_DESCRIPTION as orch_ERROR_DESCRIPTION,AL.EXP_PORT,AL.BROKER_EG ,AL.EXP_IP,OAL.API_NAME,OAL.URL,BL.END_POINT_URL,BL.END_POINT_PORT,BL.TXN_ENDPOINT, BL.request_date_time,BL.response_date_time ,to_char(BL.response_date_time - BL.request_date_time ) AS Difference_in_request_response_time,AD.EXCEPTION_DESC,AD.INPUT_DATA As api_details_input,OAD.INPUT_DATA as orch_api_input,AD.OUTPUT_DATA AS API_output_data,OAD.OUTPUT_DATA as orch_output_data  FROM EISAPP.api_log AL left JOIN EISAPP.api_details AD ON AL.URN = AD.URN LEFT JOIN EISAPP.orch_api_log OAL ON AL.urn = OAL.URN  LEFT JOIN EISAPP.orch_api_details OAD ON ( AL.ORCH = 'Y' and  OAL.URN_CHILD = OAD.URN_child ) or (AL.ORCH = 'N' and OAL.URN = OAD.URN) LEFT JOIN EISAPP.backend_log BL ON (CASE  WHEN AL.ORCH = 'Y' THEN OAL.URN_CHILD  ELSE AL.URN END) = BL.URN LEFT JOIN EISAPP.backend_details BD ON (CASE  WHEN AL.ORCH = 'Y' THEN OAL.URN_CHILD ELSE AL.URN  END) = BD.URN WHERE AL.URN= '{refnum}'"
    tables = get_oracle_output(query)
    for i in range(len(tables)):
        i_list=list(tables[i])
        i_list[16]=i_list[16].strftime('%Y-%m-%d %H:%M:%S.%f')
        i_list[17]=i_list[17].strftime('%Y-%m-%d %H:%M:%S.%f')
        tables[i]=i_list
    result=[i for i in tables ]
    if(len(result) > 0):
        return result
    else:
        return "No Transactions found for this reference number "

def tables(request,refnum):
    #5 chars 20 nums
    refnum=refnum.upper()
    ref_num_arr=refnum.split(" ")
    result=""
    for i in ref_num_arr:
        if(len(i) == 25 and re.match(r"^[A-Z]{5}\d+$", i) ):
            table=get_tables(request,i)
            break
        else:
            table= "enter valid REFERENCE Number"

    return table


def Cache_Info(msg,value=""):
    if value:

        #result= get_oracle_output("select FIELD_NAME,FIELD_VALUE,SERVICE_NAME from EISAPP.cache_details where field_name = \'{value}\' or field_name like \'%{value}\' or field_name like \'{value}%\' or field_name like \'%{value}%\';")
        result= get_oracle_output(f"select FIELD_NAME,FIELD_VALUE,SERVICE_NAME from EISAPP.cache_details where field_name = '{value}' ;")
        #return result
        len_res=len(result)
        if(len_res > 0):
            if(len_res == 1):
                result=list(result[0])
                return f"\n\n<b>Field Name</b>: \"{result[0]}\" \n<b> Field_Value</b>: \"{result[1]}\" \n<b> Service Name</b>: \"{result[2]}\""
            else:
                output="Found Multiple Entries In DB"
                result_mult=[list(i) for i in result]
                for i in result_mult:
                    output+=f"\n\n<b>Field Name:</b> \"{i[0]}\n\" <b>Field_Value:</b> \"{i[1]}\" \nfor <b>Service Name:</b> \"{i[2]}\""

                return output
        else:
            return "\n\n<b>Field Name</b> is not Present In DB"
    else :
        #print("msg",msg)
        result= get_oracle_output("select count(*) from EISAPP.cache_details;")
        #print(result)
        return f"Total Cache fields present in DB are : <b>{list(result[0])[0]}</b>"
        #return result

def Server_Conf(ip):
    url = 'https://10.191.171.12:5443/PyPortal/EISHome/getComplianceByIp/'
    myobj = {'ipAddress': ip}
    x = requests.post(url, json = myobj,verify=False).text
    result=json.loads(x)["ComplianceDetails"]
    if len(result) > 0:
        filesystem=result[0]["fileSystem"]
        if filesystem == "OK":
            filesystem="Below Threshold"
        return f" Memory Utilisation: {result[0]['memory']} %  CPU Utilisation: {result[0]['cpu']} % \n Note: Below Information is updated on {result[0]['last_update']} \n Information for {result[0]['ip_address']} \n This is {result[0]['server_role']}  Server with OS Version {result[0]['osVersion']} \n fileSystem :{filesystem} \n UPTime : {result[0]['upTime']} \n RAM: {result[0]['ram']} \n CPU core:{result[0]['cpuCore']} \n Kernal Version : {result[0]['kernelVersion']}\n ACE Version : {result[0]['aceVersion']} \n MQ Version : {result[0]['mqVersion']} \n FIREWALL : {result[0]['firewall']} \n DSAgent : {result[0]['dsAgent']} \n SPLUNK : {result[0]['splunk']} \n RAgent : {result[0]['ragent']} \n eisuser Expiry : {result[0]['eisuserExpi']}\n root Expiry: {result[0]['socvaExpi']}\n addmitam Expiry: {result[0]['addmitamExpi']} "
    else:
        return "No server Found in my DB"

def workload(kwargs):
    print("in the workload")
    layer=set()
    server=set()
    eg=set()
    additional_instances=""
    thread_capacity=""
    threadInUse=""
    timeout=""
    service=""
    if(("service" in kwargs and "eg" in kwargs and "server" in kwargs) or ("service" in kwargs and "eg" in kwargs and "server" in kwargs and "layer" in kwargs) ):
        service=kwargs["service"]
        eg=kwargs["eg"]
        server=kwargs["server"]
        #layer=kwargs["layer"]
        serverdec = ServiceDetails.objects.filter(serviceName__startswith=kwargs["service"],eg__egName=kwargs["eg"],eg__broker__server__serverIP=kwargs["server"]).select_related('eg__broker__server__layer')
        if(len(serverdec) > 0):
            for s in serverdec:
                additional_instances=s.additionalInstances
                thread_capacity=s.threadCapicity
                threadInUse=s.threadInUse
                timeout=s.timeout
                service=s.serviceName
    elif("service" in kwargs and "eg" in kwargs):
        service=kwargs["service"]
        eg=kwargs["eg"]
        serverdec = ServiceDetails.objects.filter(serviceName__startswith=kwargs["service"],eg__egName=kwargs["eg"]).select_related('eg__broker__server__layer')
        if(len(serverdec) > 0):
            for s in serverdec:
                layer.add(s.eg.broker.server.layer.layer_name)
                server.add(s.eg.broker.server.serverIP)
                service=s.serviceName
        layer=list(layer)
        server=list(server)
    elif("service" in kwargs and "server" in kwargs):
        service=kwargs["service"]
        server=kwargs["server"]
        serverdec = ServiceDetails.objects.filter(serviceName__startswith=kwargs["service"],eg__broker__server__serverIP=kwargs["server"]).select_related('eg__broker__server__layer')
        if(len(serverdec) > 0):
            for s in serverdec:
                layer.add(s.eg.broker.server.layer.layer_name)
                eg.add(s.eg.egName)
                service=s.serviceName
        layer=list(layer)
        eg=list(eg)
    elif("service" in kwargs and "layer" in kwargs):
        service=kwargs["service"]
        layer=kwargs["layer"]
        serverdec = ServiceDetails.objects.filter(serviceName__startswith=kwargs["service"],eg__broker__server__layer__layer_name=kwargs["layer"]).select_related('eg__broker__server__layer')
        if(len(serverdec) > 0):
            for s in serverdec:
                server.add(s.eg.broker.server.serverIP)
                eg.add(s.eg.egName)
                service=s.serviceName
        server=list(server)
        eg=list(eg)
    elif ("service" in kwargs):
        service=kwargs["service"]
        serverdec = ServiceDetails.objects.filter(serviceName__startswith=kwargs["service"]).select_related('eg__broker__server__layer')
        if(len(serverdec) > 0):
            for s in serverdec:
                layer.add(s.eg.broker.server.layer.layer_name)
                server.add(s.eg.broker.server.serverIP)
                eg.add(s.eg.egName)
                service=s.serviceName
        layer=list(layer)
        server=list(server)
        eg=list(eg)
    else:
        service=""
        serverdec=""
        layer=list(layer)
        server=list(server)
        eg=list(eg)
    serverlen=len(serverdec)

    if serverlen == 1:
        return f"Layer: <b>{layer}</b>\n Server <b>{server}</b> has service <b>{service}</b> running in execution group <b>{eg}</b>,which is configured with following parameters: \n Additional Instances: <b>{additional_instances}</b>\n Thread Capacity: <b>{thread_capacity}</b> \n Threads In Use: <b>{threadInUse}</b>\n TimeOut: <b>{timeout}</b> "
    else:
        return {"service":service,"layer":layer,"server":server,"eg":eg}
    '''else:
        layer=list(layer)
        server=list(server)
        eg=list(eg)
        return {"layer":layer,"server":server,"eg":eg,"service":service}
    '''


def time_to_string(time_string):
    #time_string="+000000000 00:00:00.029356"
    time_string=time_string.split(" ")[-1]
    hh,mm,ss_ms=time_string.split(":")
    ss,ms=ss_ms.split(".")
    ms=ms[:3]
    time_parts=[]
    if hh!="00":
        time_parts.append(f"{int(hh)} hours")
    if mm!="00":
        time_parts.append(f"{int(mm)} minutes")
    if ss!="00":
        time_parts.append(f"{int(ss)} seconds")
    if ms!="00":
        time_parts.append(f"{int(ms)} microseconds")
    return " ".join(time_parts)
