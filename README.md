# FHIR_Proj
---
# 簡介FHIR

## FHIR是什麼？

- FHIR (**Fast** Health Interoperability Resource)
- 一種新興的醫療資訊交換標準
- 由HL7 International (國際健康資訊第七層協會)制定
- 主要目標為
    1. 促進醫療單位有效溝通醫療相關資訊
    2. 廣泛應用於多種設備，包含但不限於電腦、手機、平板等裝置

## 伺服器架構

- 傳統資料互通架構

    ![%E7%B0%A1%E4%BB%8BFHIR%2088ee7609145848baaa807ef5f127f60a.gif](./Picture/traditional%20data%20exchange%20architecture.gif)

    傳統架構中，因為每個醫院所導入的資料庫以及每個table的column都不盡相同，在交換資料時會出現很多資料不一致的情形，導致無法交流

- FHIR的伺服器互通架構

    ![%E7%B0%A1%E4%BB%8BFHIR%2088ee7609145848baaa807ef5f127f60a/FHIR.gif](./Picture/FHIR%20architecture.gif)

    在導入FHIR的伺服器架構後，因為兩者的格式一致，所以可以互相交流

## FHIR為何會成為新一代醫療系統的準則?

- 把整個醫療流程/體系中的資料全部標準化成為一單一資料結構
- 支援多種不同資料格式
- 採用主流資訊實作標準
    - 沒醫學背景的碼農也容易理解(例如我)
    - 跟其他系統對接方便
- 程式碼可讀性高
    - 對於不會程式語言的醫療人員也容易閱讀

## FHIR結構

- 對醫療人員/醫學系學生來說：
FHIR就是一種描述醫療資源/行為/數據/流程...等等方法
- 對於開發人員/資訊系學生來說：
FHIR就是一堆Data Structure，可以透過每個Resource的Reference去做溝通串連
- 每一個醫療資源/行為/數據/流程都是一個Resource(Patient, Encounter, Procedure....)
- 依照不同分類，FHIR將幾個Reference組成一支Module以方便檢視

### 參考資料

[FHIR:快速健康照護互通資源(一)](https://yellowgirl3614.medium.com/fhir-%E5%BF%AB%E9%80%9F%E5%81%A5%E5%BA%B7%E7%85%A7%E8%AD%B7%E4%BA%92%E9%80%9A%E8%B3%87%E6%BA%90-%E4%BE%9D-a50108895776)