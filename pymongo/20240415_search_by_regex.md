MongoDBでSMILES形式の分子情報を保持し、特定の部分構造に基づいてフィルタリングを行うには、正規表現を使用するアプローチが便利です。MongoDBのクエリ機能には、文字列パターンマッチングを行うための強力な正規表現のサポートが含まれています。

例えば、分子構造中に特定のパターン（この場合は「CC」のパターン）を含むSMILES文字列を検索したい場合、以下のようなMongoDBのクエリを使用できます：

```python
from pymongo import MongoClient

# MongoDBサーバーに接続
client = MongoClient('mongodb://localhost:27017/')

# 使用するデータベースとコレクションを選択
db = client['your_database_name']
collection = db['your_collection_name']

# 検索クエリ
query = {"smiles": {"$regex": "CC"}}

# クエリ実行
results = collection.find(query)

# 結果表示
for result in results:
    print(result)
```

このクエリは、`smiles` フィールドが「CC」を含むすべてのドキュメントを検索します。正規表現を使用することで、部分一致を簡単に検出できます。

もし特定のより複雑な構造や条件でフィルタリングしたい場合、正規表現を調整することで対応できます。例えば、特定の位置にある原子や結合のパターンによってフィルタリングすることもできます。そのための正規表現は、具体的な分子構造のパターンに基づいてさらに複雑になる可能性があります。