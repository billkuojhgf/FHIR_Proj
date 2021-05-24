# Save Model Using joblib
import pandas
from sklearn import model_selection
from sklearn.linear_model import LogisticRegression
import joblib
url = "https://raw.githubusercontent.com/jbrownlee/Datasets/master/pima-indians-diabetes.data.csv"
names = ['preg', 'plas', 'pres', 'skin',
         'test', 'mass', 'pedi', 'age', 'class']
# 懷孕次數、血糖、血壓、脂肪厚度（我們資料裡不可能會有的東西）、
# 胰島素、ＢＭＩ、糖尿病數值（資料庫沒有）、年齡、是否是糖尿病（答案）
dataframe = pandas.read_csv(url, names=names)
array = dataframe.values
# 在url中的csv，column 0~7為data的數值
X = array[:, 0:8]
# Url中的csv，column 8 為data的答案
Y = array[:, 8]
test_size = 0.33
seed = 7
X_train, X_test, Y_train, Y_test = model_selection.train_test_split(
    X, Y, test_size=test_size, random_state=seed)
# Fit the model on training set
model = LogisticRegression()
model.fit(X_train, Y_train)
# save the model to disk
# filename as model name
filename = 'finalized_model.sav'
# saving
joblib.dump(model, filename)

# # some time later...

# # load the model from disk
loaded_model = joblib.load(filename)
result = loaded_model.score(X_test, Y_test)
print(result)

result = loaded_model.predict_proba(X_test)
print(result)
