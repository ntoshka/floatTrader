import pandas as pd
from datetime import datetime


def getNewFloat(minV, maxV, average):
    return (maxV - minV)*average + minV

def getVar(a,b):
    return (1/12) * (b-a)**2

def getExpectedFloat(quality):
    qualities = ["Battle-Scarred", "Well-Worn", "Field-Tested", "Minimal Wear", "Factory New"]
    for ix, q in enumerate(qualities):
        if q in quality:
            if ix == 4:
                return 0.035
            if ix == 3:
                return 0.11
            if ix == 2:
                return 0.265
            if ix == 1:
                return 0.415
            else:
                return 0.725

def getQuality(f):
    qualities = ["Battle-Scarred", "Well-Worn", "Field-Tested", "Minimal Wear", "Factory New"]
    if f < 0.07:
        return qualities[4]
    elif f < 0.15:
        return qualities[3]
    elif f < 0.38:
        return qualities[2]
    elif f < 0.45:
        return qualities[1]
    else:
        return qualities[0]

def getQualityBorders(quality):
    qualities = ["Battle-Scarred", "Well-Worn", "Field-Tested", "Minimal Wear", "Factory New"]
    for ix, q in enumerate(qualities):
        if q in quality:
            if ix == 4:
                return [0,0.07]
            if ix == 3:
                return [0.07,0.15]
            if ix == 2:
                return [0.15,0.38]
            if ix == 1:
                return [0.38,0.45]
            else:
                return [0.45,1]

def getTradeupOptions(base):
    collection = base["collection"]
    baseRarity = base["rarityNum"]
    expectedFloat = getExpectedFloat(base["quality"])
    qualityBorders = getQualityBorders(base["quality"])
    variance = getVar(qualityBorders[0], qualityBorders[1])

    tradeupOptions = df.loc[df["collection"] == collection].loc[df["rarityNum"] == baseRarity + 1]

    tradeupIndices = []

    for tradeupName in tradeupOptions["itemName"].unique():
        t = tradeupOptions.loc[tradeupOptions["itemName"] == tradeupName].sample(1)
        newFloat = getNewFloat(t["minWear"], t["maxWear"], expectedFloat)
        upperBound = newFloat + variance
        lowerBound = newFloat - variance

        upperQuality = getQuality(upperBound.values[0])
        lowerQuality = getQuality(lowerBound.values[0])

        try:
            tradeupIndices.append(tradeupOptions.loc[tradeupOptions["itemName"] == tradeupName].loc[tradeupOptions["quality"] == upperQuality].index.values.astype(int)[0])
        except:
            pass

        try:
            tradeupIndices.append(tradeupOptions.loc[tradeupOptions["itemName"] == tradeupName].loc[tradeupOptions["quality"] == lowerQuality].index.values.astype(int)[0])
        except:
            pass

    tradeupIndices = list(set(tradeupIndices))

    return df.iloc[tradeupIndices]

def getMargin(base, tradeup):
    basePrice = base["price"]
    buyPrice = basePrice * 10

    margins = list()

    for ix, row in tradeup.iterrows():
        #deduct 15% tax
        marginBuff = (row["price"]) - buyPrice

        margins.append(marginBuff)
    
    return sum(margins)/len(margins)


startTime = datetime.now()

df = pd.read_csv("data/items.csv")
df["rarityNum"] = pd.to_numeric(df["rarityNum"])
df["price"] = pd.to_numeric(df["price"])

viableItems = list()
for ix, row in df.iterrows():
    options = getTradeupOptions(row)
    if len(options) == 0:
        continue
    margin = getMargin(row, options)

    #if margin >= 0.01 and margin <= 1 and row["listings"] > 100:
    if margin >= 0.01:
        viableItems.append({"base": row,
                            "options": options,
                            "margin": margin})
    


print(len(viableItems))
sortedViableItems = sorted(viableItems,key=lambda x: x["margin"])

for item in sortedViableItems[-10:]:
    print(item["base"])
    print(item["options"])
    print(item["margin"])
    print("\n-----------------------------------------------------------------------------\n")
    
print(datetime.now() - startTime)
