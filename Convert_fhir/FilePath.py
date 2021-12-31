# Input
DATA_PATH = '../20201204csv/'

disease_collection_path = DATA_PATH + "18200_疾病分類統計檔_1.csv"
outpatient_path = DATA_PATH + "18200_門診診斷檔_1.csv"
emergency_path = DATA_PATH + "18200_急診診斷檔_1.csv"
patient_path = DATA_PATH + "18200_歸戶個案_1.csv"
labortary_path = DATA_PATH + "18200_檢驗索引檔_1.csv"
labortaryResult_path = DATA_PATH + "18200_檢驗結果歷史檔_1.csv"


# Output
OUTPUT_PATH = "../output/"

# 歸戶個案
patient_info_Patient_OUTPUT = OUTPUT_PATH + "Patient_Info/Patient/"

# 疾病分類統計檔輸出路徑
disease_collection_Encounter_OUTPUT = OUTPUT_PATH + "Disease_Collection/Encounter/"
disease_collection_Condition_OUTPUT = OUTPUT_PATH + "Disease_Collection/Condition/"
disease_collection_Procedure_OUTPUT = OUTPUT_PATH + "Disease_Collection/Procedure/"

# 門診診斷檔輸出路徑
outpatient_Encounter_OUTPUT = OUTPUT_PATH + "OutPatient/Encounter/"
outpatient_Condition_OUTPUT = OUTPUT_PATH + "OutPatient/Condition/"

# 急診診斷檔輸出路徑
emergency_Encounter_OUTPUT = OUTPUT_PATH + "Emergency/Encounter/"
emergency_Condition_OUTPUT = OUTPUT_PATH + "Emergency/Condition/"

# 檢驗索引檔、檢驗結果歷史檔
labortary_Observation_OUTPUT = OUTPUT_PATH + "Labortary/Observation/"
labortary_Specimen_OUTPUT = OUTPUT_PATH + "Labortary/Specimen/"

# 生命徵象紀錄檔
#
