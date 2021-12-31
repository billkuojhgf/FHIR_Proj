import csv
from fhir.resources.observation import Observation, ObservationReferenceRange
from fhir.resources.specimen import Specimen, SpecimenProcessing, SpecimenCollection
from fhir.resources.period import Period
from fhir.resources.quantity import Quantity
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coding import Coding
from fhir.resources.reference import Reference
from datetime import datetime
from FilePath import *
import pandas as pd
import os


def observation(labortary_row, labortary_result_row, count):
    # id = labortary_result_row['歸戶代號']+'.'+labortary_result_row['檢驗編號']+'.'+labortary_result_row['檢驗單一項目']
    # status
    status = 'final'
    # valueQuantity or valueString
    valueQuantity = None
    valueString = None
    try:
        valueQuantity = Quantity.construct()
        valueQuantity.value = labortary_result_row['檢驗結果值']
        try:
            valueQuantity.unit = labortary_result_row['檢驗值單位']
        except:
            pass
        valueQuantity.system = 'https://www.cgmh.org.tw'
    except:
        valueString = labortary_result_row['檢驗結果值']
    # code
    code = CodeableConcept.construct()
    code_list = list()
    coding_cgmh = Coding.construct()
    coding_cgmh.code = labortary_result_row['檢驗單一項目']
    coding_cgmh.system = 'https://www.cgmh.org.tw'
    code_list.append(coding_cgmh)
    code.coding = code_list
    # subject
    subject = Reference.construct()
    subject.id = labortary_result_row['歸戶代號']
    subject.type = 'Patient'
    subject.reference = 'Patient/{}'.format(subject.id)
    # interpretations
    interpretations = list()
    interpretation = CodeableConcept.construct()
    interpretation.coding = list()
    coding_text = Coding.construct()
    coding_text.system = 'http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation'
    try:
        coding_text.code = labortary_result_row['檢驗值異常註記']
        coding_text.display = {
            'L': 'Low',
            'H': 'High'
        }.get(labortary_result_row['檢驗值異常註記'])
    except:
        pass
    interpretation.coding.append(coding_text)
    interpretations.append(interpretation)
    # reference range
    referenceRange = ObservationReferenceRange.construct(
        text=labortary_result_row['檢驗參考值'])
    # specimen
    specimen = Reference.construct()
    # specimen.id = labortary_row.歸戶代號.values[0]+'.'+labortary_row.檢驗編號.values[0]+'.'+labortary_row.檢體.values[0]
    specimen.id = "{Specfilename}_Spec".format(Specfilename=count)
    specimen.type = 'Specimen'
    specimen.reference = 'Specimen/{}'.format(specimen.id)
    # encounter
    encounter = Reference.construct()
    encounter.id = labortary_row.來源號碼.values[0]
    encounter.type = 'Encounter'
    encounter.reference = 'Encounter/{}'.format(encounter.id)
    # TODO: basedOn
    # performer = Reference.construct()
    # performer.id = labortary_row.醫囑科別.values[0]
    # performer.type = 'Organization'
    # performer.reference = 'Organization/{}'.format(performer.id)
    # effectiveDateTime
    try:
        effectiveDateTime = datetime.strptime(
            str(int(labortary_row.採檢日期.values[0])) + str(int(labortary_row.採檢時間.values[0])).zfill(4), '%Y%m%d%H%M')
    except:
        effectiveDateTime = None
    # effectivePeriod: 檢驗輸入時間與結果產出時間的間隔時間多少
    effectivePeriod = Period.construct()
    effectivePeriod.start = datetime.strptime(
        labortary_result_row['輸入日期'] + labortary_result_row['輸入時間'], '%Y%m%d%H%M')
    effectivePeriod.end = datetime.strptime(
        labortary_result_row['驗證日期'] + labortary_result_row['驗證時間'], '%Y%m%d%H%M')

    observ = Observation.construct(status=status, valueQuantity=valueQuantity, valueString=valueString,
                                   code=code, subject=subject, interpretation=interpretations, referenceRange=referenceRange, specimen=specimen,
                                   encounter=encounter, effectiveDateTime=effectiveDateTime, effectivePeriod=effectivePeriod)
    with open(labortary_Observation_OUTPUT + "{filename}.json".format(filename=count), 'w') as outEncounterfile:
        outEncounterfile.write(Observation.json(observ))


def specimen(labortary_row, labortary_result_row, count):
    # id = labortary_row.歸戶代號.values[0]+'.'+labortary_row.檢驗編號.values[0]+'.'+labortary_row.檢體.values[0]
    id = "{filename}_Spec".format(filename=count)
    # status
    status = 'available'
    # subject
    subject = Reference.construct()
    subject.id = labortary_result_row['歸戶代號']
    subject.type = 'Patient'
    subject.reference = 'Patient/{}'.format(labortary_result_row['歸戶代號'])
    # collection
    collection = SpecimenCollection.construct()
    collection.bodySite = CodeableConcept.construct(
        code=labortary_result_row['檢體'])
    # collectedDateTime
    try:
        collectedDateTime = datetime.strptime(
            str(int(labortary_row.採檢日期.values[0])) + str(int(labortary_row.採檢時間.values[0])).zfill(4), '%Y%m%d%H%M')
    except:
        collectedDateTime = None
    # receivedTime
    receivedTime = datetime.strptime(
        str(int(labortary_row.收件日期.values[0]))+str(int(labortary_row.收件時間.values[0])).zfill(4), '%Y%m%d%H%M')
    Spec = Specimen.construct(id=id, status=status, subject=subject,
                              collection=collection, collectedDateTime=collectedDateTime, receivedTime=receivedTime)
    with open(labortary_Specimen_OUTPUT + "{filename}.json".format(filename=id), 'w') as outEncounterfile:
        outEncounterfile.write(Specimen.json(Spec))


if __name__ == '__main__':
    from IsDirectory import isPATH
    isPATH(labortary_Observation_OUTPUT)
    isPATH(labortary_Specimen_OUTPUT)
    with open(labortaryResult_path, newline='') as csv_laboratary:
        print("資料處理中")
        rows = csv.DictReader(csv_laboratary)
        count = 0
        row_index = None
        for row_result in rows:
            id = row_result['檢驗編號']
            patid = row_result['歸戶代號']
            if row_index is None or row_index.檢驗編號.values[0] not in id:
                for csvname in os.listdir('../20201204csv/檢驗索引檔'):
                    with open(os.path.join('../20201204csv/檢驗索引檔', csvname)) as csv_index:
                        df_index = pd.read_csv(csv_index, encoding='ANSI')
                        if df_index.loc[(df_index.檢驗編號 == id) & (df_index.歸戶代號 == patid)].empty is False:
                            row_index = df_index.loc[(df_index.檢驗編號 == id) & (
                                df_index.歸戶代號 == patid)]
                            break
                        csv_index.seek(0)
            if row_index.檢驗編號.values[0] in id:
                observation(row_index, row_result, count)
                specimen(row_index, row_result, count)
                count += 1
            else:
                continue
        print('finish!')
