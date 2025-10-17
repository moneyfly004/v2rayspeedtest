name: free-v2ray-node

on:
  schedule:
    - cron: '0 * * * *'
  push:
    paths-ignore:
      - '**'
  workflow_dispatch:

jobs:
  run_demo_actions:
    runs-on: ubuntu-latest
    permissions:
      contents: write
      pull-requests: write
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          # 使用GitHub内置token，具有完整的仓库权限
          token: ${{ secrets.GITHUB_TOKEN }}
          fetch-depth: 0

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10.10'

      - name: Install requirements.txt
        run: |
          pip install -r ./requirements.txt

      - name: Run main.py
        run: python main.py

      - name: Check permissions and files
        run: |
          echo "=== 检查权限和文件状态 ==="
          echo "当前用户: $(whoami)"
          echo "当前目录: $(pwd)"
          echo "Git配置:"
          git config --list | grep -E "(user\.|remote\.)"
          echo "远程仓库:"
          git remote -v
          echo "生成的文件:"
          ls -la *.txt 2>/dev/null || echo "没有找到txt文件"

      - name: Commit and push file
        run: |
          set -e
          echo "=== 开始提交和推送文件 ==="
          
          # 配置Git用户信息
          git config user.name "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
          
          # 显示当前状态
          echo "当前工作目录: $(pwd)"
          echo "Git状态:"
          git status
          
          # 检查文件是否存在
          echo "检查生成的文件:"
          ls -la v2ray.txt all.txt v2ray_raw.txt 2>/dev/null || echo "某些文件不存在"
          
          # 显示文件内容大小
          echo "文件大小:"
          for file in v2ray.txt all.txt v2ray_raw.txt; do
            if [ -f "$file" ]; then
              echo "$file: $(wc -l < "$file") 行, $(wc -c < "$file") 字节"
            else
              echo "$file: 文件不存在"
            fi
          done
          
          # 检查是否有更改
          if git diff --quiet && git diff --cached --quiet; then
            echo "没有文件更改，跳过提交"
            exit 0
          fi
          
          # 添加文件到暂存区
          echo "添加文件到Git暂存区..."
          git add v2ray.txt all.txt v2ray_raw.txt
          
          # 检查暂存区状态
          echo "暂存区状态:"
          git diff --cached --stat
          
          # 提交更改
          echo "提交更改..."
          git commit -m "update $(date '+%Y-%m-%d %H:%M:%S')"
          
          # 显示提交历史
          echo "最近的提交:"
          git log --oneline -3
          
          # 推送更改到远程仓库
          echo "推送更改到远程仓库..."
          git push origin HEAD:master
          echo "✅ 成功推送到GitHub仓库"
          
          echo "✅ 文件推送完成"
