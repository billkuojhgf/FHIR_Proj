# -*- coding: UTF-8 -*-

import csv
import os
from fhir.resources.condition import Condition
from fhir.resources.encounter import Encounter
from fhir.resources.encounter import EncounterDiagnosis
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coding import Coding
from fhir.resources.reference import Reference
from datetime import datetime
from FilePath import *

from IsDirectory import isPATH
isPATH(emergency_Encounter_OUTPUT)
isPATH(emergency_Condition_OUTPUT)

count = 0

with open(emergency_path, newline='') as csvfile:
    rows = csv.DictReader(csvfile)
    print("資料處理中....")
    for row in rows:
        Crecordeddatetime = None
        Eid = row["門診號"]
        Cid = Eid + "-{}cond".format(row["疾病序號"])

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

        EserviceProvider = Reference.construct(type='Organization', reference="Organization/{}".format(row["院區"]),
                                               id=row["院區"])
        subject = Reference.construct(
            id=row["歸戶代號"], reference="Patient/{}".format(row["歸戶代號"]), type="Patient")
        Cencounter = Reference.construct(
            id=Eid, reference="Encounter/{}".format(Eid), type="Encounter")

        if not row["輸入日期"] == '':
            Crecordeddatetime = datetime.strptime(
                row["輸入日期"]+"+0800", '%Y%m%d%z')

        Ccode = CodeableConcept.construct()
        codelist = list()
        coding = Coding.construct()
        try:
            coding.code = str(row["疾病序號"])
        except:
            print("出錯，value為:{}, \nrow:{}".format(row["疾病序號"], count))
        # coding.display = row["手術碼名稱{}".format(i)]
        if int(row["資料年月"]) < 201600:
            coding.system = "http://hl7.org/fhir/sid/icd-9-cm"
        else:
            coding.system = "http://hl7.org/fhir/sid/icd-10"
        codelist.append(coding)
        Ccode.coding = codelist

        # is Main Diagnosis
        Ediaglist = list()
        condition = Reference.construct(
            id=Cid, reference="Condition/{}".format(Cid), type='Condition')
        diagnosis = EncounterDiagnosis.construct(condition=condition, rank=1)
        Ediaglist.append(diagnosis)

        if row["主診斷"] == 'Y':
            # when Main diagnosis == 'Y'
            ectr = Encounter.construct(id=Eid, status=Estatus, type=Etype, class_fhir=Eclass_coding, subject=subject,
                                       serviceProvider=EserviceProvider, diagnosis=Ediaglist)
        else:
            ectr = Encounter.construct(id=Eid, status=Estatus, type=Etype, class_fhir=Eclass_coding, subject=subject,
                                       serviceProvider=EserviceProvider)
        cond = Condition.construct(id=Cid, subject=subject, recordedDate=Crecordeddatetime, encounter=Cencounter,
                                   code=Ccode)

        # 先把Encounter轉成json
        # 判斷資料夾內是否沒有Encounter的File
        if not os.path.isfile(emergency_Encounter_OUTPUT + "{}.json".format(Eid)):
            with open(emergency_Encounter_OUTPUT + "{}.json".format(Eid), 'w') as outEncounterfile:
                outEncounterfile.write(Encounter.json(ectr))
        else:
            # 有Encounter的File, 但如果是主診斷,要把該檔案的內容覆蓋過去
            if row["主診斷"] == 'Y':
                with open(emergency_Encounter_OUTPUT + "{}.json".format(Eid), 'w') as outEncounterfile:
                    outEncounterfile.write(Encounter.json(ectr))
        # 再把Condition轉成json
        with open(emergency_Condition_OUTPUT + "{}.json".format(Cid), 'w') as outConditionfile:
            outConditionfile.write(Condition.json(cond))
        count += 1
    print("Completed!")
