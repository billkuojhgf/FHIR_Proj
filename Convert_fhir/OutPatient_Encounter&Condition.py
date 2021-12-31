# -*- coding: UTF-8 -*-

import csv
import os
from fhir.resources.condition import Condition
from fhir.resources.encounter import Encounter
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coding import Coding
from fhir.resources.reference import Reference
from datetime import datetime
from FilePath import *

from IsDirectory import isPATH
isPATH(outpatient_Condition_OUTPUT)
isPATH(outpatient_Encounter_OUTPUT)

with open(outpatient_path, newline='') as csvfile:
    rows = csv.DictReader(csvfile)
    print("資料處理中....")
    for row in rows:
        Eid = row["門診號"]
        id = row["疾病序號"] if int(row["疾病序號"]) > 9 else '0' + row["疾病序號"]
        Cid = Eid + "-{}cond".format(id)

        Estatus = 'finished'

        Etype = CodeableConcept.construct()
        Etype.text = 'Encounter for symptom'
        Etype_coding = list()
        coding = Coding.construct()
        coding.code = '185345009'
        coding.system = 'http://snomed.info/sct'
        coding.display = 'Encounter for symptom'
        Etype_coding.append(coding)
        Etype.coding = Etype_coding

        Eclass_coding = Coding.construct(
            system='http://terminology.hl7.org/ValueSet/v3-ActEncounterCode', code='AMB')

        EserviceProvider = Reference.construct(reference="Organization/{}".format(row["院區"]),
                                               id=row["院區"])
        subject = Reference.construct(
            id=row["歸戶代號"], reference="Patient/{}".format(row["歸戶代號"]), type="Patient")
        Cencounter = Reference.construct(
            id=Eid, reference="Encounter/{}".format(Eid), type="Encounter")

        Crecordeddatetime = datetime.strptime(row["輸入日期"]+"+0800", '%Y%m%d%z')

        Ccode = CodeableConcept.construct()
        codelist = list()
        coding = Coding.construct()
        coding.code = str(row["疾病代號"])
        # coding.display = row["手術碼名稱{}".format(i)]
        if int(row["資料年月"]) < 201600:
            coding.system = "http://hl7.org/fhir/sid/icd-9-cm"
        else:
            coding.system = "http://hl7.org/fhir/sid/icd-10"
        codelist.append(coding)
        Ccode.coding = codelist

        ectr = Encounter.construct(id=Eid, status=Estatus, type=Etype, class_fhir=Eclass_coding, subject=subject,
                                   serviceProvider=EserviceProvider)
        cond = Condition.construct(id=Cid, subject=subject, recordedDate=Crecordeddatetime, encounter=Cencounter,
                                   code=Ccode)

        # 先把Encounter轉成json
        if not os.path.isfile(outpatient_Encounter_OUTPUT + "{}.json".format(Eid)):
            with open(outpatient_Encounter_OUTPUT + "{}.json".format(Eid), 'w') as outEncounterfile:
                outEncounterfile.write(Encounter.json(ectr))

        with open(outpatient_Condition_OUTPUT + "{}.json".format(Cid), 'w') as outConditionfile:
            outConditionfile.write(Condition.json(cond))
    print("Completed!")
