feature_demo.ipynb 是以 music21这个python库为基础写的提取特征的代码，可以利用music21 的接口来读取 .midi 和 .xml(.musicxml) 文件，不过由于其为前期实验所用， bug 较多，后期没有维护和更新。



zehao_dataprepare.py/.ipynb 为提取事件形式的数据集里的特征所使用的代码，bug 较少，缺点是基于自己写的类实现的特征提取，目前只实现了事件形式的单旋律曲谱的读取，暂不支持midi和xml文件。