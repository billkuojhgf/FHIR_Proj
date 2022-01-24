from fhir.resources.medicationrequest import MedicationRequest
from fhir.resources.dosage import Dosage
from fhir.resources.period import Period
from fhir.resources.quantity import Quantity
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coding import Coding
from fhir.resources.reference import Reference
from datetime import datetime
from FilePath import *
import pandas as pd


def medicationRequest(dataframe, count, output_path):
    for row in dataframe.iterrows():
        row = row[1]
        id =
        try:

            with open(output_path + "{filename}.json".format(filename=count), 'w') as ourObservationsFile:
                ourObservationsFile.write(Observation.json())
            count += 1
        except Exception as e:
            print("{} encounters an error, error msg: {}".format(id, e))


if __name__ == '__main__':
    from IsDirectory import isPATH
    isPATH(inpatient_Treatment_MedicationRequest_OUTPUT)

    count = 0
    print("資料處理中...")
    with open(inpatient_Treatment_path, newline='') as csv_file:
        df = pd.read_csv(csv_file, encoding='ANSI')
        medicationRequest(
            df, count, inpatient_Treatment_MedicationRequest_OUTPUT)
    print('Complete!')
