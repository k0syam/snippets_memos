以下は、指定された要件に基づいてMongoDBのcollectionAからcollectionBへドキュメントを同期するためのPythonスクリプトです。このスクリプトはpymongoライブラリを使用しており、以下の機能を実装しています：

1. **collectionBに存在しないドキュメントの追加**：collectionAのドキュメントの`id`をキーとして、collectionBに同じ`id`のドキュメントが存在しない場合にのみ追加します。
2. **ドキュメントの更新**：collectionBに同じ`id`のドキュメントが存在する場合、その`update_datetime`を確認し、collectionAの対応するドキュメントの`update_datetime`がより新しい場合に更新します。

スクリプトの実装は以下の通りです：

```python
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime

# MongoDBのクライアントを設定
client = MongoClient('mongodb://localhost:27017/')
db = client['your_database']  # 使用するデータベース名を設定

collectionA = db.collectionA
collectionB = db.collectionB

# collectionAからドキュメントを取得
documents = collectionA.find()

# 各ドキュメントに対して処理を行う
for doc in documents:
    # collectionBに同じIDのドキュメントが存在するか調べる
    existing_doc = collectionB.find_one({'_id': doc['_id']})
    
    if existing_doc is None:
        # collectionBにドキュメントが存在しない場合、新規追加
        collectionB.insert_one(doc)
    else:
        # 更新日時を比較して、collectionAの方が新しい場合は更新
        if doc['update_datetime'] > existing_doc['update_datetime']:
            collectionB.update_one(
                {'_id': doc['_id']},
                {'$set': {
                    'name_key': doc['name_key'],
                    'data_exp': doc['data_exp'],
                    'data_fit': doc['data_fit'],
                    'photo': doc['photo'],
                    'update_datetime': doc['update_datetime']
                }}
            )

# バッチ処理が完了
print("同期処理が完了しました。")

# MongoDBクライアントを閉じる
client.close()
```

このスクリプトは、collectionAとcollectionBが同じデータベースに存在すると仮定しています。異なるデータベースやサーバー間で操作を行う場合は、接続設定を適宜変更する必要があります。また、エラーハンドリングやロギング機能を追加することで、本番環境での堅牢性をさらに向上させることができます。