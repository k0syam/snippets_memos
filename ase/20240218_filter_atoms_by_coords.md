指定された`atoms`（ASEの`Atoms`インスタンス）と`coords`（座標リスト）を引数とする関数を作成します。この関数は、`coords`に一致する原子のみを含む新しい`Atoms`インスタンスを返します。以下のコードは、その機能を実装したものです：

```python
from ase import Atoms
import numpy as np

def filter_atoms_by_coords(atoms, coords):
    """
    指定された座標に一致する原子のみを含む新しいAtomsインスタンスを返す関数。
    
    Parameters:
    - atoms: Atomsインスタンス。フィルタリング対象の原子を含む。
    - coords: list of list of float。一致を確認する3次元座標のリスト。
    
    Returns:
    - Atomsインスタンス。指定された座標に一致する原子のみを含む。
    """
    # 一致する原子のインデックスを保持するリストを初期化
    matching_indices = []

    # atomsインスタンスの全原子に対してループ
    for i, atom in enumerate(atoms):
        # 現在の原子の座標を取得
        atom_pos = atom.position
        
        # coords内の各座標と比較
        for coord in coords:
            # NumPyの配列に変換して比較（浮動小数点の比較のためにnp.allcloseを使用）
            if np.allclose(atom_pos, np.array(coord), atol=1e-5):
                # 一致する場合、インデックスを保存
                matching_indices.append(i)
                break  # 一致が見つかったら内側のループを抜ける

    # 一致する原子のみを含む新しいAtomsインスタンスを作成
    filtered_atoms = atoms[matching_indices]
    
    return filtered_atoms
```

この関数は、前に説明したベストプラクティスに従っています。具体的には、関数を通じてコードの再利用性を高め、機能のモジュール化を実現しています。また、関数のパラメータとして`atoms`と`coords`を受け取ることで、さまざまな状況やデータセットに対応できるようにしています。

使用例：

```python
# atoms: あなたのAtomsインスタンス
# coords: 一致を確認する座標のリスト
# filtered_atoms = filter_atoms_by_coords(atoms, coords)
# このfiltered_atomsには、指定された座標に一致する原子のみが含まれます
```

この関数を使用することで、特定の座標に一致する原子のみを含む`Atoms`インスタンスを簡単に取得できます。必要に応じて、`np.allclose`関数の`atol`パラメータ（許容誤差）を調整することで、座標の比較精度を変更することができます。