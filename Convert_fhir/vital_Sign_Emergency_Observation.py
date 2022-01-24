from fhir.resources.observation import Observation
from fhir.resources.period import Period
from fhir.resources.quantity import Quantity
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coding import Coding
from fhir.resources.reference import Reference
from datetime import datetime
from FilePath import *
import pandas as pd


def observation(dataframe, count, output_path):
    for row in dataframe.iterrows():
        row = row[1]
        id = str(row.歸戶代號) + '.' + str(row.住院號) + '.' + \
            str(row.項目代號) + "." + str(row.輸入日期) + str(row.輸入時間)
        try:
            # id, 因為位數大小過大所以目前先不放進去ㄌ
            # id = row.歸戶代號 + '.' + row.住院號 + '.' + row.項目代號 + row.輸入日期 + row.輸入時間

            # status
            status = 'perliminary'

            # category
            category = CodeableConcept.construct()
            category.coding = list()
            coding_category = Coding.construct()
            coding_category.system = "http://terminology.hl7.org/CodeSystem/observation-category"
            coding_category.code = 'vital-signs'
            category.coding.append(coding_category)

            # value: valueQuantity or valueString
            if row.測量值 != row.測量值:  # 如果測量值為空，直接跳過這一row
                continue
            valueQuantity = None
            valueString = None
            try:
                valueQuantity = Quantity.construct()
                valueQuantity.value = row.測量值
                # try:
                #     valueQuantity.unit = row.
                # except:
                #     pass
                valueQuantity.system = 'https://www.cgmh.org.tw'
            except:
                valueString = row.測量值

            # bodySite(if has value): 有些測量(如體溫、耳溫等)會有測量的部位代號，如果有就放
            bodySite = None
            if row.部位代號 != row.部位代號:
                bodySite = CodeableConcept.construct()
                bodySite.coding = list()
                coding_bodySite = Coding.construct()
                coding_bodySite.code = row.部位代號
                coding_bodySite.system = 'https://www.cgmh.org.tw'
                if row.部位名稱 != row.部位名稱:
                    coding_bodySite.display = row.部位名稱
                bodySite.coding.append(coding_bodySite)

            # code
            code = CodeableConcept.construct()
            code.coding = list()
            coding_code = Coding.construct()
            coding_code.display = row.項目名稱
            coding_code.code = row.項目代號
            coding_code.system = 'https://www.cgmh.org.tw'
            code.coding.append(coding_code)

            # subject
            subject = Reference.construct()
            subject.id = row.歸戶代號
            subject.type = 'Patient'

            # # interpretations
            # interpretations = list()
            # interpretation = CodeableConcept.construct()
            # interpretation.coding = list()
            # coding_text = Coding.construct()
            # coding_text.system = 'http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation'
            # try:
            #     coding_text.code = row.檢驗值異常註記
            #     coding_text.display = {
            #         'L': 'Low',
            #         'H': 'High'
            #     }.get(row.檢驗值異常註記)
            # except:
            #     pass
            # interpretation.coding.append(coding_text)
            # interpretations.append(interpretation)

            # # reference range
            # referenceRange = ObservationReferenceRange.construct(
            #     text=row.檢驗參考值)

            # encounter
            encounter = Reference.construct()
            encounter.id = row.歸戶代號 + '_' + row.住院號
            encounter.type = 'Encounter'

            # # performer
            # performer = Reference.construct()
            # performer.id = row.資料來源

            # effectiveDateTime
            if row.輸入時間 != row.輸入時間:
                effectiveDateTime = datetime.strptime(
                    str(int(row.輸入日期)), '%Y%m%d')
            else:
                effectiveDateTime = datetime.strptime(
                    str(int(row.輸入日期)) + str(int(row.輸入時間)).zfill(4), '%Y%m%d%H%M')

            # effectivePeriod: 檢驗輸入時間與結果產出時間的間隔時間多少
            if row.輸入時間 != row.輸入時間:
                effectivePeriod.start = datetime.strptime(
                    str(int(row.輸入日期)), '%Y%m%d'
                )
            else:
                effectivePeriod = Period.construct()
                effectivePeriod.start = datetime.strptime(
                    str(int(row.輸入日期)) + str(int(row.輸入時間)).zfill(4), '%Y%m%d%H%M')

            # try:
            #     effectivePeriod.end = datetime.strptime(
            #         str(int(row.驗證日期)) + str(int(row.驗證時間)).zfill(4), '%Y%m%d%H%M')
            # except:
            #     pass

            # 數值輸出成json
            observ = Observation.construct(status=status, valueQuantity=valueQuantity, category=category, valueString=valueString,
                                           code=code, bodySite=bodySite, subject=subject, encounter=encounter, effectiveDateTime=effectiveDateTime, effectivePeriod=effectivePeriod)
            with open(output_path + "{filename}.json".format(filename=count), 'w') as ourObservationsFile:
                ourObservationsFile.write(Observation.json(observ))
            count += 1
        except Exception as e:
            print("{} encounters an error, error msg: {}".format(id, e))


if __name__ == '__main__':
    from IsDirectory import isPATH
    isPATH(vital_sign_Emergency_Observation_OUTPUT)

    count = 0
    print("資料處理中...")
    with open(vitalSign_Emergency_path, newline='') as csv_file:
        df = pd.read_csv(csv_file, encoding='ANSI')
        observation(df, count, vital_sign_Emergency_Observation_OUTPUT)
    print('Complete!')
