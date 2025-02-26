from playwright.sync_api import sync_playwright

def run(playwright):
    # Chromium ブラウザを起動（headless=False でブラウザウィンドウを表示）
    browser = playwright.chromium.launch(headless=False)
    # 新しいブラウザコンテキストを作成
    context = browser.new_context()
    # 新しいページを作成
    page = context.new_page()
    
    # 仮想のログインページに移動
    page.goto("https://example.com/login")
    
    # ユーザー名とパスワードをそれぞれの入力フィールドに入力
    page.fill("input[name='username']", "your_username")
    page.fill("input[name='password']", "your_password")
    
    # ログインボタンをクリック（例：submit ボタン）
    page.click("button[type='submit']")
    
    # ログイン後のページが読み込まれるまで待機（ネットワークがアイドル状態になるまで）
    page.wait_for_load_state("networkidle")
    
    # ログイン完了後の処理（ここでは単純にメッセージを出力）
    print("ログインに成功しました！")
    
    # ブラウザを閉じる
    browser.close()

# sync_playwright のコンテキストマネージャを使って実行
with sync_playwright() as playwright:
    run(playwright)
