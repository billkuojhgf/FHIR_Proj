# -*- coding: UTF-8 -*-

import csv
from fhir.resources.encounter import Encounter
from fhir.resources.period import Period
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coding import Coding
from fhir.resources.reference import Reference
from datetime import datetime
from FilePath import *

from IsDirectory import isPATH
isPATH(disease_collection_Encounter_OUTPUT)

with open(disease_collection_path, newline='') as csvfile:
    print("資料處理中....")
    rows = csv.DictReader(csvfile)
    for row in rows:
        # 住院號(Encounter_ID)
        id = row["住院號"]

        # 病歷類別
        class_coding = Coding.construct(
            system='http://terminology.hl7.org/ValueSet/v3-ActEncounterCode', code='IMP')

        # 病歷狀態
        status = 'finished'

        # 具體的病歷類別
        type = CodeableConcept.construct()
        type.text = 'Encounter for symptom'
        type.coding = list()
        coding = Coding.construct()
        coding.code = '185345009'
        coding.system = 'http://snomed.info/sct'
        coding.display = 'Encounter for symptom'
        type.coding.append(coding)

        # 該病歷是屬於哪個病患
        subject = Reference.construct()
        subject.id = row["歸戶代號"]
        subject.reference = "Patient/{}".format(row["歸戶代號"])
        subject.type = "Patient"

        # 住院原因
        reason_References = list()
        References = Reference.construct()
        References.id = id + "-00cond"
        References.reference = "Condition/{}".format(
            References.id)
        References.type = "Condition"
        reason_References.append(References)

        # 住院日期與出院日期
        performed_period = Period.construct()
        performed_period.start = datetime.strptime(
            row["住院日期"]+"+0800", '%Y%m%d%z')
        performed_period.end = datetime.strptime(row["出院日期"]+"+0800", '%Y%m%d%z')

        # 在哪個院區
        serviceProvider = Reference.construct()
        serviceProvider.id = row["院區"]
        serviceProvider.reference = "Organization/{}".format(row["院區"])
        serviceProvider.type = "Organization"

        # 將所有的元素組合成Encounter
        ectr = Encounter.construct(id=id, status=status, type=type, class_fhir=class_coding, subject=subject,
                                   serviceProvider=serviceProvider, reasonReference=reason_References)
        # 輸出成json檔案
        with open(disease_collection_Encounter_OUTPUT + "/{}.json".format(id), 'w') as outfile:
            outfile.write(Encounter.json(ectr))
print("Completed!")
