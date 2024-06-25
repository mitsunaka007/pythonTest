# 必要なライブラリをインポート
import ui
import random

# じゃんけんの処理を行う関数
def janken(sender):
    global result_label  # グローバル変数を関数内部で参照するための宣言

    # じゃんけんの選択肢
    choices = ["グー", "チョキ", "パー"]
    
    # ユーザの選択をボタンのタイトルから取得
    user_choice = sender.title
    
    # コンピュータの選択をランダムに決定
    computer_choice = random.choice(choices)
    
    # 以下で勝敗の判定と結果の表示を行う
    if user_choice == computer_choice:
        result_label.text = f"相手は{computer_choice}です。あいこです!"
    elif (user_choice == "グー" and computer_choice == "チョキ") or \
         (user_choice == "チョキ" and computer_choice == "パー") or \
         (user_choice == "パー" and computer_choice == "グー"):
        result_label.text = f"相手は{computer_choice}です。あなたの勝ちです!"
    else:
        result_label.text = f"相手は{computer_choice}です。あなたの負けです..."

# メインのUIビューの設定
view = ui.View()
view.name = 'じゃんけんゲーム'
view.background_color = 'white'
view.width = 400
view.height = 400

# じゃんけんの3つのボタンを追加
for idx, choice in enumerate(["グー", "チョキ", "パー"]):
    btn = ui.Button(title=choice)
    btn.center = (view.width * 0.5, view.height * 0.3 + idx * 60)  # 位置を中央に、そして縦に並べる
    btn.flex = 'LRTB'  # 画面サイズが変わってもボタンの位置が適切に調整されるようにする設定
    btn.action = janken  # ボタンがタップされた時にjanken関数を実行
    view.add_subview(btn)  # ボタンをビューに追加

# 勝敗結果を表示するためのラベルを作成・追加
result_label = ui.Label()
result_label.frame = (50, 300, 300, 40)  # ラベルの位置とサイズを設定
result_label.text = ''  # 初期テキストは空
result_label.alignment = ui.ALIGN_CENTER  # テキストを中央寄せ
view.add_subview(result_label)  # ラベルをビューに追加

# ビューを表示
view.present('sheet')