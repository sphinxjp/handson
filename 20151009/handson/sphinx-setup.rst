準備 - インストールとエディタ
==============================


Sphinxのインストール
----------------------

Sphinxをインストールする手順について説明します。

Sphinxのインストール方法は利用しているOSによって異なります。
http://sphinx-users.jp/gettingstarted/index.html でOS別のさまざまなインストール方法について紹介しています。

ここではWindows、Mac OS Xでの最も一般的なSphinxのインストール方法を紹介します。


Pythonのインストール
~~~~~~~~~~~~~~~~~~~~~

Sphinxを動作させるためにはPythonをインストールする必要があります。

ターミナル（コマンドプロンプト）で ``python`` を実行して、コマンドが見つからない場合は、 https://www.python.org/downloads/ から **Python-2.7.10** をダウンロードしてインストールして下さい。

インストール後にターミナルで以下のように実行出来ればOKです::

    > python -V
    Python 2.7.10


pipのインストール
~~~~~~~~~~~~~~~~~~

Sphinxをインストールするにはpipというインストールツールが必要です。
Python-2.7.10 をインストールすれば、pipは自動的にインストールされます。

ターミナルで ``pip`` を実行して、コマンドが見つからない場合は、以下の手順でインストールしてください。

1. https://bootstrap.pypa.io/get-pip.py をファイルに保存
2. ``python get-pip.py`` をターミナルで実行


インストール後にターミナルで以下のように実行出来ればOKです::

    > pip -V
    pip 7.1.2 from .... (python 2.7)

Sphinxのインストール
~~~~~~~~~~~~~~~~~~~~~

ターミナルで以下の手順でインストールしてください。

::

   > pip install sphinx pillow


インストール後にターミナルで以下のように実行出来ればOKです::

    > sphinx-build --version
    Sphinx (sphinx-build) 1.3.1


テキストエディタ
-----------------

Sphinxのドキュメントはテキストエディタで作成します。

* 文字コードをUTF-8で保存できるテキストエディタを使用してください
* Windowsであればサクラエディタや秀丸
* MacであればCotEdit
* 他にも、Emacs、Vim、Eclipse、PyCharmなども使えます

