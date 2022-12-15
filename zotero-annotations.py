import sqlite3
from collections import defaultdict
'''
    sqlite中保存了zotero的所有数据，文件地址如下
    macOS:	/Users/<username>/Zotero
    Windows 7 and higher:	/Users/<username>/Zotero
    Windows XP/2000	    :   C:\Documents and Settings\<username>\Zotero
    Linux	            :   ~/Zotero
'''

COLLECTION_NAME = "test"    # 暂不支持嵌套集合
DB_PATH = r"C:\Users\24200\Zotero\zotero.sqlite"

db = sqlite3.connect(DB_PATH)
cursor= db.cursor()


def get_collections_id(collection_name):
    sql = "SELECT collectionID FROM collections WHERE collectionName='%s';" % (collection_name)
    cursor.execute(sql)
    data = cursor.fetchall()
    if data==[]:
        print("Collection not found!")
        return []
    else:
        if len(data)==1:
            print(collection_name,' ID为：',data[0][0])
        else:
            print("找到多个同名collection,ID分别为：",';'.join([i[0] for i in data])) 
        return [i[0] for i in data]

def get_items_by_collection(collection_ids):
    items = []
    for id in collection_ids:
        sql = "SELECT itemID FROM collectionItems WHERE collectionID='%s';" % (id)
        cursor.execute(sql)
        data = cursor.fetchall()
        print(data)
        items.append([i[0] for i in data])
        print('ID为',id,'的collection共有',len(items[-1]),'篇文章')
    
    return items

def get_items_title(items_id):
    id2title = defaultdict(str)
    for item_id in items_id:
        for id in item_id:
            sql = '''select itemDataValues.value from itemData left join itemDatavalues on  
                    itemData.valueID=itemDatavalues.valueID where itemData.itemID='%s' and fieldID='1' ''' % id
            cursor.execute(sql)
            data = cursor.fetchall()
            if data!=[]:
                id2title[id] = data[0][0]

    return id2title

def get_annotations(items_id,id2title):
    colors = []
    for i,item_id in enumerate(items_id):
        annotations_data = defaultdict(list)   # 将数据按color标签分类存储
        for id in item_id:
            # 一篇文章里所有的高亮注释
            sql = "SELECT text,comment,color FROM itemAnnotations as anno left join itemAttachments as attach on anno.parentItemID=attach.itemID WHERE attach.parentItemID='%s' ;" % (id)
            cursor.execute(sql)
            data = cursor.fetchall()
            color_anno_dict = defaultdict(list)
            # 按照color值对data分类
            for d in data:
                if d[0]!=None:
                        color_anno_dict[d[2]].append((d[0],d[1]))
            
            # 存入annotations_data
            for color,info in color_anno_dict.items():
                annotations_data[color].append(
                    {
                        'title':id2title[id],
                        'text':[t[0] for t in info],
                        'comment':[t[1] for t in info]
                    }
                )
            

     
        # 写入markdown文件
        with open(COLLECTION_NAME + '_'+str(ids[i])+'.md','w',encoding='utf-8') as f:
            f.write('# %s<br />\n' % COLLECTION_NAME)
            for color,items in annotations_data.items():
                print(len(annotations_data.keys()),color)
                f.write('## <font color="%s">高亮文本</font><br />\n' % color)
                for item in items:
                    f.write('### %s<br />\n' % item['title'])
                    for text,comment in list(zip(item['text'],item['comment'])):
                        f.write(text+'<br />\n')
                        if comment!=None:
                            f.write(comment+'<br />\n')
  






ids = get_collections_id(COLLECTION_NAME)
items = get_items_by_collection(ids)

id2title = get_items_title(items)
get_annotations(items,id2title)

