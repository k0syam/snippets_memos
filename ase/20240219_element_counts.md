ASE (Atomic Simulation Environment) を使用して、`ase.Atoms` インスタンスから元素の種類と数を取得し、それを辞書形式で返す関数を設計します。この関数は、各元素のシンボルをキーとし、その元素の数を値とする辞書を返します。関数の設計には以下のプログラミング原則を考慮します：

- **DRY (Don't Repeat Yourself)**: コードの重複を避け、再利用可能な関数を作成します。
- **モジュール化**: 機能ごとにコードを分割し、読みやすく、保守しやすい構造にします。
- **単一責任の原則**: 各関数は一つのことだけを行うようにします。
- **KISS (Keep It Simple, Stupid)**: コードをシンプルに保ち、複雑さを避けます。

以下の関数は、これらの原則に基づいて設計されています：

```python
from ase import Atoms

def get_element_counts(atoms):
    """
    ASE Atomsインスタンスから元素の種類と数を辞書形式で返す関数。
    
    :param atoms: ASE Atomsインスタンス
    :return: 各元素のシンボルをキーとし、その元素の数を値とする辞書
    """
    element_counts = {}
    for atom in atoms:
        symbol = atom.symbol
        if symbol in element_counts:
            element_counts[symbol] += 1
        else:
            element_counts[symbol] = 1
    return element_counts

# 使用例
# atoms = Atoms('H2O')  # 実際にはASEからAtomsインスタンスを生成する
# print(get_element_counts(atoms))
```

この関数は、`Atoms` インスタンスを引数に取り、そのインスタンス内の各原子のシンボルを走査して、辞書に元素の種類と数を記録します。元素のシンボルが辞書に既に存在する場合はそのカウントを増やし、存在しない場合は新たにキーを追加してカウントを1から始めます。これにより、関数の単一責任とモジュール化の原則に従い、ASEの`Atoms`インスタンスから必要な情報を簡潔に抽出することができます。