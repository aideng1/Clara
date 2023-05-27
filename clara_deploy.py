import requests
import re
import pandas as pd
import csv
import numpy as np
from numpy import loadtxt
from keras.models import Sequential
from keras.layers import Dense

## Original profile development based only on sub-genre preferences
one = ['9780812988529']
two = ['1451635621', '141439602', '1501173219', '99429799','425252965','143038273','452282152','9780679724773','9780679781585','9780061120091','440212561','9781608194506','9780312370848','9781982603847','9780812980356','9780375842207','9780143135692','9780143129479','9780679745204','9780385341004','9780425232200','9780316070638','9780544176560','9780743227445','9780451166890','9781519425591','9780380018178','9781688034563','9781400079988','312429983']
three = ['1774760878','451457994','60892994','312367546','60850523','441013597','1250773024','1451673264','015603008X','553288202','9780553382563','9780441007462','9783596296590','9781984802781','9781785860898','9780553293357','9780385490818','9780593359440','9780553213515','9780451530653']
four = ['1573227951','1573220825','1400077095','1425910394','159307736X','1572703857','1572705493','031298166X','1579126243','1572705477','1572704721','1579126251','1572704977','1579126952','1579126235','1579126898']
five = ['1572704497','1416534423','037312418X','189239118X','1569719365','1563891891','1401209335','1401209254','1401200133','1401212026','1563896311','1401200192','1563898942','188845170X','1933110457']
six = ['345806786','380807343','486411095','110198919X','61944890','1983988367','375703764','0765318741 ','9780345337665','9781982127794','9780743412285','9781681774664','9798550197554','9781501167713','1542539145','9781982138264','9780062094360','9780143039983','9781949982978','451219422','9781936594481','9780307743527','9780425188804','9780307888686','312924585']
seven = ['312924585','679734503','9780795333453','9780380730407','9780582419285','9780394758282','9781400032716','9780684803869','9780440245926','9780451205766','9798649649759','679722645','9780679723257','9780905712314','9781713326472','9780743298032','9780141439617','62073486','143132040','0307588378 ','679745580','60925175','525510273','525535861','307949486']
eight = ['62073486','143132040','0307588378', '679745580','60925175','525510273','525535861','307949486','345806786','312924585','440245915','9780345544148','9780345538987','9780515153651','9780446677387','9780060584757','9780375706677','9780061898815','9780451469793','9780553593549','9780140449266','9782709624930','9781594634024','9780425240335','9781455567386']
nine = ['1416520384','1887368795','1932382720','1887368884','155652532X','1842991248','1593074743','078684907X','1416918086','006447268X','1421500914','1421500906','1857237250','055215315X','006001234X','1933110333','068987670X','1416912274','1857236076','1416502041','034543949X','1857230752','1402736959']
ten = ['1451635621','1455530883','1496707443','385335482','62941208','62566733','9781495368219','9780778304807','9780452287891','9780062980076','9780060894702','9781538719107','9780593200124','9780451490803','9781612186429','9781455582877','9780307395368','9780399587665','9781533382443','9780778360018','9780425227510']
up = []
def profile_gen(id):
    #call to app to collect initial profile
    name = requests.get('https://titler.bubbleapps.io/version-test/api/1.1/obj/user/{}'.format(id))
    data = name.json()
    subgenrecomp = data.get('response',{}).get('subgenrecomp')

    for sub in subgenrecomp:
        if sub == 1:
            up.extend(one)
        if sub == 2:
            up.extend(two)
        if sub == 3:
            up.extend(three)
        if sub == 4:
            up.extend(four)
        if sub == 5:
            up.extend(five)
        if sub == 6:
            up.extend(six)
        if sub == 7:
            up.extend(seven)
        if sub == 8:
            up.extend(eight)
        if sub == 9:
            up.extend(nine)
        if sub == 10:
            up.extend(ten)
    thru = requests.patch('https://titler.bubbleapps.io/version-test/api/1.1/obj/user/{}'.format(id), json={'clarasuggestions': up})

## Subsequent profile development based on likes
likes = []
mod = []
suggestions = []
def profile_regen(books, uid):
    new_row = []
    with open('TitlerRefFile.csv','r',newline='', encoding='utf8') as file:
        reader = csv.DictReader(file)
        rows = [row for row in reader if row['ISBN'] in books]
        for row in rows:
            row = re.sub('(ISBN.*)','', str(row))
            row = re.findall('(\d+(?:\.\d+)?)', str(row))
            new_row.append([float(i) for i in row])
            mod.append(1)
        likes.extend(new_row)
    X = likes
    y = mod

    #keras model
    model = Sequential()
    model.add(Dense(8, input_dim=5, activation='relu'))
    model.add(Dense(5, activation='relu'))
    model.add(Dense(1, activation='sigmoid'))

    #compile
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

    #fit
    model.fit(X, y, epochs=100, batch_size=5)

    #evaluate
    _, accuracy = model.evaluate(X, y)
    #print('Accuracy reads at %.2f' % (accuracy*100))

    ref = loadtxt('TitlerRefFile.csv', delimiter=",", skiprows=1, usecols=(0,1,2,3,4))
    predictions = model.predict(ref)

    row_values = []
    for i in range(0, len(predictions)):
        if predictions[i] > .55:
            row_values.append(i)

    df = pd.read_csv('TitlerRefFile.csv')
    isbn_column = df.ISBN
    for rows in row_values:
        for i in range(0,len(isbn_column)):
            if rows == i:
                suggestions.append(isbn_column[i])
    print(uid)
    yon = requests.patch('https://titler.bubbleapps.io/version-test/api/1.1/obj/user/{}'.format(uid), json={'clarasuggestions': suggestions})
