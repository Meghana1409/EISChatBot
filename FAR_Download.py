import os
import pandas as pd
import pymysql
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE','PyPortal.settings')
django.setup()

from EISChatBot.models import FarDetailsAll
###### Fetching far data from portal in csv format #########
file_path="/var/www/cgi-bin/PyPortal/EISChatBot/FarDetails.csv"


#cmd = "curl -X POST -d \"user=eisadmin&pass=Password1@4&Order=ASC|ASC|ASC|ASC&OrderBy=id|||&Query=Queue+=+'Firewalls'+AND+CF.{RequesterDepartmentName}'+LIKE+'EIS'\" -k https://nspm.sbi/FireFlow/Search/Results.tsv -o " + file_path
cmd="curl -X POST -d \"user=eisadmin&pass=Password1@5&Order=ASC|ASC|ASC|ASC&OrderBy=id|||&Query=Queue+=+'Firewalls'+AND+'CF.{RequesterDepartmentName}'+LIKE+'EIS'\" -k https://nspm.sbi/FireFlow/Search/Results.tsv -o" + file_path
os.system(cmd)

print("file created")


####### accessing data and inserting in db table #####
df = pd.read_csv(file_path,sep="\t", low_memory=False)

columns_arr=["id","Subject","Status","Created","CF-Expires","CF-Requested Source","CF-Requested Destination","CF-Requested Service","CF-Requested Source NAT","CF-Requested Destination NAT","CF-Requested Port Translation","CF-Change Source","CF-Change Destination","CF-Change Service","CF-Change Source NAT","CF-Change Destination NAT","CF-Translated Destination","CF-Translated Service","CF-Dependentapplication","CF-Permanent Rule","CF-ZONE"]

filterd_df=df[~df['getParent'].isin(df['id'])|df['getParent'].isna()]

filterd_df=filterd_df.groupby('id',as_index=False).agg(lambda x: ','.join(set(x.dropna().astype(str))))

table_columns=["Far_Id","Subject","Status","Created","Expires","Requested_Source","Requested_Destination","Requested_Service","Requested_Source_NAT","Requested_Destination_NAT","Requested_Port_Translation","Change_Source","Change_Destination","Change_Service","Change_Source_NAT","Change_Destination_NAT","Translated_Destination","Translated_Service","Dependent_application","Permanent_Rule","ZONE"]

FarDetailsAll.objects.all().delete() # empty entire table

object_to_create=[]
for _,row in filterd_df.iterrows():
    data={ model_field: str(row[df_field]) for model_field,df_field in zip(table_columns,columns_arr)}
    object_to_create.append(FarDetailsAll(**data))

try:
    FarDetailsAll.objects.bulk_create(object_to_create)
except:
    print("ERROR")

print("details inserted")
