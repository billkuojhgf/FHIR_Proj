# -*- coding: UTF-8 -*-

import csv
from fhir.resources.procedure import Procedure
from fhir.resources.period import Period
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coding import Coding
from fhir.resources.reference import Reference
from datetime import datetime
from FilePath import *

from IsDirectory import isPATH
isPATH(disease_collection_Procedure_OUTPUT)

with open(disease_collection_path, newline='') as csvfile:
    print("資料處理中....")
    rows = csv.DictReader(csvfile)
    count = 0
    for row in rows:
        for i in range(1, 10):
            isLaterProcedureExists = False
            if row["手術碼{}".format(i)] != '':
                isLaterProcedureExists = True
                pid = row["住院號"] + "-0{}proc".format(i)  # 住院號

                code = CodeableConcept.construct()
                codelist = list()
                coding = Coding.construct()
                coding.code = str(row["手術碼{}".format(i)])
                # coding.display = row["手術碼名稱{}".format(i)]
                if int(row["資料年月"]) < 201600:
                    coding.system = "http://hl7.org/fhir/sid/icd-9-cm"
                else:
                    coding.system = "http://hl7.org/fhir/sid/icd-10"
                codelist.append(coding)
                code.coding = codelist

                subject = Reference.construct()
                subject.id = row["歸戶代號"]
                subject.reference = "Patient/{}".format(row["歸戶代號"])
                subject.type = "Patient"

                encounter = Reference.construct()
                encounter.id = row["住院號"]
                encounter.reference = "Encounter/{}".format(row["住院號"])
                encounter.type = "Encounter"

                performed_period = Period.construct()
                performed_period.start = datetime.strptime(
                    row["住院日期"]+"+0800", '%Y%m%d%z')
                performed_period.end = datetime.strptime(
                    row["出院日期"]+"+0800", '%Y%m%d%z')

                proc = Procedure.construct(id=pid, status="completed", code=code, subject=subject, encounter=encounter,
                                           performedPeriod=performed_period)
                with open(disease_collection_Procedure_OUTPUT + "{}.json".format(pid), 'w') as outfile:
                    outfile.write(Procedure.json(proc))
            if not isLaterProcedureExists:
                continue
print("Completed! ")
