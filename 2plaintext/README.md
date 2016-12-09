### 股票公告的文件类型中大部分是pdf，还有一些doc和docx的。这里提供了一些转为文本的方法。

#### docx
* 在python中安装：pip install python-docx，然后调用formatFun.py中的dx2t

#### doc
* 在linux下安装catdoc工具(catdoc只能在linux下用)。然后调用formatFun.py中的d2t

#### pdf
* 在python中安装 pip install pdfminer，然后调用formatFun.py中的p2t

#### formatFun.py中的参数，文件在当前目录下就写文件名即可，如果不是，则用绝对路径指明文件名

### 转换效率不是很高。有兴趣的同学可以试一试Apache的Tika，解析的种类更丰富，但效率没测试过