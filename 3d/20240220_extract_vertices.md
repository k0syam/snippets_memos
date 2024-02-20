以下に、関数全体を一度にコピーペースト可能な形で提供します。この関数は、線分のリストからユニークな頂点を抽出するために使用できます。

```python
def extract_unique_vertices(segments):
    """
    関数は線分のリストからユニークな頂点を抽出します。
    
    :param segments: 線分のリスト。各線分は2つの頂点（[x, y, z]形式）のリストです。
    :return: ユニークな頂点のリストを返します。
    """
    # ユニークな頂点を保持するためのセットを初期化
    unique_vertices = set()
    
    # 各線分に対してループ
    for segment in segments:
        # 線分の両頂点をセットに追加（重複排除）
        unique_vertices.update([tuple(segment[0]), tuple(segment[1])])
    
    # セットをリストに変換し、各頂点をリスト形式に戻す
    return [list(vertex) for vertex in unique_vertices]

# テストデータ
segments = [
    [[0,0,0],[1,1,1]],
    [[0,0,0],[2,2,2]],
    [[1,1,1],[2,2,2]]
]

# 関数を呼び出してユニークな頂点を抽出
unique_vertices = extract_unique_vertices(segments)
print(unique_vertices)
```

このコードをそのままコピーして、Python環境に貼り付けて実行することができます。この関数は、入力として線分のリストを受け取り、それらの線分からユニークな頂点のリストを返します。上記のテストデータを使用すると、抽出されたユニークな頂点は `[[0, 0, 0], [1, 1, 1], [2, 2, 2]]` となります。