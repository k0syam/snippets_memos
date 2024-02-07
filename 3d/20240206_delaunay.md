`Delaunay(points)`を計算した後に、Blender以外で可視化する方法はいくつかあります。主に科学計算やデータ可視化に使用されるPythonライブラリを利用することができます。ここでは、MatplotlibとPlotlyを使用した可視化の方法を紹介します。

### Matplotlibを使用する方法

MatplotlibはPythonで最も一般的に使用される2Dプロットライブラリですが、3Dプロットもサポートしています。3Dのドロネー複体をMatplotlibで可視化するには、以下のようなコードを使用できます。

```python
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy.spatial import Delaunay
import numpy as np

# 3次元の点群を定義
points = np.array([[x0, y0, z0], [x1, y1, z1], [x2, y2, z2], ...])

# ドロネー複体を計算
delaunay = Delaunay(points)

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# ドロネー複体の各シンプレックス（テトラヘドロン）をプロット
for simplex in delaunay.simplices:
    for s in simplex:
        s = np.append(s, simplex[0])  # 最初の点に戻るように
        ax.plot3D(points[s, 0], points[s, 1], points[s, 2], 'k-')

# 点群をプロット
ax.plot3D(points[:,0], points[:,1], points[:,2], 'o')

plt.show()
```

このコードは、3D空間内の点群から計算されたドロネー複体を表示します。ただし、この方法では、テトラヘドロンのエッジのみが表示され、内部は塗りつぶされません。

### Plotlyを使用する方法

Plotlyは、インタラクティブなグラフを作成するための別の強力なライブラリです。3Dの可視化にも対応しており、インタラクティブな操作が可能です。

```python
import plotly.graph_objects as go
from scipy.spatial import Delaunay
import numpy as np

# 3次元の点群を定義
points = np.array([[x0, y0, z0], [x1, y1, z1], [x2, y2, z2], ...])

# ドロネー複体を計算
delaunay = Delaunay(points)

# 3Dプロットを作成
fig = go.Figure()

# ドロネー複体の各シンプレックスをプロット
for simplex in delaunay.simplices:
    x, y, z = points[simplex].T
    fig.add_trace(go.Mesh3d(x=x, y=y, z=z, color='lightblue', opacity=0.5))

# 点群をプロット
fig.add_trace(go.Scatter3d(x=points[:,0], y=points[:,1], z=points[:,2],
                           mode='markers', marker=dict(size=2, color='red')))

fig.show()
```

Plotlyを使用すると、テトラヘドロンの面が表示され、ユーザーがプロットをズーム、回転、パンすることができるインタラクティブな可視化を得ることができます。

### 注意点

- Matplotlibは静的な3Dプロットを提供し、基本的な視覚化に適していますが、インタラクティブな機能は限られています。
- Plotlyは高度なインタラクティブな可視化を提供しますが、ウェブベースのプロジェクトやインタラクティブなダッシュボードに

最適です。
- どちらのライブラリも、大量のデータを扱う場合にはパフォーマンスの問題が生じる可能性があります。大規模なデータセットでの使用には注意が必要です。

これらのライブラリを使用することで、Blender以外で3Dのドロネー複体を効果的に可視化することができます。