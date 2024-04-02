import os
import re
import subprocess

import requests


def update_readme():
    # 获取环境变量
    repo = os.environ.get("REPO_NAME")
    readme_path = os.environ.get("README_PATH")

    # 获取贡献者信息和头像 URL
    response = requests.get(f"https://api.github.com/repos/{repo}/contributors")
    contributors_data = response.json()

    contributors_md = ""
    for contributor in contributors_data:
        if contributor["type"] != "User":
            continue
        login = contributor["login"]
        avatar_url = contributor["avatar_url"]
        html_url = contributor["html_url"]
        contributions = contributor["contributions"]
        contributor_md = (
            f'<div style="display: inline-block; text-align: center; margin: 10px;">'
            f'<a href="{html_url}" target="_blank"><img src="{avatar_url}" width="100px" height="100px" style="border-radius: 50%;" alt="{login}"></a>'
            f"<br>{login}<br>Contributions: {contributions}</div>"
        )
        contributors_md += contributor_md

    # 更新 README 文件
    with open(readme_path, "r") as f:
        readme_content = f.read()

    # 定义要进行匹配和替换的正则表达式模式，使用括号分组
    pattern = re.compile(
        r"<!-- CONTRIBUTORS_SECTION -->.*<!-- /CONTRIBUTORS_SECTION -->", re.DOTALL
    )

    # 定义要替换的字符串
    replacement = (
        f"<!-- CONTRIBUTORS_SECTION -->"
        f'<div align="center">\n{contributors_md}\n</div>'
        f"<!-- /CONTRIBUTORS_SECTION -->"
    )

    # 使用正则表达式进行匹配和替换
    new_readme_content = pattern.sub(replacement, readme_content)

    # 提交更改
    if new_readme_content != readme_content:
        with open(readme_path, "w") as f:
            f.write(new_readme_content)

        commit_message = f"CI: Update README (contributors: {len(contributors_data)})"
        subprocess.run(["git", "add", readme_path])
        subprocess.run(["git", "commit", "-m", commit_message])
        subprocess.run(["git", "push"])
    else:
        print("no change")


# 在需要的时候调用函数来更新 README
update_readme()
