# -*- coding: UTF-8 -*-

import csv
from fhir.resources.patient import Patient
from datetime import date, datetime
from fhir.resources.reference import Reference
from FilePath import *

from IsDirectory import isPATH
isPATH(patient_info_Patient_OUTPUT)

with open(patient_path, newline='') as csvfile:
    rows = csv.DictReader(csvfile)
    print("資料處理中....")
    for row in rows:
        # patient id
        patid = row["歸戶代號"]

        patmanagingOrganization = Reference.construct()
        patmanagingOrganization.id = row["院區"]
        # Hapi的資料ID不能只放數字，加一個h代表hospital
        patmanagingOrganization.reference = "Organization/h{}".format(
            row["院區"])
        patmanagingOrganization.type = "Organization"

        if row["性別"] == "M":
            patgender = "male"
        elif row["性別"] == "F":
            patgender = "female"

        birthdate = datetime.strptime(row["生日"], '%Y%m%d')
        patbirthdate = date(birthdate.year, birthdate.month, birthdate.day)

        pat = Patient.construct(
            id=patid, managingOrganization=patmanagingOrganization, gender=patgender, birthDate=patbirthdate)
        with open(patient_info_Patient_OUTPUT + "{}.json".format(patid), 'w') as outfile:
            outfile.write(Patient.json(pat))
    print("Completed!")
