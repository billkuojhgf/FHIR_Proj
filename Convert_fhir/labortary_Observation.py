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

from IsDirectory import isPATH
isPATH(labortary_Observation_OUTPUT)
isPATH(labortary_Specimen_OUTPUT)


def observation(labortary_row, labortary_result_row):
    # id = TODO
    # status
    status = 'final'
    # valueQuantity
    valueQuantity = Quantity.construct()
    valueQuantity.value = labortary_result_row['檢驗結果值']
    valueQuantity.unit = labortary_result_row['檢驗值單位']
    valueQuantity.system = 'https://www.cgmh.org.tw'
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
    subject.reference = 'Patient/{}'.format(labortary_result_row['歸戶代號'])
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
    specimen = Reference.construct(  # id = TODO
        reference="Specimen/{}".format(''), type="Specimen")
    # encounter
    Eid = labortary_row.來源號碼.values[0]
    encounter = Reference.construct(
        id=Eid, reference="Encounter/{}".format(Eid), type="Encounter")
    # performer
    pid = labortary_row.醫囑科別.values[0]
    performer = Reference.construct(
        id=pid, reference="Organization/{}".format(pid), type="Organization")
    # effectiveDateTime: 檢驗索引檔.採檢日期、時間
    # effectiveDateTime
    effectiveDateTime = datetime.strptime(
        str(int(labortary_row.採檢日期.values[0]))+str(int(labortary_row.採檢時間.values[0])).zfill(4), '%Y%m%d%H%M')

    observ = Observation.construct(status=status, valueQuantity=valueQuantity,
                                   code=code, subject=subject, interpretation=interpretations, referenceRange=referenceRange, specimen=specimen,
                                   encounter=encounter, performer=performer, effectiveDateTime=effectiveDateTime)
    with open(labortary_Observation_OUTPUT + "{}.json".format(1), 'w') as outEncounterfile:
        outEncounterfile.write(Observation.json(observ))

    print('finish!')


def specimen(labortary_row, labortary_result_row):
    # id = TODO
    # status
    status = 'available'
    # timePeriod
    timePeriod = Period.construct()
    timePeriod.start = datetime.strptime(
        labortary_result_row['輸入日期'] + labortary_result_row['輸入時間'], '%Y%m%d%H%M')
    timePeriod.end = datetime.strptime(
        labortary_result_row['驗證日期'] + labortary_result_row['驗證時間'], '%Y%m%d%H%M')
    # processing
    # warn: May have an error while formatting into json because of Chinese Words
    processing = SpecimenProcessing.construct()
    processing.description = labortary_result_row['檢驗名稱縮寫']
    processing.procedure = list().append(CodeableConcept.construct(
        system='https://www.cgmh.org.tw', code=labortary_result_row['檢驗單一項目']))
    # subject
    subject = Reference.construct()
    subject.id = labortary_result_row['歸戶代號']
    subject.type = 'Patient'
    subject.reference = 'Patient/{}'.format(labortary_result_row['歸戶代號'])
    # collection
    collection = SpecimenCollection.construct()
    collection.bodySite = CodeableConcept.construct(
        code=labortary_result_row['檢體'])
    # parent = TODO
    # collectedDateTime
    collectedDateTime = datetime.strptime(
        str(int(labortary_row.採檢日期.values[0]))+str(int(labortary_row.採檢時間.values[0])).zfill(4), '%Y%m%d%H%M')
    Spec = Specimen.construct(status=status, timePeriod=timePeriod, processing=processing, subject=subject,
                              collection=collection, collectedDateTime=collectedDateTime)
    with open(labortary_Specimen_OUTPUT + "{}.json".format(1), 'w') as outEncounterfile:
        outEncounterfile.write(Specimen.json(Spec))

    pass


if __name__ == '__main__':
    with open(labortaryResult_path, newline='') as csv_laboratary:
        print("資料處理中")
        rows = csv.DictReader(csv_laboratary)
        for row_result in rows:
            id = row_result['檢驗編號']
            patid = row_result['歸戶代號']
            for csvname in os.listdir('../20201204csv/檢驗索引檔'):
                with open(os.path.join('../20201204csv/檢驗索引檔', csvname)) as csv_index:
                    df_index = pd.read_csv(csv_index, encoding='ANSI')
                    if df_index.loc[(df_index.檢驗編號 == id) & (df_index.歸戶代號 == patid)].empty is False:
                        row_index = df_index.loc[(df_index.檢驗編號 == id) & (
                            df_index.歸戶代號 == patid)]
                        break
            observation(row_index, row_result)
            specimen(row_index, row_result)
