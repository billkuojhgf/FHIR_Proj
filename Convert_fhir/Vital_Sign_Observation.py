import threading
from fhir.resources.observation import Observation, ObservationReferenceRange
from fhir.resources.specimen import Specimen, SpecimenCollection
from fhir.resources.period import Period
from fhir.resources.quantity import Quantity
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coding import Coding
from fhir.resources.reference import Reference
from datetime import datetime
from FilePath import *
import pandas as pd
import os


def observation(labortary_dataframe, count):
    for row in labortary_dataframe.iterrows():
        # id = row.歸戶代號+'.'+row.檢驗編號+'.'+row.檢驗單一項目
        # status
        status = 'perliminary'
        # valueQuantity or valueString
        valueQuantity = None
        valueString = None
        try:
            valueQuantity = Quantity.construct()
            valueQuantity.value = row.檢驗結果值
            try:
                valueQuantity.unit = row.檢驗值單位
            except:
                pass
            valueQuantity.system = 'https://www.cgmh.org.tw'
        except:
            valueString = row.檢驗結果值
        # code
        code = CodeableConcept.construct()
        code_list = list()
        coding_cgmh = Coding.construct()
        coding_cgmh.display = row.項目名稱
        coding_cgmh.code = row.項目代號
        coding_cgmh.system = 'https://www.cgmh.org.tw'
        code_list.append(coding_cgmh)
        code.coding = code_list
        # subject
        subject = Reference.construct()
        subject.id = row.歸戶代號
        subject.type = 'Patient'
        subject.reference = 'Patient/{}'.format(subject.id)
        # interpretations
        interpretations = list()
        interpretation = CodeableConcept.construct()
        interpretation.coding = list()
        coding_text = Coding.construct()
        coding_text.system = 'http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation'
        try:
            coding_text.code = row.檢驗值異常註記
            coding_text.display = {
                'L': 'Low',
                'H': 'High'
            }.get(row.檢驗值異常註記)
        except:
            pass
        interpretation.coding.append(coding_text)
        interpretations.append(interpretation)
        # reference range
        referenceRange = ObservationReferenceRange.construct(
            text=row.檢驗參考值)
        # specimen
        specimen = Reference.construct()
        # specimen.id = labortary_row.歸戶代號.values[0]+'.'+labortary_row.檢驗編號.values[0]+'.'+labortary_row.檢體.values[0]
        specimen.id = "{Specfilename}_Spec".format(Specfilename=count)
        specimen.type = 'Specimen'
        specimen.reference = 'Specimen/{}'.format(specimen.id)
        # encounter
        encounter = Reference.construct()
        encounter.id = row.來源號碼
        encounter.type = 'Encounter'
        encounter.reference = 'Encounter/{}'.format(encounter.id)
        # effectiveDateTime
        try:
            effectiveDateTime = datetime.strptime(
                str(int(row.輸入日期)) + str(int(row.輸入時間)).zfill(4), '%Y%m%d%H%M')
        except:
            effectiveDateTime = None
        # effectivePeriod: 檢驗輸入時間與結果產出時間的間隔時間多少
        effectivePeriod = Period.construct()
        effectivePeriod.start = datetime.strptime(
            str(int(row.輸入日期)) + str(int(row.輸入時間)).zfill(4), '%Y%m%d%H%M')
        try:
            effectivePeriod.end = datetime.strptime(
                str(int(row.驗證日期)) + str(int(row.驗證時間)).zfill(4), '%Y%m%d%H%M')
        except:
            pass
        observ = Observation.construct(status=status, valueQuantity=valueQuantity, valueString=valueString,
                                       code=code, subject=subject, interpretation=interpretations, referenceRange=referenceRange, specimen=specimen,
                                       encounter=encounter, effectiveDateTime=effectiveDateTime, effectivePeriod=effectivePeriod)
        with open(labortary_Observation_OUTPUT + "{filename}.json".format(filename=count), 'w') as outEncounterfile:
            outEncounterfile.write(Observation.json(observ))
        count += 1


if __name__ == '__main__':
    from IsDirectory import isPATH
    isPATH(labortary_Observation_OUTPUT)

    count = 0
    print("資料處理中...")
    with open(labortaryResult_path, newline='') as csv_labortary:
        df_result = pd.read_csv(csv_labortary, encoding='ANSI')
    for csvname in os.listdir('../20201204csv/檢驗索引檔'):
        with open(os.path.join('../20201204csv/檢驗索引檔', csvname)) as csv_index:
            df_index = pd.read_csv(csv_index, encoding='ANSI')
            df = df_result.merge(df_index, how='inner', on=(
                '歸戶代號', '檢驗編號', '檢體'), suffixes=('_result', '_index'))
            if df.empty is False:
                observation(df, count)
                count += df.index.size
            print(csvname, '完成 !')
    print('Complete!')
